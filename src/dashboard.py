"""YES24 book data EDA & Search dashboard (lightweight version for Streamlit Cloud).

Run locally:
    streamlit run streamlit_app.py

Full version with RAG chatbot:
    streamlit run src/dashboard_local.py
"""

from __future__ import annotations

import html
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_DATA_FILE = DATA_DIR / "yes24_it_mobile_bestsellers.csv"


# ── 데이터 로드 (rag_vector_store 의존성 없이 자체 포함) ──

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
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False).str.strip(),
        errors="coerce",
    )


NUMERIC_COLUMNS = ["순위", "판매가(원)", "정가(원)", "할인율(%)", "평점", "리뷰수", "판매지수"]
TEXT_COLUMNS = ["도서명", "저자", "출판사", "출간일", "상세페이지링크", "내용"]


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


# ── 데이터 캐싱 ──

@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    return load_yes24_csv(path)


# ── 헬퍼 ──

def format_won(value: float | int | None) -> str:
    if pd.isna(value):
        return "-"
    return f"{int(value):,}원"


def format_number(value: float | int | None) -> str:
    if pd.isna(value):
        return "-"
    return f"{int(value):,}"


def get_data_files() -> list[Path]:
    if not DATA_DIR.exists():
        return []
    return sorted(DATA_DIR.glob("*.csv"))


# ── 필터 ──

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
    filtered = filtered[
        filtered["평점"].between(rating_range[0], rating_range[1], inclusive="both")
    ]
    filtered = filtered[
        filtered["판매가(원)"].between(price_range[0], price_range[1], inclusive="both")
    ]
    return filtered


# ── EDA 탭 ──

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
    display_cols = [
        "순위", "도서명", "저자", "출판사", "출간일",
        "판매가(원)", "평점", "리뷰수", "판매지수",
    ]
    st.dataframe(df[display_cols], use_container_width=True, hide_index=True)


# ── 검색 탭 ──

def search_books(df: pd.DataFrame, query: str, match_mode: str) -> pd.DataFrame:
    keywords = [token.lower() for token in query.split() if token.strip()]
    if not keywords:
        return df.copy()

    masks = [
        df["검색문서"].str.contains(keyword, case=False, regex=False, na=False)
        for keyword in keywords
    ]
    if match_mode == "모든 키워드 포함":
        combined = masks[0]
        for item in masks[1:]:
            combined = combined & item
    else:
        combined = masks[0]
        for item in masks[1:]:
            combined = combined | item
    return df[combined].copy()


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
        st.write(
            f"**평점/리뷰:** {book.get('평점', 0):.1f} / "
            f"리뷰 {format_number(book.get('리뷰수'))}개"
        )
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
        sort_by = st.selectbox(
            "정렬",
            [
                "순위 낮은 순",
                "판매지수 높은 순",
                "평점 높은 순",
                "리뷰수 많은 순",
                "판매가 낮은 순",
            ],
        )

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
    display_cols = [
        "순위", "도서명", "저자", "출판사", "출간일",
        "판매가(원)", "평점", "리뷰수", "판매지수",
    ]
    st.dataframe(result[display_cols], use_container_width=True, hide_index=True, height=360)

    if result.empty:
        st.info("검색 조건에 맞는 도서가 없습니다.")
        return

    selected_title = st.selectbox("상세히 볼 도서", result["도서명"].tolist())
    selected_book = result[result["도서명"] == selected_title].iloc[0]
    render_book_detail(selected_book)


# ── 메인 ──

def main() -> None:
    st.set_page_config(
        page_title="YES24 도서 EDA 대시보드",
        page_icon="📚",
        layout="wide",
    )

    st.title("YES24 IT/모바일 베스트셀러 EDA 대시보드")
    st.caption(
        "수집한 YES24 도서 데이터를 탐색하고 검색할 수 있습니다. "
        "RAG 챗봇 추천 기능은 로컬에서 `streamlit run src/dashboard_local.py`로 실행하세요."
    )

    data_files = get_data_files()
    if not data_files:
        st.error(f"`data/` 폴더에 CSV 파일이 없습니다: {DATA_DIR}")
        return

    default_index = (
        data_files.index(DEFAULT_DATA_FILE) if DEFAULT_DATA_FILE in data_files else 0
    )
    selected_file = st.sidebar.selectbox(
        "데이터 파일",
        data_files,
        index=default_index,
        format_func=lambda path: path.name,
    )

    with st.spinner("데이터를 불러오는 중입니다..."):
        df = load_data(str(selected_file))

    filtered_df = apply_sidebar_filters(df)

    st.sidebar.divider()
    st.sidebar.metric("현재 분석 대상", f"{len(filtered_df):,}권")

    if filtered_df.empty:
        st.warning("필터 조건에 맞는 데이터가 없습니다.")
        return

    tab_eda, tab_search = st.tabs(["EDA", "도서 검색"])
    with tab_eda:
        render_eda(filtered_df)
    with tab_search:
        render_search(filtered_df)


if __name__ == "__main__":
    main()
