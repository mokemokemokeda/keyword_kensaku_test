import time
import urllib.parse
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

# 明示的な待機を使用して要素が表示されるのを待つ
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'Tweet_TweetContainer'))
    )
except Exception:
    print("ツイートの取得に失敗しました。")
    driver.quit()
    exit()

# ツイート要素を取得
tweet_elements = driver.find_elements(By.CLASS_NAME, 'Tweet_TweetContainer')

# ツイートの文章を取得
tweet_texts = []
for tweet_element in tweet_elements:
    try:
        tweet_text = tweet_element.find_element(By.CLASS_NAME, 'Tweet_body').text
        tweet_texts.append(tweet_text)
    except Exception:
        continue

# 取得したツイートの数を表示
print(f'取得したツイート数: {len(tweet_texts)}')

# 取得したツイートの文章を表示
for idx, tweet in enumerate(tweet_texts, 1):
    print(f'{idx}: {tweet}')

# WebDriverを終了
driver.quit()
