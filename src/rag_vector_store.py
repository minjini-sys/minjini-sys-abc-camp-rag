"""KLUE-BERT embedding and ChromaDB vector store utilities for YES24 books."""

from __future__ import annotations

import hashlib
import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import chromadb
import numpy as np
import pandas as pd
import torch
from chromadb.config import Settings
from transformers import AutoModel, AutoTokenizer


MODEL_NAME = "klue/bert-base"
COLLECTION_NAME = "yes24_books_klue_bert"
NUMERIC_COLUMNS = ["순위", "판매가(원)", "정가(원)", "할인율(%)", "평점", "리뷰수", "판매지수"]
TEXT_COLUMNS = ["도서명", "저자", "출판사", "출간일", "상세페이지링크", "내용"]


@dataclass(frozen=True)
class VectorSearchResult:
    id: str
    document: str
    metadata: dict[str, Any]
    distance: float

    @property
    def similarity(self) -> float:
        return max(0.0, 1.0 - self.distance)


def clean_html_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = html.unescape(str(value))
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def to_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False).str.strip(), errors="coerce")


def load_yes24_csv(csv_path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    for col in TEXT_COLUMNS:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str)
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = to_number(df[col])
    df["내용_정제"] = df["내용"].map(clean_html_text)
    df["검색문서"] = (
        df["도서명"].fillna("")
        + " "
        + df["저자"].fillna("")
        + " "
        + df["출판사"].fillna("")
        + " "
        + df["내용_정제"].fillna("")
    ).str.lower()
    return df


def csv_fingerprint(csv_path: str | Path) -> str:
    path = Path(csv_path)
    stat = path.stat()
    raw = f"{path.resolve()}::{stat.st_size}::{int(stat.st_mtime)}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _as_metadata_value(value: Any) -> str | int | float | bool:
    if pd.isna(value):
        return ""
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (int, float, bool)):
        return value
    return str(value)


def book_document(row: pd.Series) -> str:
    intro = str(row.get("내용_정제", "")).replace("\n", " ")
    return "\n".join(
        [
            f"도서명: {row.get('도서명', '')}",
            f"저자: {row.get('저자', '')}",
            f"출판사: {row.get('출판사', '')}",
            f"출간일: {row.get('출간일', '')}",
            f"평점: {row.get('평점', '')}",
            f"리뷰수: {row.get('리뷰수', '')}",
            f"판매지수: {row.get('판매지수', '')}",
            f"책 소개: {intro}",
        ]
    )


def book_metadata(row: pd.Series, row_index: int, fingerprint: str) -> dict[str, str | int | float | bool]:
    fields = [
        "순위",
        "도서ID",
        "도서명",
        "저자",
        "출판사",
        "출간일",
        "판매가(원)",
        "정가(원)",
        "할인율(%)",
        "평점",
        "리뷰수",
        "판매지수",
        "상세페이지링크",
    ]
    metadata = {field: _as_metadata_value(row.get(field, "")) for field in fields}
    metadata["row_index"] = row_index
    metadata["csv_fingerprint"] = fingerprint
    return metadata


class KlueBertEmbedder:
    """Small mean-pooling encoder around klue/bert-base."""

    def __init__(self, model_name: str = MODEL_NAME, max_length: int = 256, cache_dir: str | Path | None = None) -> None:
        self.model_name = model_name
        self.max_length = max_length
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=str(self.cache_dir) if self.cache_dir else None)
        self.model = AutoModel.from_pretrained(model_name, cache_dir=str(self.cache_dir) if self.cache_dir else None).to(self.device)
        self.model.eval()

    def encode(self, texts: list[str], batch_size: int = 16) -> list[list[float]]:
        embeddings: list[np.ndarray] = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            encoded = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="pt",
            )
            encoded = {key: value.to(self.device) for key, value in encoded.items()}
            with torch.no_grad():
                output = self.model(**encoded)
                token_embeddings = output.last_hidden_state
                mask = encoded["attention_mask"].unsqueeze(-1).expand(token_embeddings.size()).float()
                summed = torch.sum(token_embeddings * mask, dim=1)
                counts = torch.clamp(mask.sum(dim=1), min=1e-9)
                pooled = summed / counts
                pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
            embeddings.extend(pooled.cpu().numpy())
        return [embedding.astype(float).tolist() for embedding in embeddings]


class Yes24VectorStore:
    def __init__(
        self,
        persist_dir: str | Path,
        model_name: str = MODEL_NAME,
        collection_name: str = COLLECTION_NAME,
        model_cache_dir: str | Path | None = None,
    ) -> None:
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name
        self.collection_name = collection_name
        self.model_cache_dir = Path(model_cache_dir) if model_cache_dir else self.persist_dir.parent / "hf_models"
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine", "model": model_name},
        )
        self._embedder: KlueBertEmbedder | None = None

    @property
    def embedder(self) -> KlueBertEmbedder:
        if self._embedder is None:
            self._embedder = KlueBertEmbedder(self.model_name, cache_dir=self.model_cache_dir)
        return self._embedder

    def count(self) -> int:
        return int(self.collection.count())

    def reset(self) -> None:
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine", "model": self.model_name},
        )

    def build_from_csv(
        self,
        csv_path: str | Path,
        batch_size: int = 16,
        force_rebuild: bool = False,
        progress_callback: Any | None = None,
    ) -> int:
        df = load_yes24_csv(csv_path)
        fingerprint = csv_fingerprint(csv_path)

        if force_rebuild:
            self.reset()
        elif self.count() > 0:
            probe = self.collection.get(limit=1, include=["metadatas"])
            metadatas = probe.get("metadatas") or []
            if metadatas and metadatas[0].get("csv_fingerprint") == fingerprint:
                return self.count()
            self.reset()

        documents = [book_document(row) for _, row in df.iterrows()]
        ids = [f"book-{int(idx)}" for idx in df.index]
        metadatas = [book_metadata(row, int(idx), fingerprint) for idx, row in df.iterrows()]

        total = len(documents)
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            batch_docs = documents[start:end]
            embeddings = self.embedder.encode(batch_docs, batch_size=batch_size)
            self.collection.add(
                ids=ids[start:end],
                documents=batch_docs,
                metadatas=metadatas[start:end],
                embeddings=embeddings,
            )
            if progress_callback:
                progress_callback(end, total)
        return self.count()

    def search(self, query: str, n_results: int = 8) -> list[VectorSearchResult]:
        if self.count() == 0:
            return []
        query_embedding = self.embedder.encode([query], batch_size=1)[0]
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        return [
            VectorSearchResult(
                id=str(item_id),
                document=str(document),
                metadata=dict(metadata),
                distance=float(distance),
            )
            for item_id, document, metadata, distance in zip(ids, documents, metadatas, distances)
        ]
