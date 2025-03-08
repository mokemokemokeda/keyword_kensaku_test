import time
import xlsxwriter
import pandas as pd
import urllib.parse
import io
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import os
import json
import re

# -----------------------------
# ① キーワード設定とURL準備
# -----------------------------
keyword = "プリオケ"
encoded_keyword = urllib.parse.quote(keyword)
search_url = f"https://search.yahoo.co.jp/realtime/search?p={encoded_keyword}"

# -----------------------------
# ② Selenium WebDriver のセットアップ（ヘッドレスモード）
# -----------------------------
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

# -----------------------------
# ③ Yahooリアルタイム検索ページを開く
# -----------------------------
driver.get(search_url)
time.sleep(1)  # ページ読み込み待機

# 自動更新を停止するため、特定のタブ（クラス名 "Tab_on__cXzYq"）をクリック
try:
    driver.find_element(By.CLASS_NAME, "Tab_on__cXzYq").click()
    time.sleep(1)
except NoSuchElementException:
    pass

# -----------------------------
# ④ スクロールや「もっと見る」ボタンを操作する関数群
# -----------------------------
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

def extract_tweet_elements(driver, max_tweets=100):
    """
    ツイートコンテナ要素（最大 max_tweets 件）を取得する
    """
    while True:
        tweet_elements = driver.find_elements(By.CLASS_NAME, "Tweet_TweetContainer__gC_9g")
        # 取得件数が十分または「もっと見る」ボタンがなければ終了
        if len(tweet_elements) >= max_tweets or not find_show_more_button(driver):
            break
        click_show_more_button(driver)
        # 「もっと見る」ボタンまでスクロールして更新を促す
        while True:
            show_more = find_show_more_button(driver)
            if show_more:
                scroll_to_elem(driver, show_more)
                # もしボタンが同じならループ終了
                if show_more == find_show_more_button(driver):
                    break
            else:
                break
    # 再度全件取得して、最大件数を返す
    tweet_elements = driver.find_elements(By.CLASS_NAME, "Tweet_TweetContainer__gC_9g")
    return tweet_elements[:max_tweets]

# -----------------------------
# ⑤ 各ツイートから情報を抽出する関数群
# -----------------------------
def extract_tweet_text(tweet_container_elem):
    try:
        return tweet_container_elem.find_element(By.CLASS_NAME, "Tweet_body__XtDoj").text
    except NoSuchElementException:
        return None

def extract_screen_name(tweet_container_elem):
    try:
        text = tweet_container_elem.find_element(By.CLASS_NAME, "Tweet_authorID__B1U8c").text
        return text[1:] if text.startswith("@") else text
    except NoSuchElementException:
        return None

def extract_account_name(tweet_container_elem):
    try:
        return tweet_container_elem.find_element(By.CLASS_NAME, "Tweet_authorName__V3waK").text
    except NoSuchElementException:
        return None

def extract_tweet_date(tweet_container_elem):
    try:
        tweet_time = tweet_container_elem.find_element(By.CLASS_NAME, "Tweet_time__78Ddq").text
        return format_tweet_time(tweet_time)
    except NoSuchElementException:
        return None

def extract_client_params(tweet_container_elem):
    """
    ツイートに埋め込まれたカスタムパラメータ（いいね数、リツイート数など）を抽出する。
    ※ Yahooリアルタイム検索上のDOM構造に合わせた実装例です。
    """
    try:
        # data-cl-params属性が格納されているリンク要素を対象とする
        tweet_time_elem = tweet_container_elem.find_element(By.CSS_SELECTOR, ".Tweet_time__78Ddq a")
        params_str = tweet_time_elem.get_attribute("data-cl-params")
        pairs = params_str.split(";")
        params = {}
        for pair in pairs:
            if ":" in pair:
                key, value = pair.split(":", 1)
                params[key] = value
        return params
    except NoSuchElementException:
        return {}

def format_tweet_time(text):
    """
    ツイートの時間表示（例："1分前", "2時間前", "2020/12/31 23:59" など）を
    "YYYY-MM-DD HH:MM:SS" 形式に変換する（簡易実装）
    """
    try:
        if "前" in text:
            # 数字を抽出して、秒、分、または時間を計算
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
                return dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            # 直接日時としてパース（例："2020/12/31 23:59"）
            dt = datetime.strptime(text, "%Y/%m/%d %H:%M")
            return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return text

def extract_tweet_records(tweet_elements):
    """
    ツイート要素リストから、必要な情報を辞書型で抽出し、リストとして返す
    """
    records = []
    for elem in tweet_elements:
        try:
            params = extract_client_params(elem)
            record = {
                "tweet_text": extract_tweet_text(elem),
                "screen_name": extract_screen_name(elem),
                "account_name": extract_account_name(elem),
                "tweet_date": extract_tweet_date(elem),
                # 数値変換ができなければ0とする
                "like": int(params.get("like", 0)),
                "quote": int(params.get("quote", 0)),
                "reply": int(params.get("reply", 0)),
                "retweet": int(params.get("retweet", 0)),
            }
            records.append(record)
        except Exception:
            continue
    return records

# -----------------------------
# ⑥ ツイート情報の取得と保存処理
# -----------------------------
# ツイート要素を最大100件取得
tweet_elements = extract_tweet_elements(driver, max_tweets=100)

# ツイート情報（辞書のリスト）を抽出
tweet_records = extract_tweet_records(tweet_elements)
print("取得したツイート数: ", len(tweet_records))

# ブラウザを閉じる
driver.quit()

# DataFrameに変換
df_tweets = pd.DataFrame(tweet_records)
print(df_tweets.head())

# CSVファイルに保存（後々Googleスプレッドシート連携も可能）
output_filename = "yahoo_tweets.csv"
df_tweets.to_csv(output_filename, index=False, encoding="utf-8-sig")
print(f"ツイート情報を {output_filename} に保存しました！")
