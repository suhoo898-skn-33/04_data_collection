"""뉴스 데이터 모델.

API 응답 dict와 DB 조회 row를 같은 형태의 NaverNews 객체로 다루기 위해 사용한다.
"""

from datetime import datetime


class NaverNews:
    """네이버 뉴스 API 응답과 DB 조회 결과를 담는 모델."""

    def __init__(
        self,
        id: int | None,
        title: str,
        originallink: str,
        link: str,
        description: str,
        pubDate: str,
        created_at: datetime | None = None,
    ):
        # id는 DB의 auto_increment 기본키이다.
        # API에서 막 받아온 데이터는 아직 DB에 저장되지 않았으므로 None을 사용한다.
        self.__id = id
        self.__title = title
        self.__originallink = originallink
        self.__link = link
        self.__description = description
        self.__pubDate = pubDate
        self.__created_at = created_at

    @classmethod
    def from_api_item(cls, item: dict) -> "NaverNews":
        """네이버 API item 딕셔너리를 NaverNews 객체로 변환한다."""

        # dict.get()을 사용하면 응답에 특정 key가 없더라도 빈 문자열로 안전하게 처리할 수 있다.
        return cls(
            id=None,
            title=item.get("title", ""),
            originallink=item.get("originallink", ""),
            link=item.get("link", ""),
            description=item.get("description", ""),
            pubDate=item.get("pubDate", ""),
        )

    @classmethod
    def from_db_row(cls, row: tuple) -> "NaverNews":
        """DB 조회 결과 튜플을 NaverNews 객체로 변환한다."""

        # select 컬럼 순서와 __init__ 파라미터 순서가 같기 때문에 언패킹을 사용할 수 있다.
        return cls(*row)

    # @property: 메서드를 변수처럼 사용할 수 있게하는 문법
    @property
    def id(self):
        return self.__id

    @property
    def title(self):
        return self.__title

    @property
    def originallink(self):
        return self.__originallink

    @property
    def link(self):
        return self.__link

    @property
    def description(self):
        return self.__description

    @property
    def pubDate(self):
        return self.__pubDate

    @property
    def created_at(self):
        return self.__created_at

    def to_db_params(self) -> tuple[str, str, str, str, str]:
        """insert SQL에 전달할 파라미터 튜플을 만든다."""

        return (
            self.title,
            self.originallink,
            self.link,
            self.description,
            self.pubDate,
        )

    def to_display_dict(self) -> dict:
        """Streamlit 표에 보여줄 딕셔너리를 만든다."""

        return {
            "id": self.id,
            "title": self.title,
            "originallink": self.originallink,
            "link": self.link,
            "description": self.description,
            "pubDate": self.pubDate,
            "created_at": self.created_at,
        }

    def __repr__(self):
        return (
            f"NaverNews({self.__id}, {self.__title}, {self.__originallink}, "
            f"{self.__link}, {self.__description}, {self.__pubDate}, {self.__created_at})"
        )
