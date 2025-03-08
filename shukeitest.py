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

# Chrome WebDriverのインスタンスを作成
driver = webdriver.Chrome(options=CHROME_OPTIONS)

# 検索キーワード
keyword = 'ヨルクラ'

# URLエンコード
url_encoded_keyword = urllib.parse.quote(keyword)

# WebDriverでYahooリアルタイム検索のページを開く
driver.get(f'https://search.yahoo.co.jp/realtime/search?p={url_encoded_keyword}')

time.sleep(3)  # ページの読み込みを待つ

# 明示的な待機を使用してツイート要素が表示されるのを待つ
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="Tweet"]'))
    )
except Exception:
    print("ツイートの取得に失敗しました。")
    driver.quit()
    exit()

# 過去6時間以内のツイートを取得するための時間範囲
now = datetime.now()
six_hours_ago = now - timedelta(hours=6)

# ツイート要素を取得
tweet_elements = driver.find_elements(By.CSS_SELECTOR, 'div[class*="Tweet"]')

# ツイートの文章のみを取得
tweet_texts = set()
for tweet_element in tweet_elements:
    try:
        tweet_text = tweet_element.text.strip()
        
        # ツイートが「ヨルクラ」を含むか確認
        if 'ヨルクラ' in tweet_text:
            # 日付と時間の抽出（簡易的なパターン）
            time_match = re.search(r'(\d{1,2}/\d{1,2} \d{1,2}:\d{1,2})', tweet_text)
            if time_match:
                tweet_time = time_match.group(1)
                tweet_texts.add(f'{tweet_time} - {tweet_text}')
    except Exception:
        continue

# 取得したツイートの数を表示
print(f'取得したツイート数: {len(tweet_texts)}')

# 取得したツイートの文章を表示
for idx, tweet in enumerate(tweet_texts, 1):
    print(f'{idx}: {tweet}')

# WebDriverを終了
driver.quit()
