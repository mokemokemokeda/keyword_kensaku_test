import time
import urllib.parse
from datetime import datetime, timedelta
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
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
chrome_options.add_argument("--headless")  # ヘッドレスモード
driver = webdriver.Chrome(options=chrome_options)

# ===== 検索キーワードとURL準備 =====
keyword = "ヨルクラ"
encoded_keyword = urllib.parse.quote(keyword)
search_url = f"https://search.yahoo.co.jp/realtime/search?p={encoded_keyword}"

driver.get(search_url)
time.sleep(2)  # ページが完全に読み込まれるまで待機

# 自動更新停止のため、該当タブをクリック（存在すれば）
try:
    driver.find_element(By.CLASS_NAME, "Tab_on__cXzYq").click()
    time.sleep(1)
except NoSuchElementException:
    pass

# ===== ツイート時刻の解析関数 =====
def parse_tweet_time(text):
    """
    ツイート時刻のテキスト（例："5分前", "2時間前", "2023/04/01 12:34" など）を
    datetime オブジェクトに変換する。
    """
    try:
        if "前" in text:
            m = re.search(r"(\d+)", text)
            if m:
                num = int(m.group(1))
                if "秒前" in text:
                    dt = datetime.now() - timedelta(seconds=num)
                elif "分前" in text:
                    dt = datetime.now() - timedelta(minutes=num)
                elif "時間前" in text:
                    dt = datetime.now() - timedelta(hours=num)
                else:
                    dt = datetime.now()
                return dt
        else:
            dt = datetime.strptime(text, "%Y/%m/%d %H:%M")
            return dt
    except Exception:
        return None

def extract_tweet_date(tweet_element):
    """
    ツイート要素から時刻テキストを取得し、datetime オブジェクトに変換する。
    ※ Yahooリアルタイム検索のDOM構造に合わせ、クラス名 "Tweet_time__78Ddq" を利用。
    """
    try:
        time_text = tweet_element.find_element(By.CLASS_NAME, "Tweet_time__78Ddq").text
        return parse_tweet_time(time_text)
    except NoSuchElementException:
        return None

# ===== スクロール操作と「もっと見る」操作 =====
def scroll_to_elem(driver, elem):
    try:
        actions = ActionChains(driver)
        actions.move_to_element(elem)
        actions.perform()
        time.sleep(1)
        return True
    except (NoSuchElementException, StaleElementReferenceException):
        return False

def find_show_more_button(driver):
    try:
        return driver.find_element(By.CLASS_NAME, "More_More__rHgzp")
    except NoSuchElementException:
        return None

def click_show_more_button(driver):
    try:
        btn = find_show_more_button(driver)
        if btn:
            btn.click()
            time.sleep(1)
            return True
        return False
    except NoSuchElementException:
        return False

def extract_all_tweet_elements(driver, max_iterations=30):
    """
    「もっと見る」ボタンがなくなるか、max_iterations 回以上スクロールしたら終了する。
    """
    iterations = 0
    all_tweets = driver.find_elements(By.CLASS_NAME, "Tweet_TweetContainer__gC_9g")
    while iterations < max_iterations:
        btn = find_show_more_button(driver)
        if btn:
            click_show_more_button(driver)
            time.sleep(1)
            new_tweets = driver.find_elements(By.CLASS_NAME, "Tweet_TweetContainer__gC_9g")
            if len(new_tweets) > len(all_tweets):
                all_tweets = new_tweets
            else:
                break
        else:
            break
        iterations += 1
    return all_tweets

# ===== ツイート要素の取得 =====
tweet_elements = extract_all_tweet_elements(driver)
driver.quit()

# ===== 過去1週間以内のツイート数をカウント =====
one_week_ago = datetime.now() - timedelta(days=7)
count = 0
for tweet in tweet_elements:
    dt = extract_tweet_date(tweet)
    if dt and dt >= one_week_ago:
        count += 1

print(f"過去1週間で『{keyword}』を含むツイート数: {count} 件")
