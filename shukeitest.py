import time
import urllib.parse
import re
from datetime import datetime, timedelta
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
search_url = f"https://search.yahoo.co.jp/realtime/search?p={encoded_keyword}"

driver.get(search_url)

# ページ読み込みの安定化のために待機
time.sleep(3)

# WebDriverWait を使い、「件」という文字を含む要素が表示されるのを待つ
try:
    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'件')]"))
    )
    count_text = element.text  # 例："約467件" など
    # 正規表現で数字部分を抽出
    m = re.search(r'約?([\d,]+)件', count_text)
    if m:
        count = int(m.group(1).replace(',', ''))
        print(f"過去1週間で『{keyword}』を含むツイート数: {count} 件")
    else:
        print("件数の正規表現抽出に失敗しました。")
except Exception as e:
    print("件数の抽出に失敗しました:", e)

driver.quit()
