import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import chromedriver_autoinstaller

# ChromeDriverの自動インストール
chromedriver_autoinstaller.install()

# Chromeのオプションを設定
CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument('--headless')  # ヘッドレスモードでブラウザを表示せずに動作

# Chrome WebDriverのインスタンスを作成
driver = webdriver.Chrome(options=CHROME_OPTIONS)

# 検索キーワード
keyword = '原神'

# URLエンコード
url_encoded_keyword = urllib.parse.quote(keyword)

# WebDriverでYahooリアルタイム検索のページを開く
driver.get(f'https://search.yahoo.co.jp/realtime/search?p={url_encoded_keyword}')
time.sleep(1)  # サーバー側の負荷を避けるために1秒待機

# 「Tab_on__cXzYq」クラスの要素をクリックして、タイムラインの自動更新を停止する
driver.find_element(By.CLASS_NAME, 'Tab_on__cXzYq').click()
time.sleep(1)

# ツイート情報を抽出する関数（詳細情報）
def extract_tweet_texts(tweet_elements):
    tweet_texts = []
    for tweet_element in tweet_elements:
        try:
            tweet_text_element = tweet_element.find_element(By.CLASS_NAME, 'Tweet_body__XtDoj')
            tweet_texts.append(tweet_text_element.text)
        except NoSuchElementException:
            continue
    return tweet_texts

# ツイート要素を取得
tweet_elements = driver.find_elements(By.CLASS_NAME, 'Tweet_TweetContainer__gC_9g')

# ツイートのテキストを取得
tweet_texts = extract_tweet_texts(tweet_elements)

# 取得したツイート数を表示
print(f"取得したツイート数: {len(tweet_texts)}")

# 以下、ツイート情報を取得するコードも記述
# ...

# ドライバを閉じる
driver.quit()
