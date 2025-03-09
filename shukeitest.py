import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()

# Chromeのオプションを設定
CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument('--headless')  # ヘッドレスモードで動作

# Chrome WebDriverのインスタンスを作成
driver = webdriver.Chrome(options=CHROME_OPTIONS)

# 検索キーワード
keyword = 'ヨルクラ'
url_encoded_keyword = urllib.parse.quote(keyword)

# Yahooリアルタイム検索のページを開く
driver.get(f'https://search.yahoo.co.jp/realtime/search?p={url_encoded_keyword}')

# WebDriverWaitを使って、特定の要素が読み込まれるまで待機する
try:
    # 例：最大10秒待機して要素を探す
    tab_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'Tab_on__cXzYq'))
    )
    tab_element.click()
except Exception as e:
    print("指定の要素が見つかりませんでした:", e)

# 1秒の待機
time.sleep(1)

# ツイートの情報を取得するための関数
def extract_tweet_texts(tweet_elements):
    tweet_texts = []
    for tweet_element in tweet_elements:
        try:
            tweet_text_element = tweet_element.find_element(By.CLASS_NAME, 'Tweet_body__XtDoj')
            tweet_texts.append(tweet_text_element.text)
        except NoSuchElementException:
            continue
    return tweet_texts

def extract_tweet_records(tweet_elements):
    tweet_records = []
    for tweet_element in tweet_elements:
        try:
            tweet_record = {
                'tweet_text': extract_tweet_text(tweet_element),  # ツイートのテキスト
                'screen_name': extract_screen_name(tweet_element),  # ユーザー名
                'like': extract_like_count(tweet_element),  # いいね数
                'retweet': extract_retweet_count(tweet_element),  # リツイート数
            }
            tweet_records.append(tweet_record)
        except NoSuchElementException:
            continue
    return tweet_records

def extract_tweet_text(tweet_element):
    try:
        return tweet_element.find_element(By.CLASS_NAME, 'Tweet_body__XtDoj').text
    except NoSuchElementException:
        return None

def extract_screen_name(tweet_element):
    try:
        return tweet_element.find_element(By.CLASS_NAME, 'Tweet_authorID__B1U8c').text[1:]
    except NoSuchElementException:
        return None

def extract_like_count(tweet_element):
    try:
        return int(tweet_element.find_element(By.CLASS_NAME, 'Tweet_likeCount__DxLrt').text)
    except NoSuchElementException:
        return 0

def extract_retweet_count(tweet_element):
    try:
        return int(tweet_element.find_element(By.CLASS_NAME, 'Tweet_retweetCount__rVXfL').text)
    except NoSuchElementException:
        return 0

# ツイートの詳細情報を取得する関数
def extract_tweet_elements(driver, max_tweets=100):
    tweet_elements = driver.find_elements(By.CLASS_NAME, 'Tweet_TweetContainer__gC_9g')
    
    # もっと見るボタンをクリックする処理（任意）
    while len(tweet_elements) < max_tweets:
        try:
            show_more_button = driver.find_element(By.CLASS_NAME, 'More_More__rHgzp')
            show_more_button.click()
            time.sleep(1)
            tweet_elements = driver.find_elements(By.CLASS_NAME, 'Tweet_TweetContainer__gC_9g')
        except NoSuchElementException:
            break
    return tweet_elements[:max_tweets]

# ツイートを取得
tweet_elements = extract_tweet_elements(driver, max_tweets=100)

# ツイートのテキストを取得
tweet_texts = extract_tweet_texts(tweet_elements)

# ツイートの詳細情報を取得
tweet_records = extract_tweet_records(tweet_elements)

# 結果を表示
print(f"取得したツイート数: {len(tweet_records)}")
for record in tweet_records:
    print(f"ツイートテキスト: {record['tweet_text']}")
    print(f"ユーザー名: {record['screen_name']}")
    print(f"いいね数: {record['like']}")
    print(f"リツイート数: {record['retweet']}")
    print("="*30)

# 終了処理
driver.quit()
