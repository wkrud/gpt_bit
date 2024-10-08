import yfinance as yf
import json
import pyupbit
from openai import OpenAI
client = OpenAI()

# ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
def get_info():
    df = pyupbit.get_ohlcv("KRW-BTC", count=30, interval="day")
    # print(df.to_json())
    
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
            {
                "role": "system",
                "content": [
                {
                    "type": "text",
                    "text": "You are an expert in short-term Bitcoin investing. Tell me whether to buy, sell, or hold at the moment based on the chart data provided. response in json format\n\nResponse Example:\n{\"decision\": \"buy\", \"reason\": \"some technical reason\"}\n{\"decision\": \"sell\", \"reason\": \"some technical reason\"}\n{\"decision\": \"hold\", \"reason\": \"some technical reason\"}"
                }
                ]
            },
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": df.to_json()
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
    # print(response)
    result = response.choices[0].message.content
    result = json.loads(result)
    print(result)
