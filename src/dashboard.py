"""YES24 book data EDA, search, and KLUE-BERT/ChromaDB RAG chatbot dashboard.

Run:
    streamlit run src/dashboard.py
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from rag_vector_store import MODEL_NAME, Yes24VectorStore, VectorSearchResult, load_yes24_csv


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "data" / "chroma_yes24"
DEFAULT_DATA_FILE = DATA_DIR / "yes24_it_mobile_bestsellers.csv"
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


st.set_page_config(
    page_title="YES24 도서 EDA 대시보드",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    return load_yes24_csv(path)


@st.cache_resource(show_spinner=False)
def get_vector_store() -> Yes24VectorStore:
    return Yes24VectorStore(CHROMA_DIR, model_name=MODEL_NAME)


def get_data_files() -> list[Path]:
    if not DATA_DIR.exists():
        return []
    return sorted(DATA_DIR.glob("*.csv"))


def format_won(value: float | int | None) -> str:
    if pd.isna(value):
        return "-"
    return f"{int(value):,}원"


def format_number(value: float | int | None) -> str:
    if pd.isna(value):
        return "-"
    return f"{int(value):,}"


def apply_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("필터")

    publishers = sorted(df["출판사"].dropna().astype(str).unique())
    selected_publishers = st.sidebar.multiselect("출판사", publishers)

    min_rating = float(df["평점"].min()) if df["평점"].notna().any() else 0.0
    max_rating = float(df["평점"].max()) if df["평점"].notna().any() else 10.0
    rating_range = st.sidebar.slider(
        "평점 범위",
        min_value=0.0,
        max_value=10.0,
        value=(max(0.0, min_rating), min(10.0, max_rating)),
        step=0.1,
    )

    max_price = int(df["판매가(원)"].max()) if df["판매가(원)"].notna().any() else 100000
    price_range = st.sidebar.slider(
        "판매가 범위",
        min_value=0,
        max_value=max(1000, max_price),
        value=(0, max(1000, max_price)),
        step=1000,
        format="%d원",
    )

    filtered = df.copy()
    if selected_publishers:
        filtered = filtered[filtered["출판사"].isin(selected_publishers)]
    filtered = filtered[filtered["평점"].between(rating_range[0], rating_range[1], inclusive="both")]
    filtered = filtered[filtered["판매가(원)"].between(price_range[0], price_range[1], inclusive="both")]
    return filtered


def render_metrics(df: pd.DataFrame) -> None:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("도서 수", f"{len(df):,}권")
    col2.metric("출판사 수", f"{df['출판사'].nunique():,}곳")
    col3.metric("평균 평점", f"{df['평점'].mean():.2f}")
    col4.metric("평균 판매가", format_won(df["판매가(원)"].mean()))
    col5.metric("평균 판매지수", format_number(df["판매지수"].mean()))


def render_eda(df: pd.DataFrame) -> None:
    st.subheader("탐색적 데이터 분석")
    render_metrics(df)

    st.divider()
    left, right = st.columns(2)

    with left:
        publisher_counts = df["출판사"].value_counts().head(15).reset_index()
        publisher_counts.columns = ["출판사", "도서 수"]
        fig = px.bar(
            publisher_counts.sort_values("도서 수"),
            x="도서 수",
            y="출판사",
            orientation="h",
            title="출판사별 도서 수 Top 15",
            text="도서 수",
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        publisher_sales = (
            df.groupby("출판사", as_index=False)
            .agg(평균판매지수=("판매지수", "mean"), 도서수=("도서명", "count"))
            .query("도서수 >= 2")
            .sort_values("평균판매지수", ascending=False)
            .head(15)
        )
        fig = px.bar(
            publisher_sales,
            x="출판사",
            y="평균판매지수",
            color="도서수",
            title="출판사별 평균 판매지수 Top 15",
        )
        fig.update_xaxes(tickangle=35)
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        fig = px.histogram(df, x="평점", nbins=20, title="평점 분포")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.histogram(df, x="판매가(원)", nbins=30, title="판매가 분포")
        fig.update_layout(xaxis_tickformat=",")
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        fig = px.scatter(
            df,
            x="리뷰수",
            y="판매지수",
            color="평점",
            hover_name="도서명",
            hover_data=["저자", "출판사", "판매가(원)"],
            title="리뷰수와 판매지수 관계",
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        top_books = df.sort_values("판매지수", ascending=False).head(15)
        fig = px.bar(
            top_books.sort_values("판매지수"),
            x="판매지수",
            y="도서명",
            orientation="h",
            title="판매지수 Top 15 도서",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("원본 데이터 미리보기")
    display_cols = ["순위", "도서명", "저자", "출판사", "출간일", "판매가(원)", "평점", "리뷰수", "판매지수"]
    st.dataframe(df[display_cols], use_container_width=True, hide_index=True)


def search_books(df: pd.DataFrame, query: str, match_mode: str) -> pd.DataFrame:
    keywords = [token.lower() for token in query.split() if token.strip()]
    if not keywords:
        return df.copy()

    masks = [df["검색문서"].str.contains(keyword, case=False, regex=False, na=False) for keyword in keywords]
    if match_mode == "모든 키워드 포함":
        mask = masks[0]
        for item in masks[1:]:
            mask = mask & item
    else:
        mask = masks[0]
        for item in masks[1:]:
            mask = mask | item
    return df[mask].copy()


def render_book_detail(book: pd.Series) -> None:
    st.markdown(f"### {book['도서명']}")
    meta_left, meta_right = st.columns([1, 2])

    with meta_left:
        st.write(f"**순위:** {format_number(book.get('순위'))}")
        st.write(f"**저자:** {book.get('저자', '-')}")
        st.write(f"**출판사:** {book.get('출판사', '-')}")
        st.write(f"**출간일:** {book.get('출간일', '-')}")
        st.write(f"**판매가:** {format_won(book.get('판매가(원)'))}")
        st.write(f"**정가:** {format_won(book.get('정가(원)'))}")
        st.write(f"**할인율:** {book.get('할인율(%)', 0):.1f}%")
        st.write(f"**평점/리뷰:** {book.get('평점', 0):.1f} / 리뷰 {format_number(book.get('리뷰수'))}개")
        st.write(f"**판매지수:** {format_number(book.get('판매지수'))}")
        if book.get("상세페이지링크"):
            st.link_button("YES24 상세페이지 열기", str(book["상세페이지링크"]))

    with meta_right:
        st.markdown("**책 소개**")
        content = str(book.get("내용_정제", "")).strip()
        if content:
            st.text_area("내용", content, height=360, label_visibility="collapsed")
        else:
            st.info("수집된 책 소개 내용이 없습니다.")


def render_search(df: pd.DataFrame) -> None:
    st.subheader("도서 제목과 내용 검색")
    query_col, mode_col, sort_col = st.columns([2.4, 1, 1])

    with query_col:
        query = st.text_input("검색어", placeholder="예: 클로드 AI 코딩")
    with mode_col:
        match_mode = st.selectbox("검색 조건", ["모든 키워드 포함", "하나 이상 포함"])
    with sort_col:
        sort_by = st.selectbox("정렬", ["순위 낮은 순", "판매지수 높은 순", "평점 높은 순", "리뷰수 많은 순", "판매가 낮은 순"])

    result = search_books(df, query, match_mode)
    sort_map = {
        "순위 낮은 순": ("순위", True),
        "판매지수 높은 순": ("판매지수", False),
        "평점 높은 순": ("평점", False),
        "리뷰수 많은 순": ("리뷰수", False),
        "판매가 낮은 순": ("판매가(원)", True),
    }
    sort_col_name, ascending = sort_map[sort_by]
    result = result.sort_values(sort_col_name, ascending=ascending)

    st.caption(f"검색 결과 {len(result):,}권")
    display_cols = ["순위", "도서명", "저자", "출판사", "출간일", "판매가(원)", "평점", "리뷰수", "판매지수"]
    st.dataframe(result[display_cols], use_container_width=True, hide_index=True, height=360)

    if result.empty:
        st.info("검색 조건에 맞는 도서가 없습니다.")
        return

    selected_title = st.selectbox("상세히 볼 도서", result["도서명"].tolist())
    selected_book = result[result["도서명"] == selected_title].iloc[0]
    render_book_detail(selected_book)


def filter_results_for_current_df(results: list[VectorSearchResult], df: pd.DataFrame) -> list[VectorSearchResult]:
    allowed_titles = set(df["도서명"].astype(str))
    return [result for result in results if str(result.metadata.get("도서명", "")) in allowed_titles]


def build_book_context(results: list[VectorSearchResult]) -> str:
    rows: list[str] = []
    for idx, result in enumerate(results, 1):
        metadata = result.metadata
        document = result.document.replace("\n", " ")
        if len(document) > 900:
            document = document[:900] + "..."
        rows.append(
            "\n".join(
                [
                    f"[{idx}] 제목: {metadata.get('도서명', '')}",
                    f"저자: {metadata.get('저자', '')}",
                    f"출판사: {metadata.get('출판사', '')}",
                    f"출간일: {metadata.get('출간일', '')}",
                    f"평점: {metadata.get('평점', '')}",
                    f"리뷰수: {metadata.get('리뷰수', '')}",
                    f"판매지수: {metadata.get('판매지수', '')}",
                    f"벡터 유사도: {result.similarity:.3f}",
                    f"링크: {metadata.get('상세페이지링크', '')}",
                    f"내용: {document}",
                ]
            )
        )
    return "\n\n".join(rows)


def call_groq_chat(api_key: str, model: str, user_query: str, results: list[VectorSearchResult]) -> str:
    context = build_book_context(results)
    system_prompt = """
당신은 YES24 도서 추천 RAG 챗봇입니다.
반드시 제공된 ChromaDB 벡터 검색 결과 안에서만 추천하세요.
사용자 요구와 맞는 도서가 검색 결과에 없다면 "추천할 도서가 없습니다."라고 답하세요.
추천할 때는 1~3권만 고르고, 각 도서의 추천 이유를 짧게 설명하세요.
상세 링크가 제공된 책은 Markdown 링크 형식으로 제목을 연결하세요.
검색 결과 밖의 책, 저자, 링크를 만들지 마세요.
""".strip()
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"사용자 요청:\n{user_query}\n\nChromaDB 벡터 검색 결과:\n{context}",
            },
        ],
        "temperature": 0.2,
        "max_completion_tokens": 900,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    response = requests.post(GROQ_CHAT_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def render_vector_results(results: list[VectorSearchResult]) -> None:
    with st.expander("ChromaDB 검색 결과와 링크 보기", expanded=True):
        rows = []
        for result in results:
            metadata = result.metadata
            rows.append(
                {
                    "유사도": round(result.similarity, 3),
                    "도서명": metadata.get("도서명", ""),
                    "저자": metadata.get("저자", ""),
                    "출판사": metadata.get("출판사", ""),
                    "평점": metadata.get("평점", ""),
                    "판매지수": metadata.get("판매지수", ""),
                    "상세페이지링크": metadata.get("상세페이지링크", ""),
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        for result in results:
            title = str(result.metadata.get("도서명", "")).strip()
            link = str(result.metadata.get("상세페이지링크", "")).strip()
            if link:
                st.link_button(f"{title} 열기", link)


def parse_korean_amount(raw_number: str, unit: str) -> int:
    number = float(raw_number.replace(",", ""))
    normalized_unit = unit.replace(" ", "")
    if normalized_unit in {"만원", "만"}:
        number *= 10000
    elif normalized_unit == "천원":
        number *= 1000
    return int(number)


def extract_limit(query: str, default: int = 10) -> int:
    patterns = [
        r"(?:상위|top|TOP|탑)\s*(\d{1,2})",
        r"(\d{1,2})\s*권",
        r"(\d{1,2})\s*개",
    ]
    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            return max(1, min(int(match.group(1)), 30))
    return default


def parse_range_from_query(query: str, metric: str) -> tuple[int | None, int | None]:
    text = query.replace(",", "")
    min_value: int | None = None
    max_value: int | None = None

    if metric == "price":
        amount_pattern = r"(\d+(?:\.\d+)?)\s*(만\s*원|만원|천원|원)"
        range_pattern = amount_pattern + r"\s*(?:~|-|부터|에서)\s*" + amount_pattern
        range_match = re.search(range_pattern, text)
        if range_match:
            first = parse_korean_amount(range_match.group(1), range_match.group(2))
            second = parse_korean_amount(range_match.group(3), range_match.group(4))
            return min(first, second), max(first, second)

        for match in re.finditer(amount_pattern, text):
            value = parse_korean_amount(match.group(1), match.group(2))
            tail = text[match.end() : match.end() + 8]
            if any(token in tail for token in ["이하", "미만", "보다 낮", "보다 싸", "아래"]):
                max_value = value - 1 if "미만" in tail else value
            elif any(token in tail for token in ["이상", "초과", "보다 높", "보다 비", "넘"]):
                min_value = value + 1 if "초과" in tail else value
            elif min_value is None and max_value is None:
                max_value = value
        return min_value, max_value

    amount_pattern = r"(\d+(?:\.\d+)?)\s*(만|천)?"
    range_pattern = amount_pattern + r"\s*(?:~|-|부터|에서)\s*" + amount_pattern
    range_match = re.search(range_pattern, text)
    if range_match:
        window_start = max(0, range_match.start() - 8)
        window_end = min(len(text), range_match.end() + 8)
        window = text[window_start:window_end]
    else:
        window = ""
    if range_match and ("판매지수" in window or "지수" in window):
        first = parse_korean_amount(range_match.group(1), range_match.group(2) or "")
        second = parse_korean_amount(range_match.group(3), range_match.group(4) or "")
        return min(first, second), max(first, second)

    for match in re.finditer(amount_pattern, text):
        unit = match.group(2) or ""
        value = parse_korean_amount(match.group(1), unit)
        if value < 100 and not unit:
            continue
        window_start = max(0, match.start() - 8)
        window_end = min(len(text), match.end() + 8)
        window = text[window_start:window_end]
        if "판매지수" not in window and "지수" not in window:
            continue
        if any(token in window for token in ["이하", "미만", "보다 낮", "아래"]):
            max_value = value - 1 if "미만" in window else value
        elif any(token in window for token in ["이상", "초과", "보다 높", "넘"]):
            min_value = value + 1 if "초과" in window else value
    return min_value, max_value


def analyze_numeric_book_query(df: pd.DataFrame, query: str) -> dict[str, Any] | None:
    text = query.lower()
    asks_price = any(token in text for token in ["가격", "판매가", "정가", "원", "만원", "저렴", "싼", "비싼"])
    asks_sales = any(token in text for token in ["판매지수", "판매 지수", "지수", "잘 팔", "인기"])
    if not asks_price and not asks_sales:
        return None

    result = df.copy()
    filters: list[str] = []
    sort_col = "판매지수" if asks_sales and not asks_price else "판매가(원)"
    ascending = True if sort_col == "판매가(원)" else False

    if asks_price:
        price_min, price_max = parse_range_from_query(query, "price")
        if price_min is not None:
            result = result[result["판매가(원)"] >= price_min]
            filters.append(f"판매가 {price_min:,}원 이상")
        if price_max is not None:
            result = result[result["판매가(원)"] <= price_max]
            filters.append(f"판매가 {price_max:,}원 이하")
        if any(token in text for token in ["비싼", "높은", "내림차순"]):
            sort_col = "판매가(원)"
            ascending = False
        elif any(token in text for token in ["저렴", "싼", "낮은", "오름차순"]):
            sort_col = "판매가(원)"
            ascending = True

    if asks_sales:
        sales_min, sales_max = parse_range_from_query(query, "sales")
        if sales_min is not None:
            result = result[result["판매지수"] >= sales_min]
            filters.append(f"판매지수 {sales_min:,} 이상")
        if sales_max is not None:
            result = result[result["판매지수"] <= sales_max]
            filters.append(f"판매지수 {sales_max:,} 이하")
        if any(token in text for token in ["낮은", "오름차순", "적은"]):
            sort_col = "판매지수"
            ascending = True
        elif any(token in text for token in ["높은", "많은", "상위", "인기", "내림차순", "잘 팔"]):
            sort_col = "판매지수"
            ascending = False

    limit = extract_limit(query)
    result = result.sort_values(sort_col, ascending=ascending).head(limit)
    display_cols = ["순위", "도서명", "저자", "출판사", "출간일", "판매가(원)", "평점", "리뷰수", "판매지수", "상세페이지링크"]
    result = result[display_cols]

    direction = "오름차순" if ascending else "내림차순"
    return {
        "metric": sort_col,
        "ascending": ascending,
        "direction": direction,
        "filters": filters,
        "limit": limit,
        "result": result,
    }


def build_numeric_answer(analysis: dict[str, Any]) -> str:
    result: pd.DataFrame = analysis["result"]
    if result.empty:
        return "해당 수치 범위에 맞는 도서가 없습니다."

    filters = ", ".join(analysis["filters"]) if analysis["filters"] else "별도 범위 조건 없음"
    lines = [
        f"조건: {filters}",
        f"정렬: {analysis['metric']} {analysis['direction']}",
        f"결과: {len(result):,}권",
        "",
    ]
    for idx, (_, book) in enumerate(result.head(5).iterrows(), 1):
        title = str(book["도서명"])
        link = str(book.get("상세페이지링크", "")).strip()
        title_text = f"[{title}]({link})" if link else title
        lines.append(
            f"{idx}. {title_text} - 판매가 {format_won(book['판매가(원)'])}, "
            f"판매지수 {format_number(book['판매지수'])}, 평점 {book['평점']:.1f}"
        )
    return "\n".join(lines)


def render_numeric_results(analysis: dict[str, Any]) -> None:
    result: pd.DataFrame = analysis["result"]
    st.markdown("#### 함수 호출 결과")
    st.caption("CSV의 가격/판매지수 컬럼을 직접 계산해 필터링하고 정렬했습니다.")
    if result.empty:
        st.info("해당 수치 범위에 맞는 도서가 없습니다.")
        return

    st.dataframe(result, use_container_width=True, hide_index=True)
    with st.expander("상세 링크 열기"):
        for _, book in result.iterrows():
            link = str(book.get("상세페이지링크", "")).strip()
            if link:
                st.link_button(str(book["도서명"]), link)


def render_chatbot(df: pd.DataFrame, selected_file: Path) -> None:
    st.subheader("KLUE-BERT + ChromaDB RAG 도서 추천 챗봇")
    st.caption("YES24 CSV를 KLUE-BERT로 임베딩하고 ChromaDB에 저장한 뒤, 벡터 검색 결과만 Groq 답변에 사용합니다.")

    store = get_vector_store()
    index_col, settings_col = st.columns([1.1, 1])

    with index_col:
        st.markdown("#### 벡터 데이터베이스")
        st.write(f"임베딩 모델: `{MODEL_NAME}`")
        st.write(f"ChromaDB 경로: `{CHROMA_DIR}`")
        st.metric("저장된 벡터 수", f"{store.count():,}개")
        force_rebuild = st.checkbox("기존 벡터 DB를 삭제하고 다시 구축")
        if st.button("벡터 DB 구축/갱신", type="primary"):
            progress = st.progress(0)
            status = st.empty()

            def update_progress(done: int, total: int) -> None:
                progress.progress(done / total)
                status.info(f"임베딩 및 저장 중... {done:,}/{total:,}")

            with st.spinner("KLUE-BERT 모델 로딩 및 ChromaDB 인덱싱 중입니다. 최초 실행은 시간이 걸릴 수 있습니다."):
                try:
                    count = store.build_from_csv(selected_file, force_rebuild=force_rebuild, progress_callback=update_progress)
                except Exception as error:
                    st.error(f"벡터 DB 구축에 실패했습니다: {error}")
                    return
            progress.progress(1.0)
            status.success(f"벡터 DB 준비 완료: {count:,}개 문서")

    with settings_col:
        st.markdown("#### 챗봇 설정")
        api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
        model = st.selectbox(
            "Groq 모델",
            ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "openai/gpt-oss-20b"],
            index=0,
        )
        top_k = st.slider("벡터 검색 결과 수", min_value=3, max_value=12, value=8)
        min_similarity = st.slider("최소 유사도 기준", min_value=0.0, max_value=1.0, value=0.25, step=0.01)

    user_query = st.text_area(
        "어떤 책을 찾고 있나요?",
        placeholder="예: AI 코딩을 처음 배우는 직장인에게 맞는 책을 추천해줘",
        height=120,
    )
    ask = st.button("RAG 챗봇에게 추천 받기", type="primary")

    if "rag_answer" not in st.session_state:
        st.session_state.rag_answer = ""
    if "rag_results" not in st.session_state:
        st.session_state.rag_results = []
    if "numeric_analysis" not in st.session_state:
        st.session_state.numeric_analysis = None

    if ask:
        if not user_query.strip():
            st.warning("추천 요청을 입력해 주세요.")
            return

        st.session_state.rag_results = []
        st.session_state.numeric_analysis = None

        numeric_analysis = analyze_numeric_book_query(df, user_query)
        if numeric_analysis is not None:
            st.session_state.numeric_analysis = numeric_analysis
            st.session_state.rag_answer = build_numeric_answer(numeric_analysis)
            return

        if store.count() == 0:
            st.warning("먼저 벡터 DB를 구축해 주세요.")
            return

        with st.spinner("ChromaDB에서 관련 도서를 검색하는 중입니다..."):
            try:
                results = filter_results_for_current_df(store.search(user_query, n_results=top_k), df)
            except Exception as error:
                st.error(f"벡터 검색에 실패했습니다: {error}")
                return

        results = [result for result in results if result.similarity >= min_similarity]
        st.session_state.rag_results = results

        if not results:
            st.session_state.rag_answer = "추천할 도서가 없습니다."
        elif not api_key.strip():
            st.warning("Groq API Key를 입력해 주세요.")
            return
        else:
            with st.spinner("Groq가 벡터 검색 결과를 바탕으로 답변하는 중입니다..."):
                try:
                    st.session_state.rag_answer = call_groq_chat(api_key.strip(), model, user_query, results)
                except requests.HTTPError as error:
                    detail = error.response.text[:500] if error.response is not None else str(error)
                    st.error(f"Groq API 요청이 실패했습니다: {detail}")
                    return
                except requests.RequestException as error:
                    st.error(f"Groq API에 연결하지 못했습니다: {error}")
                    return
                except (KeyError, IndexError) as error:
                    st.error(f"Groq 응답 형식을 해석하지 못했습니다: {error}")
                    return

    if st.session_state.rag_answer:
        st.markdown("#### 답변")
        st.markdown(st.session_state.rag_answer)

    if st.session_state.numeric_analysis is not None:
        render_numeric_results(st.session_state.numeric_analysis)

    if st.session_state.rag_results:
        render_vector_results(st.session_state.rag_results)


def main() -> None:
    st.title("YES24 IT/모바일 베스트셀러 EDA 대시보드")
    st.caption("수집한 YES24 도서 데이터를 탐색하고, KLUE-BERT/ChromaDB RAG 기반 추천 챗봇을 제공합니다.")

    data_files = get_data_files()
    if not data_files:
        st.error(f"data 폴더에 CSV 파일이 없습니다: {DATA_DIR}")
        return

    default_index = data_files.index(DEFAULT_DATA_FILE) if DEFAULT_DATA_FILE in data_files else 0
    selected_file = st.sidebar.selectbox("데이터 파일", data_files, index=default_index, format_func=lambda path: path.name)

    with st.spinner("데이터를 불러오는 중입니다..."):
        df = load_data(str(selected_file))

    filtered_df = apply_sidebar_filters(df)

    st.sidebar.divider()
    st.sidebar.metric("현재 분석 대상", f"{len(filtered_df):,}권")
    st.sidebar.caption(f"데이터 위치: {selected_file.relative_to(BASE_DIR)}")

    if filtered_df.empty:
        st.warning("필터 조건에 맞는 데이터가 없습니다.")
        return

    tab_eda, tab_search, tab_chatbot = st.tabs(["EDA", "도서 검색", "RAG 챗봇 추천"])
    with tab_eda:
        render_eda(filtered_df)
    with tab_search:
        render_search(filtered_df)
    with tab_chatbot:
        render_chatbot(filtered_df, selected_file)


if __name__ == "__main__":
    main()
