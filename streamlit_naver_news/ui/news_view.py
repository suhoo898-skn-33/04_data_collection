"""Streamlit 화면 조각 모듈.

여러 페이지에서 공통으로 사용하는 입력 폼, 표, 안내 메시지를 함수로 분리한다.
"""

import html
import re

import pandas as pd
import streamlit as st

from models.news import NaverNews


SORT_OPTIONS = {
    # 화면에 보이는 한글 라벨과 네이버 API에 전달할 실제 값을 매핑한다.
    "최신순(date)": "date",
    "정확도순(sim)": "sim",
}


def clean_html_text(value: str) -> str:
    """API 응답에 포함된 <b> 태그와 HTML entity를 화면용 텍스트로 정리한다."""

    text = re.sub(r"<[^>]+>", "", value or "")
    return html.unescape(text)


def news_to_dataframe(news_list: list[NaverNews]) -> pd.DataFrame:
    """NaverNews 리스트를 Streamlit 표에 적합한 DataFrame으로 변환한다."""

    rows = []
    for news in news_list:
        row = news.to_display_dict()
        row["title"] = clean_html_text(row["title"])
        row["description"] = clean_html_text(row["description"])
        rows.append(row)

    return pd.DataFrame(rows)


def render_header():
    st.title("네이버 뉴스 검색/저장/조회 예시")
    st.write(
        "네이버 뉴스 OpenAPI로 데이터를 조회하고, 버튼을 눌러 MySQL에 저장한 뒤, "
        "저장된 데이터를 다시 조회하는 Streamlit 예제입니다."
    )


def render_database_notice():
    with st.expander("중복 저장 방지를 위한 DB 설정"):
        st.write("`link` 컬럼에 Unique 제약조건이 있어야 같은 뉴스가 중복 저장되지 않습니다.")
        st.code(
            """
alter table naver_news
add constraint uq_naver_news_link unique (link);
            """.strip(),
            language="sql",
        )


def render_search_controls() -> tuple[str, int, int, str, bool]:
    """API 조회 페이지에서 사용할 검색 조건 입력 폼을 그린다."""

    st.subheader("API 검색 조건")

    # form을 사용하면 사용자가 입력값을 조정한 뒤 검색 버튼을 눌렀을 때만 API를 호출한다.
    with st.form("api_search_form"):
        col1, col2 = st.columns([2, 1])
        keyword = col1.text_input("검색어", value="인공지능")
        sort_label = col2.selectbox("정렬 방식", options=list(SORT_OPTIONS.keys()))

        col3, col4 = st.columns(2)
        display = col3.slider("표시 개수", min_value=10, max_value=100, value=10, step=10)
        start = col4.number_input("검색 시작 위치", min_value=1, max_value=1000, value=1, step=10)

        search_clicked = st.form_submit_button("검색", type="primary")

    return keyword, display, start, SORT_OPTIONS[sort_label], search_clicked


def render_news_table(title: str, news_list: list[NaverNews]):
    """뉴스 목록을 Streamlit dataframe으로 표시한다."""

    st.subheader(title)

    if not news_list:
        st.info("표시할 뉴스 데이터가 없습니다.")
        return

    df = news_to_dataframe(news_list)
    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("ID"),
            "title": st.column_config.TextColumn("제목"),
            "originallink": st.column_config.LinkColumn("원문 링크"),
            "link": st.column_config.LinkColumn("네이버 링크"),
            "description": st.column_config.TextColumn("요약"),
            "pubDate": st.column_config.TextColumn("발행일"),
            "created_at": st.column_config.DatetimeColumn("저장 시각"),
        },
    )


def render_save_result(insert_count: int, skip_count: int):
    """DB 저장 결과를 신규 저장/중복 제외 지표로 표시한다."""

    st.subheader("DB 저장 결과")
    col1, col2 = st.columns(2)
    col1.metric("신규 저장", f"{insert_count}건")
    col2.metric("중복 제외", f"{skip_count}건")


def render_db_query_controls() -> tuple[str, int, bool]:
    """DB 조회 페이지에서 사용할 검색 조건 입력 폼을 그린다."""

    st.subheader("DB 조회 조건")

    with st.form("db_query_form"):
        col1, col2 = st.columns([2, 1])
        keyword = col1.text_input("DB 검색어", value="")
        limit = col2.slider("조회 개수", min_value=10, max_value=100, value=30, step=10)
        query_clicked = st.form_submit_button("DB 조회", type="primary")

    return keyword, limit, query_clicked
