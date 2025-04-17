from bs4 import BeautifulSoup
from notion_client import Client
from datetime import datetime
import os
import csv

# Notion 설정
notion = Client(auth=os.environ["NOTION_API_KEY"])
database_id = os.environ["NOTION_DB_ID"]

# 키워드 및 가이드 설정
DANGER_KEYWORDS = ["telegram", "ssn", "dump", "leak"]
RESPONSE_GUIDE = {
    "telegram": "텔레그램 채널 조사 및 신고 조치",
    "ssn": "신원정보 유출 가능성, 고객 데이터 샘플 대조 필요",
    "dump": "데이터 판매 정황, 샘플 수집/조사 권고",
    "leak": "고객 이메일 누출 가능성, 매칭 필요",
}

def generate_risk_level(keywords):
    if "ssn" in keywords or "dump" in keywords:
        return "높음"
    elif "leak" in keywords:
        return "중간"
    else:
        return "낮음"

def generate_response_guide(keywords):
    return [RESPONSE_GUIDE[kw] for kw in keywords if kw in RESPONSE_GUIDE]

def save_csv_report(keywords, risk_level, guide, filename="report.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["감지 키워드", "위험도", "대응 가이드"])
        writer.writerow([", ".join(keywords), risk_level, " / ".join(guide)])

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
"{content}"

---

### 🚨 대응 가이드
"""
    for line in guide:
        markdown += f"- {line}\n"
    markdown += "\n---"
    return markdown, risk, guide

def fetch_html_sample():
    return """<html><body>SSN dump on Telegram</body></html>"""

def extract_keywords(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text().lower()
    found = [kw for kw in DANGER_KEYWORDS if kw in text]
    return found, text

def upload_to_notion(keywords, risk, guide):
    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "제목": {"title": [{"text": {"content": f"[다크웹] 위험 리포트 {datetime.now().strftime('%Y-%m-%d')}"}}]},
            "상태": {"select": {"name": "확인"}},
            "위험도": {"select": {"name": risk}},
            "감지 키워드": {"rich_text": [{"text": {"content": ', '.join(keywords)}}]},
            "대응 가이드": {"rich_text": [{"text": {"content": '\n'.join(guide)}}]},
            "CSV 리포트 링크": {"url": "https://raw.githubusercontent.com/yourname/yourrepo/main/report.csv"}
        }
    )

def main():
    html = fetch_html_sample()
    keywords, text = extract_keywords(html)
    if keywords:
        print(f"[!] 감지된 키워드: {keywords}")
        _, risk, guide = generate_markdown_report(keywords, text)
        save_csv_report(keywords, risk, guide)
        upload_to_notion(keywords, risk, guide)
    else:
        print("안전한 페이지입니다.")

if __name__ == "__main__":
    main()