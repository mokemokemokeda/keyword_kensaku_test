import time
import urllib.parse
import re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
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
search_url = f"https://search.yahoo.co.jp/realtime/search?p={encoded_keyword}"

driver.get(search_url)
time.sleep(3)  # ページ読み込み待機

# ※ ページ上部に「約467件」などの件数表示がある場合、その要素を取得する
# 例として、クラス名 "resultCount" の要素に件数が入っているケースを想定
try:
    count_element = driver.find_element(By.CSS_SELECTOR, ".resultCount")
    count_text = count_element.text  # 例："約467件"
    # 数字部分を抽出
    m = re.search(r'約?([\d,]+)', count_text)
    if m:
        count_str = m.group(1).replace(',', '')
        count = int(count_str)
    else:
        count = 0
    print(f"過去1週間で『{keyword}』を含むツイート数: {count} 件")
except Exception as e:
    print("件数の抽出に失敗しました:", e)

driver.quit()
