"""YES24 도서 상세페이지에서 도서 소개(내용)를 수집하여 데이터셋을 보강하는 전처리 모듈.

이 모듈은 기존 수집된 CSV 데이터의 상세페이지 링크를 기반으로 각 도서의 책 소개 텍스트를 크롤링하고,
'내용' 컬럼을 추가하여 최종 CSV 파일로 저장하는 기능을 제공합니다.
봇 차단을 방지하기 위해 요청 간 적절한 지연 시간을 유지하며, 과도한 서버 부하를 막기 위해
상위 N개의 도서에 대해서만 수집을 진행할 수 있도록 제한할 수 있습니다.
"""

import os
import sys
import time
import re
from typing import Optional, Dict, Any
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 윈도우 환경 콘솔 출력 시 한글 특수문자(∙ 등) 인코딩 에러 방지
sys.stdout.reconfigure(encoding='utf-8')

# 실제 웹 브라우저의 HTTP Request Header를 모사하기 위한 설정
HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.7"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.yes24.com/",
    "Connection": "keep-alive",
}


def clean_text(text: Optional[str]) -> str:
    """텍스트 데이터의 줄바꿈, 연속된 공백 등을 제거하여 정제한다.

    Args:
        text: 정제할 원본 문자열.

    Returns:
        정제된 문자열. 공백이 제거되거나 빈 문자열이 반환될 수 있음.
    """
    if not text:
        return ""
    # 연속된 공백 및 줄바꿈을 단일 공백으로 치환하여 가독성을 높임
    cleaned = re.sub(r"\s+", " ", text)
    return cleaned.strip()


def fetch_book_introduction(url: str, session: requests.Session) -> str:
    """지정된 YES24 상세페이지 URL에서 도서 소개(책 소개) 텍스트를 추출한다.

    상세페이지 내 책 소개 영역을 BeautifulSoup 셀렉터로 파싱합니다.
    YES24의 HTML 레이아웃 특성에 맞춰 여러 백업 셀렉터를 순차 탐색합니다.

    Args:
        url: 도서 상세페이지 URL.
        session: HTTP 요청 속도와 세션을 관리하기 위한 requests Session 객체.

    Returns:
        추출 및 정제된 책 소개 텍스트. 페이지 요청에 실패하거나 요소를 찾지 못하면 빈 문자열을 반환한다.
    """
    if not url or pd.isna(url):
        return ""

    try:
        response = session.get(url, timeout=10)
        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.text, "html.parser")
        
        # 1순위: 책소개가 포함된 대표적인 클래스 영역 탐색
        intro_elem = soup.find(class_="infoWrap_txt")
        if intro_elem:
            return clean_text(intro_elem.get_text())

        # 2순위: 상세 탭 하위의 정보 영역 탐색 (일부 개편 페이지 및 백업)
        intro_elem_alt = soup.find(id="infosub_info")
        if intro_elem_alt:
            return clean_text(intro_elem_alt.get_text())

    except requests.RequestException:
        # 크롤링 프로세스가 도중에 중단되지 않도록 네트워크 예외를 포착하고 빈 문자열을 반환
        pass

    return ""


def enrich_data(
    input_path: str,
    output_path: str,
    limit: int = 150,
) -> None:
    """기존 도서 데이터 CSV를 읽어 상위 N개 도서의 상세 소개를 추가하고 저장한다.

    지정한 개수만큼 순위별로 상세페이지 링크를 방문하여 '내용' 컬럼을 생성 및 보강합니다.
    도서 목록 중 상위 랭킹 위주로 데이터를 수집하여 속도와 안전성을 확보합니다.

    Args:
        input_path: 기존 도서 데이터 CSV 파일 경로.
        output_path: 상세 소개가 추가된 데이터를 저장할 CSV 파일 경로.
        limit: 상세 소개를 크롤링할 상위 도서의 최대 개수 (순위 기준).

    Raises:
        FileNotFoundError: 입력 경로에 원본 CSV 파일이 존재하지 않는 경우.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"입력 파일이 존재하지 않습니다: {input_path}")

    # 데이터 로드
    df = pd.read_csv(input_path)

    # '내용' 컬럼이 존재하지 않는 경우 생성
    if "내용" not in df.columns:
        df["내용"] = ""

    # 평점이 결측치인 경우 빈 문자열로 안전하게 채움
    df["내용"] = df["내용"].fillna("")

    session = requests.Session()
    session.headers.update(HEADERS)

    # 순위를 기준으로 데이터 정렬
    df["순위_숫자"] = pd.to_numeric(df["순위"], errors="coerce")
    df = df.sort_values(by="순위_숫자").reset_index(drop=True)

    # 실제 수집할 도서 수 산출
    total_to_crawl = min(len(df), limit)
    print(f"총 {len(df)}개 도서 중 상위 {total_to_crawl}개 도서의 책 소개글 수집을 시작합니다...")

    try:
        for idx in range(total_to_crawl):
            url = df.loc[idx, "상세페이지링크"]
            title = df.loc[idx, "도서명"]

            # 이미 내용이 수집되었거나 기존 정보가 있는 경우 생략 (점진적 업데이트 대응)
            if str(df.loc[idx, "내용"]).strip() != "":
                continue

            print(f"[{idx+1}/{total_to_crawl}] 수집 중: {title}")
            intro_text = fetch_book_introduction(url, session)
            df.loc[idx, "내용"] = intro_text

            # 5개마다 중간 저장하여 강제 종료 시에도 데이터 유실 최소화
            if (idx + 1) % 5 == 0:
                temp_df = df.drop(columns=["순위_숫자"])
                temp_df.to_csv(output_path, index=False, encoding="utf-8-sig")

            # 봇 탐지 우회를 위한 1.0초 지연 시간 유지 (수집 속도 향상 조정)
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n사용자 요청 또는 인터럽트에 의해 수집이 중단되었습니다. 현재까지의 수집 상태를 보존합니다.")
    finally:
        if "순위_숫자" in df.columns:
            df = df.drop(columns=["순위_숫자"])

        # 저장 경로의 상위 폴더 생성
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # 한글 인코딩을 위해 utf-8-sig 사용
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"데이터 파일 백업 및 최종 저장 완료: {output_path}")


if __name__ == "__main__":
    # 프로젝트 기본 경로 설정
    INPUT_FILE = "data/yes24_it_mobile_bestsellers.csv"
    OUTPUT_FILE = "data/yes24_it_mobile_bestsellers.csv"
    enrich_data(INPUT_FILE, OUTPUT_FILE, limit=80)
