# 실행 파일
# 실행 명령어 : streamlit run app.py

import streamlit as st
from ui.api_page import render_api_page
from ui.db_page import render_db_page

# 앱 전체에 공통으로 적용할 브라우저 제목, 화면 너비 설정
st.set_page_config(
    '네이버 뉴스 검색/저장/조회',
    layout='wide',
)

# 페이지 등록 작업
api_page = st.Page(
    render_api_page,
    title="API 조회",
    default=True    # 기본 페이지(첫 페이지)
)

db_page = st.Page(
    render_db_page,
    title="DB 저장 뉴스 조회"
)

# 사이드바 네비게이션 등록
navigation = st.navigation([api_page, db_page], position="sidebar")
navigation.run()

