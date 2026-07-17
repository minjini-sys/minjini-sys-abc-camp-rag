# YES24 IT/모바일 베스트셀러 EDA 및 RAG 추천 시스템

YES24 IT 모바일 종합 베스트셀러 도서 데이터를 수집하고, 탐색적 데이터 분석(EDA) 대시보드와 벡터 검색 기반 RAG 추천 챗봇을 제공하는 프로젝트입니다.

## 주요 기능

### 1. YES24 베스트셀러 크롤러 (`yes24_crawler.py`)
- YES24 IT 모바일 종합 베스트셀러 페이지를 순회하며 도서 정보 수집
- 도서명, 저자, 출판사, 가격, 평점, 리뷰수, 판매지수 등 상세 정보 파싱
- 중복 수집 방지 및 봇 차단 우회 처리
- 결과를 CSV 파일(`data/yes24_it_mobile_bestsellers.csv`)로 저장

### 2. 데이터 보강 (`src/data_enricher.py`)
- 수집된 도서의 YES24 상세페이지에서 책 소개 텍스트 수집
- 상위 N개 도서에 대해 내용 컬럼 보강
- 5개마다 중간 저장하여 데이터 유실 최소화

### 3. Streamlit EDA 대시보드 (`src/dashboard.py`)
- **EDA 탭**: 출판사별 도서 수, 평점 분포, 판매가 분포, 리뷰수-판매지수 관계 등 시각화
- **도서 검색 탭**: 키워드 검색 및 상세 정보 열람
- **RAG 챗봇 탭**: KLUE-BERT 임베딩 + ChromaDB 기반 도서 추천 챗봇 (Groq API 연동)
- 사이드바 필터 (출판사, 평점, 가격 범위)

### 4. 엑셀 대시보드 (`src/create_excel_dashboard.py`)
- 수집된 데이터 기반 Excel 대시보드 생성
- KPI 카드 (도서 수, 출판사 수, 평균 평점/판매가/판매지수)
- 출판사별 차트, 판매지수 Top 10, 판매가 분포, 연도별 추이 차트
- 3개 시트 구성: Dashboard, Analysis, Data

### 5. RAG 벡터 저장소 (`src/rag_vector_store.py`)
- KLUE-BERT(`klue/bert-base`) 모델로 도서 설명을 임베딩
- ChromaDB 기반 벡터 저장소 구축 및 검색
- CSV 변경 감지(fingerprint)로 자동 재구축

## 프로젝트 구조

```
ABC-RAG/
├── yes24_crawler.py              # YES24 베스트셀러 크롤러
├── requirements.txt               # 의존성 패키지 목록
├── .gitignore                     # Git 제외 파일 목록
├── implementation_plan.md         # 구현 계획 문서
│
├── data/
│   ├── yes24_it_mobile_bestsellers.csv  # 수집된 베스트셀러 데이터
│   ├── chroma_yes24/                    # ChromaDB 벡터 저장소 (Git 제외)
│   └── hf_models/                       # HuggingFace 모델 캐시 (Git 제외)
│
├── src/
│   ├── dashboard.py               # Streamlit EDA + RAG 대시보드
│   ├── create_excel_dashboard.py  # 엑셀 대시보드 생성
│   ├── data_enricher.py           # 도서 내용 데이터 보강
│   └── rag_vector_store.py        # KLUE-BERT + ChromaDB 벡터 저장소
│
└── outputs/                       # 생성된 문서 파일 (Git 제외)
    ├── 신규_도서_기획_제안서.pptx
    └── yes24_dashboard/
        └── yes24_books_dashboard.xlsx
```

## 설치 및 실행

### 의존성 설치

```bash
pip install -r requirements.txt
```

### 데이터 수집

```bash
python yes24_crawler.py
```

### 데이터 보강 (책 소개 내용 수집)

```bash
python src/data_enricher.py
```

### 대시보드 실행

```bash
streamlit run src/dashboard.py
```

### 엑셀 대시보드 생성

```bash
python src/create_excel_dashboard.py
# outputs/yes24_dashboard/yes24_books_dashboard.xlsx 생성
```

## 주요 의존성

- `requests`, `beautifulsoup4` — 웹 크롤링
- `pandas`, `openpyxl` — 데이터 처리 및 엑셀 생성
- `streamlit`, `plotly` — EDA 대시보드
- `chromadb` — 벡터 데이터베이스
- `transformers`, `torch` — KLUE-BERT 임베딩
