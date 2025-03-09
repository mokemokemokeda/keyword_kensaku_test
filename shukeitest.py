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

# WebDriverWait を使い、「件」という文字を含む要素が表示されるのを待つ
try:
    # 最初の「14件」を表示
    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'件')]"))
    )
    count_text = element.text  # 例："約14件" など
    # 正規表現で数字部分を抽出
    m = re.search(r'約?([\d,]+)件', count_text)
    if m:
        count = int(m.group(1).replace(',', ''))
        print(f"最初のカウント：『{keyword}』を含むツイート数: {count} 件")
    else:
        print("件数の正規表現抽出に失敗しました。")

    # ツイート情報を表示（ツイート内容）
    tweets = driver.find_elements(By.XPATH, "//*[@id='bt']/div[2]/div/div/div[1]/p")  # ツイート部分のXPath

    print(f"ツイートの数: {len(tweets)} 件")

    for tweet in tweets:
        try:
            # ツイート内容を表示
            tweet_content = tweet.text
            print(f"ツイート内容: {tweet_content}")

            # 良いね数を取得
            try:
                like_count = tweet.find_element(By.XPATH, ".//following-sibling::div//span[contains(@class, 'sw-CardBase-like')]").text
                print(f"良いね数: {like_count}")
            except Exception as e:
                print("良いね数の取得に失敗しました:", e)

            # 投稿時間を取得
            try:
                time_element = tweet.find_element(By.XPATH, ".//preceding-sibling::time")
                tweet_time = datetime.strptime(time_element.get_attribute("datetime"), "%Y-%m-%dT%H:%M:%S.%fZ")
                print(f"投稿時間: {tweet_time}")
            except Exception as e:
                print("投稿時間の取得に失敗しました:", e)

        except Exception as e:
            print(f"ツイート情報の取得に失敗しました: {e}")

except Exception as e:
    print("ツイートの抽出に失敗しました:", e)

driver.quit()
