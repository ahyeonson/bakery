"""3년 뒤 성장 상권 분석용 데이터 수집 (서울시 상권분석서비스 Open API)."""
import csv, json, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = Path(__file__).parent
OUT = BASE / "data"; OUT.mkdir(exist_ok=True)
KEY = next(l.split("=", 1)[1].strip() for l in (BASE / ".env").read_text().splitlines() if l.startswith("SEOUL_API_KEY"))
QS = ["20254", "20244", "20234"]
INDS = {"제과점", "커피-음료"}


def call(service, start, end, extra=""):
    url = f"http://openapi.seoul.go.kr:8088/{KEY}/json/{service}/{start}/{end}/{extra}"
    for _ in range(3):
        try:
            return json.load(urllib.request.urlopen(url, timeout=60))[service]
        except Exception:
            pass
    raise RuntimeError(url)


def fetch(service, extra="", keep=lambda r: True):
    first = call(service, 1, 1000, extra)
    total = first["list_total_count"]
    starts = range(1001, total + 1, 1000)
    with ThreadPoolExecutor(6) as ex:
        pages = list(ex.map(lambda s: call(service, s, s + 999, extra).get("row", []), starts))
    rows = first.get("row", []) + [r for p in pages for r in p]
    return [r for r in rows if keep(r)]


def save(rows, name):
    if not rows:
        print(name, "0 rows"); return
    with (OUT / name).open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    print(name, len(rows), flush=True)


for q in QS:
    save(fetch("VwsmTrdarSelngQq", q, lambda r: r["SVC_INDUTY_CD_NM"] in INDS), f"sales_{q}.csv")
    save(fetch("VwsmTrdarStorQq", q, lambda r: r["SVC_INDUTY_CD_NM"] in INDS), f"stores_{q}.csv")
    save(fetch("VwsmTrdarFlpopQq", q), f"flpop_{q}.csv")
slim = lambda r: {k: r[k] for k in ("STDR_YYQU_CD", "TRDAR_SE_CD_NM", "TRDAR_CD", "TRDAR_CD_NM") + tuple(x for x in r if x.startswith("TOT_"))}
save([slim(r) for r in fetch("VwsmTrdarRepopQq")], "repop_all.csv")
save([slim(r) for r in fetch("VwsmTrdarWrcPopltnQq")], "wrcpop_all.csv")
