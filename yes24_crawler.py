"""YES24 IT 모바일 종합 베스트셀러 도서 정보를 수집하는 크롤러 모듈.

이 모듈은 지정된 카테고리의 베스트셀러 페이지를 순회하며 
도서명, 저자, 출판사, 가격, 평점 등 상세 정보를 크롤링하고 
이를 CSV 파일로 저장하는 기능을 제공합니다.
봇 차단을 방지하기 위해 실제 웹 브라우저의 HTTP Request Header를 모사합니다.
"""

import time
import re
from typing import Dict, List, Any, Optional
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 대상 카테고리 URL 템플릿 (IT 모바일 종합 베스트셀러)
BASE_URL = (
    "https://www.yes24.com/product/category/bestseller"
    "?categoryNumber=001001003&pageNumber={page}&pageSize=24"
)

# 실제 브라우저 요청과 유사한 헤더 설정
HEADERS = {
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
    # 연속된 공백 및 줄바꿈을 단일 공백으로 치환
    cleaned = re.sub(r"\s+", " ", text)
    return cleaned.strip()


def parse_book_item(item: BeautifulSoup) -> Dict[str, Any]:
    """개별 도서 태그 객체(li)를 파싱하여 도서 정보 딕셔너리를 반환한다.

    Args:
        item: BeautifulSoup으로 파싱된 li 태그 객체.

    Returns:
        순위, 도서명, 저자, 가격, 평점 등을 포함하는 도서 정보 딕셔너리.
    """
    # 도서 고유 ID 추출
    goods_no = item.get("data-goods-no", "")

    # 순위 추출
    rank_tag = item.find("em", class_="rank")
    rank = rank_tag.text.strip() if rank_tag else ""

    # 도서 정보 영역 추출
    item_info = item.find("div", class_="item_info")
    if not item_info:
        return {}

    # 도서명 및 링크 추출
    title_tag = item_info.find("a", class_="gd_name")
    title = clean_text(title_tag.text) if title_tag else ""
    link = (
        f"https://www.yes24.com{title_tag['href']}"
        if title_tag and title_tag.has_attr("href")
        else ""
    )

    # 저자, 출판사, 출간일 추출
    # YES24 개편에 따라 이 정보들은 info_pubGrp 클래스 내부에 모여 있습니다.
    author_tag = item_info.find("span", class_="info_auth")
    author = clean_text(author_tag.text) if author_tag else ""

    publisher_tag = item_info.find("span", class_="info_pub")
    publisher = clean_text(publisher_tag.text) if publisher_tag else ""

    date_tag = item_info.find("span", class_="info_date")
    pub_date = clean_text(date_tag.text) if date_tag else ""

    # 가격 정보 추출 (판매가, 정가, 할인율)
    sale_price_tag = item_info.select_one("div.info_price strong.txt_num em.yes_b")
    sale_price = sale_price_tag.text.strip() if sale_price_tag else ""

    original_price_tag = item_info.select_one("div.info_price span.txt_num.dash em.yes_m")
    original_price = original_price_tag.text.strip() if original_price_tag else ""

    discount_tag = item_info.select_one("div.info_price span.txt_sale em.num")
    discount_rate = discount_tag.text.strip() if discount_tag else ""

    # 평점 및 리뷰 수 추출
    rating_tag = item_info.select_one("span.rating_grade em.yes_b")
    rating = rating_tag.text.strip() if rating_tag else ""

    review_tag = item_info.select_one("span.rating_rvCount a em.txC_blue")
    review_count = review_tag.text.strip() if review_tag else "0"

    # 판매지수 추출
    sales_tag = item_info.select_one("span.saleNum")
    sales_index = ""
    if sales_tag:
        # '판매 38,511' 형식에서 숫자 및 쉼표만 남김
        sales_match = re.search(r"[\d,]+", sales_tag.text)
        if sales_match:
            sales_index = sales_match.group(0)

    return {
        "순위": rank,
        "도서ID": goods_no,
        "도서명": title,
        "저자": author,
        "출판사": publisher,
        "출간일": pub_date,
        "판매가(원)": sale_price,
        "정가(원)": original_price,
        "할인율(%)": discount_rate,
        "평점": rating,
        "리뷰수": review_count,
        "판매지수": sales_index,
        "상세페이지링크": link,
    }


def fetch_bestsellers() -> List[Dict[str, Any]]:
    """YES24 IT 모바일 베스트셀러 목록의 전체 페이지 데이터를 수집한다.

    각 페이지를 요청하여 데이터를 수집하며, 더 이상 데이터가 없거나 
    이전 페이지와 동일한 목록이 반환되는 시점에 수집을 중단한다.

    Returns:
        수집된 모든 도서 정보 객체들의 리스트.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    all_books: List[Dict[str, Any]] = []
    seen_goods_ids = set()
    page = 1

    # 무한 루프 방지를 위해 최대 페이지 제한 설정
    max_pages = 50

    while page <= max_pages:
        url = BASE_URL.format(page=page)
        print(f"페이지 {page} 수집 중: {url}")

        try:
            response = session.get(url, timeout=10)
            if response.status_code != 200:
                print(
                    f"에러: 페이지 {page} 요청이 실패했습니다. (상태 코드: {response.status_code})"
                )
                break

            soup = BeautifulSoup(response.text, "html.parser")
            best_list = soup.find(id="yesBestList")

            # 도서 목록 영역이 없는 경우 수집 종료
            if not best_list:
                print(f"더 이상 도서 목록이 존재하지 않습니다. (페이지 {page} 종료)")
                break

            # 중첩 구조 방지를 위해 최상위 li 태그만 선택
            items = best_list.find_all("li", recursive=False)
            if not items:
                print(f"페이지 {page}에 도서 아이템이 없습니다. 종료합니다.")
                break

            # 현재 페이지에서 새로 추가된 도서가 있는지 판별하는 플래그
            new_books_in_page = 0

            for item in items:
                book_data = parse_book_item(item)
                if not book_data or not book_data.get("도서명"):
                    continue

                goods_id = book_data.get("도서ID")
                # 중복 수집된 도서가 아닐 경우에만 추가
                if goods_id and goods_id not in seen_goods_ids:
                    seen_goods_ids.add(goods_id)
                    all_books.append(book_data)
                    new_books_in_page += 1

            # 만약 현재 페이지의 모든 도서가 이미 이전 페이지에서 수집되었다면 중단
            # 이는 마지막 페이지를 넘어섰을 때 동일한 마지막 페이지 데이터가 반복되어 반환되는 것을 방지합니다.
            if new_books_in_page == 0:
                print(
                    f"페이지 {page}에서 새로 수집된 도서가 없습니다. 수집을 완료합니다."
                )
                break

            print(
                f"페이지 {page} 완료: {new_books_in_page}개 신규 도서 추가 (누적: {len(all_books)}개)"
            )

            # 웹서버 부하 경감 및 봇 탐지 우회를 위한 지연 시간
            time.sleep(1.0)
            page += 1

        except requests.RequestException as error:
            print(f"페이지 {page} 요청 중 네트워크 에러 발생: {error}")
            break

    return all_books


def main() -> None:
    """메인 실행 함수.

    베스트셀러 정보를 수집하여 데이터프레임으로 변환하고 
    최종 결과물을 CSV 파일로 저장한다.
    """
    print("YES24 IT 모바일 종합 베스트셀러 크롤링을 시작합니다...")
    books = fetch_bestsellers()

    if not books:
        print("수집된 도서 데이터가 없습니다. 스크립트를 종료합니다.")
        return

    # DataFrame 생성 및 정렬
    df = pd.DataFrame(books)

    # 순위 정보를 기준으로 데이터 정렬 (순위는 숫자로 가공하여 정렬)
    df["순위_숫자"] = pd.to_numeric(df["순위"], errors="coerce")
    df = df.sort_values(by="순위_숫자").drop(columns=["순위_숫자"])

    # CSV 파일 저장 (한글 깨짐 방지를 위해 utf-8-sig 인코딩 적용)
    output_filename = "yes24_it_mobile_bestsellers.csv"
    try:
        df.to_csv(output_filename, index=False, encoding="utf-8-sig")
        print(
            f"성공적으로 데이터를 수집하여 '{output_filename}' 파일로 저장했습니다."
        )
        print(f"총 수집된 도서 수: {len(df)}개")
    except IOError as error:
        print(f"CSV 파일 저장 중 오류가 발생했습니다: {error}")


if __name__ == "__main__":
    main()
