"""서울 상권분석서비스 API에서 제과점 업종 데이터를 수집해 CSV로 저장."""
import csv, json, sys, urllib.request
from pathlib import Path

BASE = Path(__file__).parent
KEY = next(l.split("=", 1)[1].strip() for l in (BASE / ".env").read_text().splitlines() if l.startswith("SEOUL_API_KEY"))
INDUSTRY = "제과점"
QUARTERS = sys.argv[1:] or ["20254", "20244"]


def fetch(service, quarter):
    rows, start = [], 1
    while True:
        url = f"http://openapi.seoul.go.kr:8088/{KEY}/json/{service}/{start}/{start+999}/{quarter}"
        data = json.load(urllib.request.urlopen(url, timeout=60))[service]
        rows += data.get("row", [])
        if start + 999 >= data["list_total_count"]:
            return rows
        start += 1000


for service, tag in [("VwsmTrdarSelngQq", "sales"), ("VwsmTrdarStorQq", "stores")]:
    for q in QUARTERS:
        rows = [r for r in fetch(service, q) if r["SVC_INDUTY_CD_NM"] == INDUSTRY]
        out = BASE / f"bakery_{tag}_{q}.csv"
        if rows:
            with out.open("w", newline="", encoding="utf-8-sig") as f:
                w = csv.DictWriter(f, fieldnames=rows[0].keys())
                w.writeheader(); w.writerows(rows)
        print(service, q, len(rows), "rows ->", out.name)
