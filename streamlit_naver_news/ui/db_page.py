"""DB 저장 뉴스 조회 페이지.

MySQL에 저장된 뉴스 데이터를 검색하고 결과를 표로 표시한다.
"""

import mysql.connector
import streamlit as st

from config.settings import SettingsError, get_settings
from db.news_repository import find_news
from ui.news_view import render_db_query_controls, render_news_table


def render_db_page():
    """DB에 저장된 뉴스 데이터를 조회하는 페이지."""

    st.title("DB 저장 뉴스 조회")
    st.write("MySQL에 저장된 뉴스 데이터를 제목과 설명 기준으로 검색합니다.")

    try:
        settings = get_settings()
    except SettingsError as e:
        # DB 접속 정보가 없거나 API Key가 누락된 경우 사용자에게 오류를 보여주고 중단한다.
        st.error(str(e))
        st.stop()

    # 조회 결과를 session_state에 저장해 화면 재실행 시에도 표가 바로 사라지지 않도록 한다.
    if "stored_news" not in st.session_state:
        st.session_state["stored_news"] = []

    db_keyword, db_limit, query_clicked = render_db_query_controls()

    if query_clicked:
        try:
            st.session_state["stored_news"] = find_news(
                db_settings=settings.database,
                keyword=db_keyword,
                limit=db_limit,
            )
            st.success(f"DB 조회 완료: {len(st.session_state['stored_news'])}건")
        except mysql.connector.Error as e:
            st.error(f"DB 조회 오류: {e}")

    render_news_table("DB 저장 뉴스 조회 결과", st.session_state["stored_news"])
