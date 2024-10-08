import db.query_module as query_module
from db.db_module import Database
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
load_dotenv()

class ChkAccTkn:

    # tkn 확인
    def chk_tkn():
        query = """
        SELECT exp_yn
          FROM API_KEY_MGT
         WHERE id = "KIS"
           AND exp_yn = 'N'
           AND exp_dt > DATE_SUB(NOW(), INTERVAL 1 MINUTE)
        """

        # query = """
        # SELECT *
        # FROM info_mgt
        # """
        tkn_rows = query_module.fetch_all_data(query)
        # print(len(tkn_rows))
        if len(tkn_rows) == 1:
            print("Y")
        else:
            get_acc_tkn()

    # print("Fetched data: ", rows)

# acc tkn 호출
kis_domain = "https://openapi.koreainvestment.com:9443"

# 1. KIS접근토큰 발행/폐기
# acctkn 유효기간 24시간(1일 1회 발급 원칙)
# 갱신발급주기 6시간(6시간 이내는 기존 발급키로 응답)
# 일정시간(1분) 이내에 재호출 시 에러
def get_acc_tkn():
    appkey = os.getenv("KIS_APP_KEY")
    secret = os.getenv("KIS_SECRET_KEY")
    url = "/oauth2/tokenP"
    # if flg == "N" else "/oauth2/revokeP"

    data = {
        "grant_type": "client_credentials",
        "appkey": appkey,
        "appsecret": secret
    }
    response = requests.post(kis_domain + url, json=data)
    print(response)
    if response.status_code == 200:
        try:
            json_data = response.json()
            print(json_data)
            key_val = json_data.get('access_token')
            exp_dt = datetime.strptime(json_data.get('access_token_token_expired'), '%Y-%m-%d %H:%M:%S')
            tkn_tp = json_data.get('token_type')
            upd_dt = datetime.now()
            query = f"""
            INSERT INTO API_KEY_MGT (
                id,
                key_val,
                tkn_tp,
                exp_dt,
                exp_yn
            ) VALUE (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            ON DUPLICATE KEY UPDATE
                key_val = %s,
                exp_dt = %s,
                exp_yn = %s,
                upd_dt = %s
            """
            query_module.insert_data(query, ('KIS', key_val, tkn_tp, exp_dt, 'N', key_val, exp_dt, 'N', upd_dt))
        except ValueError:
            print("JSON 형식의 응답이 아님:", response.text)
    else:
        print(f"서버 에러: {response.status_code}")
        print(response.text)


# def revoke_acc_tkn():


# query_module.insert_data(query, param)

