from bs4 import BeautifulSoup

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

danger_keywords = ["credit card", "leaked", "telegram", "dump"]

found = [kw for kw in danger_keywords if kw in text]

if found:
    print(f"[!] 위험 키워드 감지됨: {found}")
else:
    print("안전한 페이지입니다.")
