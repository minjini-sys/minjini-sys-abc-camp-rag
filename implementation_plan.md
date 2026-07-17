# YES24 IT 모바일 베스트셀러 도서 목록 크롤러 구현 계획

이 계획은 YES24의 IT 모바일 종합 베스트 도서 목록 전체 페이지를 크롤링하여 도서 데이터를 수집하고, 이를 CSV 파일 형태로 저장하는 스크립트를 구현하는 것을 목표로 합니다.

## User Review Required

> [!NOTE]
> 수집 과정에서 봇 차단을 방지하기 위해 실제 브라우저와 유사한 Request Header (`User-Agent`, `Referer`, `Accept` 등)를 구성하여 요청을 보냅니다.
> 또한, 웹서버에 과도한 부하를 주지 않기 위해 각 페이지 요청 사이에 적절한 지연 시간(예: 1초 내외)을 추가하여 안전하게 크롤링을 진행합니다.

> [!IMPORTANT]
> 파이썬 가상환경은 사용자 가이드라인에 따라 `uv`를 사용하며, 기존에 `.venv` 폴더가 존재하지 않으므로 새롭게 생성하여 진행합니다.

## Proposed Changes

### 가상환경 설정 및 의존성 설치
- `.venv` 파이썬 가상환경 생성 (`uv venv`)
- 필수 라이브러리 설치 (`uv pip install requests beautifulsoup4 pandas`)

---

### 크롤러 스크립트 구현

#### [NEW] [yes24_crawler.py](file:///c:/documents/26-1/한신대ABC캠프-2026/ABC-RAG/yes24_crawler.py)
전체 페이지를 수집하는 크롤러 메인 스크립트입니다. 주요 로직은 다음과 같습니다.
1. **브라우저 모사**: `requests.Session` 객체를 사용하고, 헤더 정보(User-Agent 등)를 설정하여 실제 웹 브라우저에서 보낸 요청처럼 만듭니다.
2. **페이지 루프**: `pageNumber`를 1부터 순차적으로 증가시키며 데이터를 요청합니다. 더 이상 도서 데이터가 없는 페이지(또는 404 에러나 도서 목록 영역이 비어 있는 경우)에 도달하면 루프를 종료합니다.
3. **데이터 파싱**: `BeautifulSoup`을 사용하여 도서명, 저자, 출판사, 출판일, 판매가, 평점, 상세 페이지 링크 등의 정보를 파싱합니다.
4. **결과 저장**: 수집된 데이터를 `pandas` DataFrame으로 정제한 후 `yes24_it_mobile_bestsellers.csv` 파일로 내보냅니다.

## Verification Plan

### Automated/Manual Verification
- 작성한 `yes24_crawler.py` 스크립트를 가상환경에서 실행합니다.
- 콘솔 출력을 통해 진행 상황(수집 중인 페이지 수 및 수집된 도서 개수)을 확인합니다.
- 정상 종료 후 `yes24_it_mobile_bestsellers.csv` 파일이 생성되었는지 확인하고, 해당 파일의 일부 데이터를 읽어 컬럼과 내용이 올바른지 확인합니다.
