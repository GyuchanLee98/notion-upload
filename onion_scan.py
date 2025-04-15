from bs4 import BeautifulSoup
from notion_client import Client
from datetime import datetime
import os

# Notion 설정
notion = Client(auth=os.environ["NOTION_API_KEY"])
database_id = os.environ["NOTION_DB_ID"]

# 감지 키워드 필터링
DANGER_KEYWORDS = ["telegram", "ssn", "dump", "leak"]

# 대응 가이드 매핑
RESPONSE_GUIDE = {
    "telegram": "텔레그램 채널 조사 및 신고 조치",
    "ssn": "신원정보 유출 가능성, 고객 데이터 샘플 대조 필요",
    "dump": "데이터 판매 정황, 샘플 수집/조사 권고",
    "leak": "고객 이메일 누출 가능성, 매칭 필요",
}

# 위험도 산정
def generate_risk_level(keywords):
    if "ssn" in keywords or "dump" in keywords:
        return "높음"
    elif "leak" in keywords:
        return "중간"
    else:
        return "낮음"

# 대응 가이드 생성
def generate_response_guide(keywords):
    return [RESPONSE_GUIDE[kw] for kw in keywords if kw in RESPONSE_GUIDE]

# Markdown 리포트 생성
def generate_markdown_report(keywords, content):
    date = datetime.now().strftime("%Y-%m-%d")
    risk = generate_risk_level(keywords)
    guide = generate_response_guide(keywords)

    markdown = f"""## 📄 다크웹 위협 리포트

- 생성일: {date}
- 감지된 키워드: {', '.join(keywords)}
- 위험도: **{risk}**

---

### 🔎 감지된 내용 요약
\"{content}\"

---

### 🚨 대응 가이드
"""
    for line in guide:
        markdown += f"- {line}\n"
    markdown += "\n---"
    return markdown, risk, guide

# 샘플 HTML
html = """
<html>
  <body>
    <h1>Fresh SSN dumps for sale</h1>
    <p>Available on Telegram. Instant delivery.</p>
  </body>
</html>
"""

# 파싱 + 감지
soup = BeautifulSoup(html, 'html.parser')
text = soup.get_text().lower()
found = [kw for kw in DANGER_KEYWORDS if kw in text]

if found:
    print(f"[!] 위험 키워드 감지됨: {found}")
    report_md, risk_level, guide_list = generate_markdown_report(found, text)

    # Notion 업로드
    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "제목": {
                "title": [
                    {"text": {"content": f"[다크웹] 위험 감지 리포트 {datetime.now().strftime('%m/%d')}" }}
                ]
            },
            "상태": {"select": {"name": "확인"}},
            "위험도": {"select": {"name": risk_level}},
            "감지 키워드": {"rich_text": [{"text": {"content": ', '.join(found)}}]},
            "대응 가이드": {"rich_text": [{"text": {"content": '\n'.join(guide_list)}}]},
        }
    )
else:
    print("안전한 페이지입니다.")
