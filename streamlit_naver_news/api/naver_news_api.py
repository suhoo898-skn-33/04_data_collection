"""네이버 뉴스 OpenAPI 호출 모듈.

이 파일은 외부 API 요청과 응답 변환만 담당하고, 화면 출력이나 DB 저장은 담당하지 않는다.
"""

import requests

from config.settings import NaverApiSettings
from models.news import NaverNews


NAVER_NEWS_API_URL = "https://openapi.naver.com/v1/search/news.json"


def search_news(
    api_settings: NaverApiSettings,
    keyword: str,
    display: int,
    start: int,
    sort: str,
) -> list[NaverNews]:
    """네이버 뉴스 검색 OpenAPI를 호출하고 결과를 NaverNews 리스트로 변환한다."""

    # params는 URL query string으로 전달된다.
    # 예: ?query=인공지능&display=10&start=1&sort=date
    params = {
        "query": keyword,
        "display": display,
        "start": start,
        "sort": sort,
    }

    # timeout=10은 10초 안에 응답이 없으면 요청을 중단한다.
    # raise_for_status()는 4xx, 5xx 응답을 예외로 바꿔준다.
    response = requests.get(
        NAVER_NEWS_API_URL,
        headers=api_settings.headers,
        params=params,
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()
    items = data.get("items", [])

    # API 응답 dict 목록을 앱 내부에서 다루기 쉬운 모델 객체 목록으로 바꾼다.
    return [NaverNews.from_api_item(item) for item in items]
