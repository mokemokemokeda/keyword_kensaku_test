import time
import urllib.parse
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

# Chromeのオプションを設定
CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument('--headless')  # ヘッドレスモードでブラウザを表示せずに動作
CHROME_OPTIONS.add_argument('--no-sandbox')
CHROME_OPTIONS.add_argument('--disable-dev-shm-usage')

# Chrome WebDriverのインスタンスを作成
driver = webdriver.Chrome(options=CHROME_OPTIONS)

# 検索キーワード
keyword = 'ヨルクラ'

# URLエンコード
url_encoded_keyword = urllib.parse.quote(keyword)

# WebDriverでYahooリアルタイム検索のページを開く
driver.get(f'https://search.yahoo.co.jp/realtime/search?p={url_encoded_keyword}')

time.sleep(5)  # ページの完全な読み込みを待つ

# 明示的な待機を使用してツイート要素が表示されるのを待つ
try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'li[class*="StreamItem"]'))
    )
except Exception:
    print("ツイートの取得に失敗しました。")
    driver.quit()
    exit()

# 過去6時間以内のツイートを取得するための時間範囲
now = datetime.now()
six_hours_ago = now - timedelta(hours=6)

# ツイート要素を取得
tweet_elements = driver.find_elements(By.CSS_SELECTOR, 'li[class*="StreamItem"]')

tweet_texts = []
for tweet_element in tweet_elements:
    try:
        tweet_time_element = tweet_element.find_element(By.CSS_SELECTOR, 'time')
        tweet_text_element = tweet_element.find_element(By.CSS_SELECTOR, 'div[class*="Tweet_body"]')
        
        tweet_time_str = tweet_time_element.get_attribute('datetime')
        tweet_text = tweet_text_element.text.strip()
        
        # 取得した時間を適切な形式に変換
        tweet_time = datetime.strptime(tweet_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        
        # 6時間以内のツイートのみを取得
        if tweet_time >= six_hours_ago:
            tweet_texts.append(f'{tweet_time.strftime("%Y-%m-%d %H:%M")} - {tweet_text}')
    except Exception:
        continue

# 取得したツイートの数を表示
print(f'取得したツイート数: {len(tweet_texts)}')

# 取得したツイートの文章を表示
for idx, tweet in enumerate(tweet_texts, 1):
    print(f'{idx}: {tweet}')

# WebDriverを終了
driver.quit()
