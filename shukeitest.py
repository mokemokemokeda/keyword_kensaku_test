import time
import urllib.parse
import re
from datetime import datetime
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

# ページが完全に読み込まれるまで待機
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'件')]")))

# スクロールして全てのツイートを読み込む
for _ in range(5):  # スクロール回数を5回に設定
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # スクロール後に待機

# ツイート情報を表示（ツイート内容）
tweets = driver.find_elements(By.XPATH, "//div[contains(@class, 'card-content')]")

print(f"ツイートの数: {len(tweets)} 件")

for tweet in tweets:
    try:
        # ツイート内容を表示
        tweet_content = tweet.find_element(By.XPATH, ".//p").text  # ツイート内容を取得
        print(f"ツイート内容: {tweet_content}")

        # 良いね数を取得
        try:
            like_count = tweet.find_element(By.XPATH, ".//span[contains(@class, 'sw-CardBase-like')]").text
            print(f"良いね数: {like_count}")
        except Exception as e:
            print("良いね数の取得に失敗しました:", e)

        # 投稿時間を取得
        try:
            time_element = tweet.find_element(By.XPATH, ".//time")
            tweet_time = datetime.strptime(time_element.get_attribute("datetime"), "%Y-%m-%dT%H:%M:%S.%fZ")
            print(f"投稿時間: {tweet_time}")
        except Exception as e:
            print("投稿時間の取得に失敗しました:", e)

    except Exception as e:
        print(f"ツイート情報の取得に失敗しました: {e}")

driver.quit()
