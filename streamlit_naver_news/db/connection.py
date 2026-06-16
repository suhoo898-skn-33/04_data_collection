"""" DB 연결 모듈

DB 연결 코드를 모아두고, 재사용 목적
"""

import mysql.connector

from config.settings import DatabaseSettings

def get_connection(db_settings: DatabaseSettings):
    # MySQL 연결 객체 생성

    return mysql.connector.connect(
        host=db_settings.host,
        port=db_settings.port,
        user=db_settings.user,
        password=db_settings.password,
        database=db_settings.database
    )