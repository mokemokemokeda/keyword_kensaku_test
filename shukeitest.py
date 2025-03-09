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

# スクロールしながらツイートを取得する
def scroll_and_get_tweets():
    tweet_texts = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        tweet_elements = driver.find_elements(By.CLASS_NAME, 'Tweet_TweetContainer__gC_9g')
        for tweet_element in tweet_elements:
            try:
                tweet_text_element = tweet_element.find_element(By.CLASS_NAME, 'Tweet_body__XtDoj')
                tweet_text = tweet_text_element.text.strip()
                if tweet_text and 'ヨルクラ' in tweet_text:
                    tweet_texts.append(tweet_text)
            except Exception:
                continue
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return list(set(tweet_texts))

# ツイートを取得
tweets = scroll_and_get_tweets()

# 取得したツイートの数を表示
print(f'取得したツイート数: {len(tweets)}')

# 取得したツイートの文章を表示
for idx, tweet in enumerate(tweets, 1):
    print(f'{idx}: {tweet}')

# WebDriverを終了
driver.quit()
