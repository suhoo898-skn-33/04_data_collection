"""뉴스 데이터 저장소 모듈.

SQL 실행은 이 파일에 모아두고, API 호출이나 Streamlit 화면 코드는 분리한다.
"""

import mysql.connector

from config.settings import DatabaseSettings
from db.connection import get_connection
from models.news import NaverNews


def save_news_list(
    db_settings: DatabaseSettings,
    news_list: list[NaverNews],
) -> tuple[int, int]:
    """뉴스 목록을 DB에 저장하고, 신규 저장/중복 제외 건수를 반환한다."""

    insert_count = 0
    skip_count = 0

    # with 문을 사용하면 DB 작업이 끝난 뒤 연결과 cursor를 자동으로 정리할 수 있다.
    with get_connection(db_settings) as conn:
        with conn.cursor() as cursor:
            for news in news_list:
                # link 컬럼의 unique 제약조건을 기준으로 이미 저장된 뉴스는 insert하지 않는다.
                cursor.execute(
                    """
                    insert into naver_news
                        (title, originallink, link, description, pub_date)
                    values
                        (%s, %s, %s, %s, %s)
                    on duplicate key update
                        link = link
                    """,
                    news.to_db_params(),
                )

                # 신규 insert면 rowcount가 1이고, 중복이면 의미 없는 update라 0이 된다.
                if cursor.rowcount == 1:
                    insert_count += 1
                else:
                    skip_count += 1

            conn.commit()

    return insert_count, skip_count


def find_news(
    db_settings: DatabaseSettings,
    keyword: str = "",
    limit: int = 30,
) -> list[NaverNews]:
    """DB에 저장된 뉴스 목록을 제목/설명 기준으로 조회한다."""

    # like 검색을 위해 검색어 앞뒤에 %를 붙인다.
    # 빈 문자열이면 %%가 되어 전체 데이터 중 limit 개수만 조회된다.
    search_keyword = f"%{keyword.strip()}%"

    with get_connection(db_settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                select
                    id,
                    title,
                    originallink,
                    link,
                    description,
                    pub_date,
                    created_at
                from
                    naver_news
                where
                    title like %s
                    or description like %s
                order by
                    id desc
                limit %s
                """,
                (search_keyword, search_keyword, limit),
            )
            rows = cursor.fetchall()

    return [NaverNews.from_db_row(row) for row in rows]


def is_duplicate_key_error(error: mysql.connector.Error) -> bool:
    """DB 작업 중 duplicate key 오류인지 확인하는 보조 함수."""

    return error.errno == 1062
