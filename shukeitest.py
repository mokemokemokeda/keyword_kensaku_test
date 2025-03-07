import time
import xlsxwriter
import pandas as pd
import urllib.parse
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import json

# 環境変数からサービスアカウントキーを取得
google_credentials_json = os.getenv("GOOGLE_SERVICE_ACCOUNT")
if not google_credentials_json:
    raise ValueError("GOOGLE_SERVICE_ACCOUNT が設定されていません。")
json_data = json.loads(google_credentials_json)

# Google Drive API 認証
credentials = service_account.Credentials.from_service_account_info(json_data)
drive_service = build("drive", "v3", credentials=credentials)
print("✅ Google Drive API の認証が完了しました！")

# Chromeのオプションを設定
CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument('--headless')  # ヘッドレスモードでブラウザを表示せずに動作

# Chrome WebDriverのインスタンスを作成
driver = webdriver.Chrome(options=CHROME_OPTIONS)

# 検索キーワード
keyword = 'プリオケ'

# URLエンコード
url_encoded_keyword = urllib.parse.quote(keyword)

# WebDriverでYahooリアルタイム検索のページを開く
driver.get(f'https://search.yahoo.co.jp/realtime/search?p={url_encoded_keyword}')
time.sleep(1)  # サーバー側の負荷を避けるために1秒待機

# 「Tab_on__cXzYq」クラスの要素をクリックして、タイムラインの自動更新を停止する
driver.find_element(By.CLASS_NAME, 'Tab_on__cXzYq').click()
time.sleep(1)

from selenium.common.exceptions import NoSuchElementException

def extract_tweet_texts(tweet_elements):
    '''
    ツイートのテキストを取得する
    '''
    tweet_texts = []
    for tweet_element in tweet_elements:
        try:
            # ツイートのテキスト要素を取得
            tweet_text_element = tweet_element.find_element(By.CLASS_NAME, 'Tweet_body__XtDoj')
            tweet_texts.append(tweet_text_element.text)
        except NoSuchElementException:
            continue
    return tweet_texts

# ツイートコンテナ要素を取得
tweet_elements = driver.find_elements(By.CLASS_NAME, 'Tweet_TweetContainer__gC_9g')

# ツイートのテキストを取得
tweet_texts = extract_tweet_texts(tweet_elements)

print("取得したツイート数: ", len(tweet_texts))

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

def scroll_to_elem(driver, elem):
    '''
    指定された要素までスクロールする
    '''
    try:
        actions = ActionChains(driver)
        actions.move_to_element(elem)
        actions.perform()
        time.sleep(1)
        return True
    except (NoSuchElementException, StaleElementReferenceException):
        return False

def find_show_more_button(driver):
    '''
    もっと見るボタンを取得する
    '''
    try:
        return driver.find_element(By.CLASS_NAME, 'More_More__rHgzp')
    except NoSuchElementException:
        return None

def click_show_more_button(driver):
    '''
    もっと見るボタンをクリックする
    '''
    try:
        find_show_more_button(driver).click()
        time.sleep(1)
        return True
    except NoSuchElementException:
        return False

def extract_tweet_elements(driver, max_tweets=100):
    '''
    ツイート要素を取得する
    '''
    # "もっと見る"ボタンをクリックして追加のツイートを取得
    while True:
        # ツイートコンテナ要素を取得
        tweet_elements = driver.find_elements(By.CLASS_NAME, 'Tweet_TweetContainer__gC_9g')
        
        # 取得ツイート数が指定された数に達するか、もっと見るボタンがない場合は終了
        if len(tweet_elements) >= max_tweets or not find_show_more_button(driver):
            break
        
        # もっと見るボタンをクリック
        click_show_more_button(driver)
        
        # 指定回数スクロール（次のもっと見るボタンが出てくるまで）
        while True:
            # もっと見るボタンを取得
            show_more_button_element = find_show_more_button(driver)
            
            # もっと見るボタンまでスクロール
            scroll_to_elem(driver, show_more_button_element)
            
            # もっと見るボタンがないか、もっと見るボタンまでスクロール出来たら終了
            if not find_show_more_button(driver) or show_more_button_element == find_show_more_button(driver):
                break
    
    return tweet_elements[:max_tweets]

# ツイートを取得
tweet_elements = extract_tweet_elements(driver, max_tweets=100)

# ツイートのテキストを取得
tweet_texts = extract_tweet_texts(tweet_elements)
print("取得したツイート数: ", len(tweet_texts))

import re
from datetime import timedelta, datetime

def extract_tweet_records(tweet_elements):
    '''
    ツイートの情報を取得する
    '''
    tweet_records = []
    
    for tweet_element in tweet_elements:
        cl_params = extract_client_params(tweet_element)
        tweet_id = cl_params.get('twid')
        user_id = cl_params.get('twuid')
        
        try:
            tweet_record = {
                'tweet_id': tweet_id, # ツイートID
                'tweet_text': extract_tweet_text(tweet_element), # ツイートのテキスト
                'user_id': user_id, # ユーザーID
                'screen_name': extract_screen_name(tweet_element), # ユーザー名
                'account_name': extract_account_name(tweet_element), # アカウント名
                'tweet_date': extract_tweet_date(tweet_element), # ツイート日時
                'like': int(cl_params.get('like')), # いいね数
                'quote': int(cl_params.get('quote')), # 引用数
                'reply': int(cl_params.get('reply')), # リプライ数
                'retweet': int(cl_params.get('retweet')), # リツイート数
            }
            tweet_records.append(tweet_record)
        except NoSuchElementException:
            continue
    return tweet_records

def extract_tweet_text(tweet_container_elem):
    '''
    ツイート本文を取得する。
    '''
    try:
        return tweet_container_elem.find_element(By.CLASS_NAME, 'Tweet_body__XtDoj').text
    except NoSuchElementException:
        return None

def extract_screen_name(tweet_container_element):
    '''
    スクリーンネームを取得する。
    '''
    try:
        return tweet_container_element.find_element(By.CLASS_NAME, 'Tweet_authorID__B1U8c').text[1:]
    except NoSuchElementException:
        return None
    
def extract_account_name(tweet_container_element):
    '''
    アカウント名を取得する。
    '''
    try:
        return tweet_container_element.find_element(By.CLASS_NAME, 'Tweet_authorName__V3waK').text
    except NoSuchElementException:
        return None

def extract_tweet_date(tweet_container_element):
    '''
    ツイート日時を取得する。
    '''
    try:
        tweet_time = tweet_container_element.find_element(By.CLASS_NAME, 'Tweet_time__78Ddq').text
        return format_tweet_time(text=tweet_time)
    except NoSuchElementException:
        return None

def extract_client_params(tweet_container_element):
    '''
    data-cl-params属性を取得する。
    '''
    try:
        # data-cl-params属性を取得
        tweet_time_element = tweet_container_element.find_element(By.CLASS_NAME, 'Tweet_time__78Ddq a')
        client_params_str = tweet_time_element.get_attribute('data-cl-params')
        
        # セミコロンで区切られたペアをリストに分解
        pairs = client_params_str.split(';')
        
        # 辞書型に変換
        cl_params_dict = {}
        for pair in pairs:
            if ':' in pair:
                key, value = pair.split(':', 1)  # keyとvalueをコロンで分割
                cl_params_dict[key] = value
        
        return cl_params_dict
    except NoSuchElementException:
        return None

def format_tweet_time(text: str, date_format='%Y-%m-%d %H:%M:%S') -> str:
    '''
    ツイート時間を整形する。
    '''
    # ツイート時間が「2020年1月1日」などの形式の場合はそのまま返す
    if extracted_datetime := extract_datetime_from_text(text):
        return extracted_datetime.strftime(date_format)
    
    # ツイート時間が「1分前」などの場合は現在時刻から計算
    current_time_string = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())
    specified_datetime = calculate_time_difference(current_time_string, text)
    return specified_datetime.strftime(date_format)

def extract_datetime_from_text(date_str: str) -> datetime:
    '''
    指定された文字列から日付を抽出する。
    '''
    # 日付を抽出するための正規表現パターン
    datetime_pattern = r"(\d{1,2})月(\d{1,2})日\([月火水木金土日]\) (\d{1,2}):(\d{1,2})"
    date_pattern = r"(\d{4})年(\d{1,2})月(\d{1,2})日"
    
    # 時刻を含むパターンを検索
    if match := re.search(datetime_pattern, date_str):
        month, day, hour, minute = map(int, match.groups())
        current_time = datetime.now()
        specified_datetime = datetime(current_time.year, month, day, hour, minute)
        return specified_datetime
    
    # 日付のみのパターンを検索
    if match := re.search(date_pattern, date_str):
        year, month, day = map(int, match.groups())
        current_time = datetime.now()
        specified_datetime = datetime(year, month, day)
        return specified_datetime
    
    # マッチしない場合は None を返す
    return None

def calculate_time_difference(current_time_string: str, time_difference_string: str) -> datetime:
    '''
    指定された時間と現在時刻の差分を計算する。
    '''
    # 現在時刻の文字列をdatetimeオブジェクトに変換
    current_time = datetime.strptime(current_time_string, '%Y/%m/%d %H:%M:%S')

    # 差分のタイプに応じて処理を行う
    if '秒前' in time_difference_string:
        # 秒数の差分を計算
        time_difference = int(time_difference_string.split('秒前')[0])
        time_delta = timedelta(seconds=time_difference)
    elif '分前' in time_difference_string:
        # 分数の差分を計算
        time_difference = int(time_difference_string.split('分前')[0])
        time_delta = timedelta(minutes=time_difference)
    elif '時間前' in time_difference_string:
        # 時間数の差分を計算
        time_difference = int(time_difference_string.split('時間前')[0])
        time_delta = timedelta(hours=time_difference)
    elif '昨日' in time_difference_string:
        # 「昨日」の日付と指定された時間の差分を計算
        time_parts = time_difference_string.split('昨日 ')[1].split(':')
        hour, minute = map(int, time_parts)
        yesterday = current_time - timedelta(days=1)
        specified_datetime = datetime(yesterday.year, yesterday.month, yesterday.day, hour, minute)
        return specified_datetime
    else:
        # 指定された時間を計算
        hour, minute = map(int, time_difference_string.split(':'))
        specified_time = datetime(current_time.year, current_time.month, current_time.day, hour, minute)
        return specified_time

    # 差分を計算して結果を返す
    specified_datetime = current_time - time_delta
    return specified_datetime

# ツイートを取得
tweet_elements = extract_tweet_elements(driver, max_tweets=100)

# ツイートの情報を取得
tweet_records = extract_tweet_records(tweet_elements)
print("取得したツイート数: ", len(tweet_texts))
