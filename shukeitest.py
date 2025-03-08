import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

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
time.sleep(2)  # サーバー側の負荷を避けるために待機

# ツイート要素を取得
tweet_elements = driver.find_elements(By.CLASS_NAME, 'Tweet_TweetContainer__gC_9g')

# ツイートの文章を取得
tweet_texts = []
for tweet_element in tweet_elements:
    try:
        tweet_text = tweet_element.find_element(By.CLASS_NAME, 'Tweet_body__XtDoj').text
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
