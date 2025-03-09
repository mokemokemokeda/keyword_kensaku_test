import time
import urllib.parse
import re
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

# Yahooリアルタイム検索のURLに「過去1週間」のフィルターを適用
search_url = f"https://search.yahoo.co.jp/realtime/search?p={encoded_keyword}&ei=UTF-8&rs=2"

driver.get(search_url)

# ページ読み込みの安定化のために待機
time.sleep(3)

# デバッグ用にページの一部を表示
print(driver.page_source[:1000])

# WebDriverWait を使い、「件」という文字を含む要素が表示されるのを待つ
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'件')]"))
    )
    count_text = element.text  # 例："約467件" など
    print(f"デバッグ: 取得した件数テキスト: {count_text}")
    # 正規表現で数字部分を抽出
    m = re.search(r'約?([\d,]+)件', count_text)
    if m:
        count = int(m.group(1).replace(',', ''))
        print(f"過去1週間で『{keyword}』を含むツイート数: {count} 件")
    else:
        print("件数の正規表現抽出に失敗しました。")
except Exception as e:
    print("件数の抽出に失敗しました:", e)

# ツイートを取得する関数
def get_tweets():
    tweet_texts = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        tweet_elements = driver.find_elements(By.CLASS_NAME, 'Tweet_TweetContainer__gC_9g')
        print(f"デバッグ: 取得したツイート要素の数: {len(tweet_elements)}")
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

# ツイートの取得
tweets = get_tweets()

# 取得したツイートの数を表示
print(f'取得したツイート数: {len(tweets)}')

# 取得したツイートの文章を表示
for idx, tweet in enumerate(tweets, 1):
    print(f'{idx}: {tweet}')

# WebDriverを終了
driver.quit()
