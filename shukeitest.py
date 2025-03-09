import time
import urllib.parse
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        EC.presence_of_element_located((By.CLASS_NAME, 'Tweet_TweetContainer__gC_9g'))
    )
except Exception:
    print("ツイートの取得に失敗しました。")
    driver.quit()
    exit()

# 過去6時間以内のツイートを取得するための時間範囲
now = datetime.now()
six_hours_ago = now - timedelta(hours=6)

tweet_elements = driver.find_elements(By.CLASS_NAME, 'Tweet_TweetContainer__gC_9g')

tweet_texts = []
for tweet_element in tweet_elements:
    try:
        tweet_time_element = tweet_element.find_element(By.CLASS_NAME, 'Tweet_time__78Ddq')
        tweet_text_element = tweet_element.find_element(By.CLASS_NAME, 'Tweet_body__XtDoj')
        
        tweet_time = tweet_time_element.text.strip()
        tweet_text = tweet_text_element.text.strip()
        
        tweet_texts.append(f'{tweet_time} - {tweet_text}')
    except Exception:
        continue

# 取得したツイートの数を表示
print(f'取得したツイート数: {len(tweet_texts)}')

# 取得したツイートの文章を表示
for idx, tweet in enumerate(tweet_texts, 1):
    print(f'{idx}: {tweet}')

# WebDriverを終了
driver.quit()
