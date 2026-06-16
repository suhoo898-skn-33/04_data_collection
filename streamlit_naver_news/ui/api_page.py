"""API 조회 페이지.

네이버 뉴스 검색, 검색 결과 화면 출력, DB 저장 버튼 처리를 한 페이지에서 담당한다.
"""

import mysql.connector
import requests
import streamlit as st

from api.naver_news_api import search_news
from config.settings import SettingsError, get_settings
from db.news_repository import save_news_list
from ui.news_view import (
    render_database_notice,
    render_news_table,
    render_save_result,
    render_search_controls,
)


def render_api_page():
    """네이버 뉴스 API 조회와 DB 저장을 담당하는 페이지."""

    st.title("API 조회")
    st.write("검색 조건을 입력해 네이버 뉴스 OpenAPI를 조회하고, 결과를 확인한 뒤 DB에 저장합니다.")
    render_database_notice()

    try:
        settings = get_settings()
    except SettingsError as e:
        # 필수 환경변수가 없으면 이후 API/DB 작업을 진행할 수 없으므로 페이지 실행을 멈춘다.
        st.error(str(e))
        st.stop()

    # session_state를 사용하면 검색 버튼을 누른 뒤에도 결과가 화면에 유지된다.
    if "search_results" not in st.session_state:
        st.session_state["search_results"] = []

    if "save_result" not in st.session_state:
        st.session_state["save_result"] = None

    keyword, display, start, sort, search_clicked = render_search_controls()

    if search_clicked:
        if not keyword.strip():
            st.warning("검색어를 입력해 주세요.")
        else:
            try:
                st.session_state["search_results"] = search_news(
                    api_settings=settings.naver_api,
                    keyword=keyword.strip(),
                    display=display,
                    start=start,
                    sort=sort,
                )
                st.session_state["save_result"] = None
                st.success(f"API 조회 완료: {len(st.session_state['search_results'])}건")
            except requests.exceptions.Timeout:
                st.error("API 요청 시간이 초과되었습니다.")
            except requests.exceptions.HTTPError as e:
                st.error(f"API HTTP 오류: {e}")
            except requests.exceptions.RequestException as e:
                st.error(f"API 요청 오류: {e}")
            except ValueError:
                st.error("API 응답을 JSON으로 변환할 수 없습니다.")

    render_news_table("API 조회 결과", st.session_state["search_results"])

    if st.session_state["search_results"]:
        # API 조회와 DB 저장 버튼을 분리해 학생들이 두 단계 흐름을 명확히 볼 수 있게 한다.
        if st.button("DB에 저장", type="primary"):
            try:
                insert_count, skip_count = save_news_list(
                    settings.database,
                    st.session_state["search_results"],
                )
                st.session_state["save_result"] = (insert_count, skip_count)
                st.success("DB 저장 작업이 완료되었습니다.")
            except mysql.connector.Error as e:
                st.error(f"DB 저장 오류: {e}")

    if st.session_state["save_result"]:
        render_save_result(*st.session_state["save_result"])
