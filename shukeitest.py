import time
import urllib.parse
import re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import json

# ===== Google認証周り（変更不要） =====
google_credentials_json = os.getenv("GOOGLE_SERVICE_ACCOUNT")
if not google_credentials_json:
    raise ValueError("GOOGLE_SERVICE_ACCOUNT が設定されていません。")
json_data = json.loads(google_credentials_json)
print("✅ Google Drive API の認証情報を取得しました！")

# ===== Selenium WebDriver のセットアップ =====
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

# ===== 検索キーワードとURL準備 =====
keyword = "ヨルクラ"
encoded_keyword = urllib.parse.quote(keyword)
search_url = f"https://search.yahoo.co.jp/realtime/search?p={encoded_keyword}"

driver.get(search_url)

# ページ読み込みの安定化のために待機
time.sleep(3)

# ツイートの投稿時間を過去6時間以内にフィルタリング
six_hours_ago = datetime.now() - timedelta(hours=6)

# WebDriverWait を使い、「件」という文字を含む要素が表示されるのを待つ
try:
    tweets = driver.find_elements(By.XPATH, "//*[@class='SearchResult-item']")  # ツイートを格納する要素を抽出
    tweet_count = 0

    for tweet in tweets:
        # ツイート時間を抽出
        time_element = tweet.find_element(By.XPATH, ".//time")  # 投稿時間を含む要素
        tweet_time = datetime.strptime(time_element.get_attribute("datetime"), "%Y-%m-%dT%H:%M:%S.%fZ")
        
        # もしツイートが過去6時間以内ならカウント
        if tweet_time > six_hours_ago:
            tweet_count += 1

    print(f"過去6時間以内に『{keyword}』を含むツイート数: {tweet_count} 件")
except Exception as e:
    print("ツイートの抽出に失敗しました:", e)

driver.quit()
