import os
import requests
from datetime import datetime, timedelta
import json

# Google認証情報（今回は直接利用しませんが、残してあります）
google_credentials_json = os.getenv("GOOGLE_SERVICE_ACCOUNT")
if not google_credentials_json:
    raise ValueError("GOOGLE_SERVICE_ACCOUNT が設定されていません。")
json_data = json.loads(google_credentials_json)
print("✅ Google Drive API の認証情報を取得しました！")

# Twitter API 認証
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
if not bearer_token:
    raise ValueError("TWITTER_BEARER_TOKEN が設定されていません。")
headers = {"Authorization": f"Bearer {bearer_token}"}

# 検索クエリと期間の設定
query = "ヨルクラ"

# end_time は現在時刻から10秒引いた値にする
end_time = datetime.utcnow() - timedelta(seconds=10)
start_time = end_time - timedelta(days=7)

# ISO8601形式の文字列に変換
start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

# Recent Tweet CountsエンドポイントURL
url = (
    "https://api.twitter.com/2/tweets/counts/recent"
    f"?query={query}&start_time={start_time_str}&end_time={end_time_str}&granularity=day"
)

response = requests.get(url, headers=headers)
if response.status_code != 200:
    raise Exception(f"Twitter API エラー: {response.status_code} {response.text}")

data = response.json()
total_count = sum([int(item["tweet_count"]) for item in data.get("data", [])])

print(f"過去1週間で『{query}』を含むツイート数: {total_count} 件")
