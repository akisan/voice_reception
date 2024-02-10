from bs4 import BeautifulSoup, ResultSet, Tag
import datetime
import requests


# クラスにしてログイン状態を保持する
def get_events(account: str, password: str, uid: int) -> ResultSet[Tag]:
    with requests.Session() as s:
        s.post(
            "https://cybozu.systemd.co.jp/scripts/cb/ag.exe?",
            data={
                "_Account": account,
                "Password": password,
                "Submit": "ログイン",
                "_System": "login",
                "_Login": 1,
                "LoginMethod": 2,
                "csrf_ticket": "",
            },
        )

        today_date = datetime.date.today().strftime("%Y.%m.%d")
        resScheduleUserDay = s.get(
            f"https://cybozu.systemd.co.jp/scripts/cb/ag.exe?page=ScheduleUserDay&GID=1337&UID={uid}&Date=da.{today_date}"
        )
        print(resScheduleUserDay.url)
        soup = BeautifulSoup(resScheduleUserDay.text, "html.parser")
        bannerEvents = soup.select("a.bannerevent")
        events = soup.select("a.event")
        return bannerEvents + events
