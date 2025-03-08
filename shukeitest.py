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
time.sleep(3)  # ページの読み込みを待つ

# 件数表示を取得する試み
count_text = None
# ① CSSセレクタで取得（従来の例）
try:
    count_element = driver.find_element(By.CSS_SELECTOR, ".resultCount")
    count_text = count_element.text  # 例："約467件"
except Exception as e:
    print("CSSセレクタ(.resultCount)では件数要素が見つかりませんでした。", e)

# ② XPathで「約」と「件」を含む要素を探索
if not count_text:
    print("XPathによる探索を試みます。")
    elements = driver.find_elements(By.XPATH, "//*[contains(text(),'約') and contains(text(),'件')]")
    for elem in elements:
        text = elem.text.strip()
        # 「約◯◯件」の形式かチェック
        m = re.search(r'約([\d,]+)件', text)
        if m:
            count_text = m.group(0)
            break

if count_text:
    m = re.search(r'約?([\d,]+)', count_text)
    if m:
        count_number = int(m.group(1).replace(',', ''))
        print(f"過去1週間で『{keyword}』を含むツイート数: {count_number} 件")
    else:
        print("件数の抽出に失敗しました: 数字パターンが一致しません。")
else:
    print("件数の抽出に失敗しました: 該当するテキスト要素が見つかりませんでした。")

driver.quit()
