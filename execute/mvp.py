import db.query_module as query_module
from db.db_module import Database
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
# import json
# import talib

# import pyupbit
# btc_info = pyupbit.get_ohlcv("KRW-BTC", count=30, interval="day")
# json_df = btc_info.to_json()
# dict_json = json.loads(json_df)['close']
# close_price = list(dict_json.values())
# close_date = list(dict_json.keys())
# data = {
#     'data': close_date,
#     'close': close_price
# }
# df = pd.DataFrame(data)

# 단순 이동 평균(SMA)
# df['SMA_3'] = df['close'].rolling(window=3).mean()

# 지수 이동 평균(EMA)
# df['EMA_3'] = df['close'].ewm(span=3, adjust=False).mean()

# RSI (Relative Strength Index)
# df['RSI'] = talib.RSI(df['close'], timeperiod=14)

# MACD (Moving Average Convergence Divergence)
# df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, singnalperiod=9)

# print(df)

# dict_type = json.loads(json_df)
# print(key_list)
# print(list(close_df.keys()))

# print(pyupbit.get_ohlcv("KRW-BTC", interval="minute1"))

def ai_trading():
  # 1. 업비트 차트 데이터 가져오기 (30일 일봉)
  import pyupbit
  import json
  access = os.getenv("UPBIT_ACCESS_KEY")
  secret = os.getenv("UPBIT_SECRET_KEY")
  upbit = pyupbit.Upbit(access, secret)
  # import pandas as pd

  # df = pyupbit.get_ohlcv("KRW-BTC", interval="minute1")
  btc_info = pyupbit.get_ohlcv("KRW-BTC", count=30, interval="day")
  # print(btc_info)
  # strData = str(df)
  # print(df.to_json())
  json_df = btc_info.to_json()
  dict_json = json.loads(json_df)['close']
  close_price = list(dict_json.values())
  close_date = list(dict_json.keys())
  data = {
      'data': close_date,
      'close': close_price
  }
  df = pd.DataFrame(data)

  # 단순 이동 평균(SMA)
  df['SMA_3'] = df['close'].rolling(window=3).mean()

  # 지수 이동 평균(EMA)
  df['EMA_3'] = df['close'].ewm(span=3, adjust=False).mean()

  pos_stgy = []
  query = '''
  SELECT DO
    FROM BTC_HIST
   WHERE DO != 'hold'
     AND STATUS = 'S'
   ORDER BY HIST_SEQ DESC
   LIMIT 1
  '''
  # result_do = (query_module.fetch_all_data(query))
  # if result_do and len(result_do[0]) > 0:
  #   if result_do[0][0] == 'sell':
  #     pos_stgy = ['buy', 'hold']
  #   else:
  #     pos_stgy = ['sell', 'hold']
  # else:
  #    print("No result found")

  my_krw = upbit.get_balance("KRW")
  my_btc = upbit.get_balance("KRW-BTC")
  strategy = {
      "strategy": {
        "price_data": json_df
      },
      "technical_indicators": df.to_json(),
      "asset": {
        "KRW": my_krw,
        "BITCOIN": my_btc
      }
  }
  # strategy = {
  #     "strategy": {
  #       "price_data": json_df
  #     },
  #     "technical_indicators": df.to_json(),
  #     "asset": {
  #       "KRW": my_krw,
  #       "BITCOIN": my_btc
  #     },
  #     "possible_strategy": {
  #        "possible_strategy": pos_stgy
  #     }
  # }
  # print(strategy)

  # 2. AI에게 데이터 제공하고 판단 받기
  from openai import OpenAI
  client = OpenAI()

  response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {
        "role": "system",
        "content": [
          {
            "type": "text",
            "text": "You are an expert in short-term Bitcoin investing. target: 'at least 1percent gain' Tell me whether to buy, sell, or hold at the moment based on the chart data provided. response in json format\n\nResponse Example:\n{\"decision\": \"buy\", \"reason\": \"some technical reason\"}\n{\"decision\": \"sell\", \"reason\": \"some technical reason\"}\n{\"decision\": \"hold\", \"reason\": \"some technical reason\"}"
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": json.dumps(strategy)
          }
        ]
      }
    ],
    # temperature=1,
    # max_tokens=255,
    # top_p=1,
    # frequency_penalty=0,
    # presence_penalty=0,
    response_format={
      "type": "json_object"
    }
  )
  result = response.choices[0].message.content

  # 3. AI의 판단에 따라 실제로 자동매매 진행하기
  import json
  result = json.loads(result)
  # import pyupbit
  # access = os.getenv("UPBIT_ACCESS_KEY")
  # secret = os.getenv("UPBIT_SECRET_KEY")
  # upbit = pyupbit.Upbit(access, secret)
  # decision = result["decision"]
  decision = 'buy'
  print("------------------------------------------------")
  print("------------   " + decision + "   ------------")
  print("-------------------------------------------------")

  query = """
  INSERT INTO BTC_HIST (
    DO, INFO, BTC_AMT, KRW_AMT, REASON, STATUS, FAIL_REASON
  ) VALUE (
    %s, %s, %s, %s, %s, %s, %s
  )
  """
  currency = ''
  amt = ''
  reason = result["reason"]
  status = 'F'
  fail_reason = ''
  if decision == "buy":
      # 매수
      my_krw = upbit.get_balance("KRW")
      if my_krw*0.9995 > 5000:
        print(upbit.buy_market_order("KRW-BTC", my_krw*0.9995))
        print("buy: ",reason)
        status = 'S'
      else:
        fail_reason = '실패: krw 5000원 미만'
        print(fail_reason)
  elif decision == "sell":
      # 매도
      my_btc = upbit.get_balance("KRW-BTC")
      current_price = pyupbit.get_orderbook(ticker="KRW-BTC")['orderbook_units'][0]["ask_price"]
      
      if (my_btc*current_price > 5000):
        print(upbit.sell_market_order("KRW-BTC", upbit.get_balance("KRW-BTC")))
        print("sell: ",reason)
        status = 'S'
      else:
        fail_reason = '실패: btc 5000원 미만'
        print(fail_reason)
  elif decision == "hold":
      # 지나감
      print(reason)
      status = 'S'
  
  my_krw = upbit.get_balance("KRW")
  my_btc = upbit.get_balance("KRW-BTC")
  clob_stgy = json.dumps(strategy)
  query_module.insert_data(query, (decision.upper(), clob_stgy, my_btc, my_krw, reason, status.upper(), fail_reason))
  print("-------------------------------------")
  print("------------   ",upbit.get_balance("KRW"))
  print("-------------------------------------")

while True:
  import time
  time.sleep(60)
  ai_trading()
