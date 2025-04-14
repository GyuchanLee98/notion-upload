from bs4 import BeautifulSoup
from notion_client import Client
import os

# 📌 Notion API Key와 Database ID를 환경변수에서 불러오기
notion = Client(auth=os.environ["NOTION_API_KEY"])
database_id = os.environ["NOTION_DB_ID"]

# 1. 샘플 HTML 페이지 (가짜 .onion 시뮬레이션)
html = """
<html>
  <body>
    <h1>Credit card dumps</h1>
    <p>Visa, MasterCard leaked - fresh 2025-04</p>
    <p>Telegram: @darkdumpchannel</p>
  </body>
</html>
"""

soup = BeautifulSoup(html, 'html.parser')
text = soup.get_text().lower()

# 2. 위험 키워드 필터링
danger_keywords = ["credit card", "leaked", "telegram", "dump"]
found = [kw for kw in danger_keywords if kw in text]

# 3. 리포트 업로드 함수
def upload_report_to_notion(title, keywords):
    new_page = {
        "parent": {"database_id": database_id},
        "properties": {
            "제목": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            "상태": {
                "select": {
                    "name": "확인"
                }
            },
            "감지 키워드": {
                "rich_text": [
                    {
                        "text": {
                            "content": ", ".join(keywords)
                        }
                    }
                ]
            }
        }
    }

    notion.pages.create(**new_page)

# 4. 실행
if found:
    print(f"[!] 위험 키워드 감지됨: {found}")
    upload_report_to_notion("[다크웹 위협] 키워드 감지", found)
else:
    print("안전한 페이지입니다.")
