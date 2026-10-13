import os
import time
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

BASE_URL = "https://openapi.koreainvestment.com:9443"

APP_KEY = os.environ.get("KIS_APP_KEY")
APP_SECRET = os.environ.get("KIS_APP_SECRET")


def get_access_token():
    if not APP_KEY or not APP_SECRET:
        raise RuntimeError(
            "API 인증 정보가 서버에 설정되지 않았습니다."
        )

    response = requests.post(
        f"{BASE_URL}/oauth2/tokenP",
        json={
            "grant_type": "client_credentials",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET,
        },
        timeout=20,
    )

    response.raise_for_status()
    data = response.json()

    token = data.get("access_token")

    if not token:
        raise RuntimeError(
            "API 인증 실패: " + str(data.get("msg1", "응답 확인 필요"))
        )

    return token


def get_samsung_daily_price(token):
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    end_date = now.strftime("%Y%m%d")
    start_date = (now - timedelta(days=100)).strftime("%Y%m%d")

    response = requests.get(
        f"{BASE_URL}/uapi/domestic-stock/v1/quotations/"
        "inquire-daily-itemchartprice",
        headers={
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET,
            "tr_id": "FHKST03010100",
            "custtype": "P",
        },
        params={
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": "005930",
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date,
            "FID_PERIOD_DIV_CODE": "D",
            "FID_ORG_ADJ_PRC": "0",
        },
        timeout=20,
    )

    response.raise_for_status()
    data = response.json()

    if data.get("rt_cd") != "0":
        raise RuntimeError(
            "주가 조회 실패: " + str(data.get("msg1", "응답 확인 필요"))
        )

    prices = data.get("output2", [])

    if not prices:
        raise RuntimeError("조회된 주가 데이터가 없습니다.")

    latest = prices[0]

    print(
        "조회 성공 | "
        f"종목: 삼성전자(005930) | "
        f"거래일: {latest.get('stck_bsop_date')} | "
        f"종가: {latest.get('stck_clpr')}원"
    )


def main():
    print("자동매매 프로그램 시작")
    print("현재 단계: 실전 API 연결 및 시세 조회")
    print("실제 주문 기능: 비활성 상태")

    while True:
        try:
            token = get_access_token()
            get_samsung_daily_price(token)

        except Exception as exc:
            print(
                f"오류 발생: {type(exc).__name__}: {exc}"
            )

        time.sleep(3600)


if __name__ == "__main__":
    main()
