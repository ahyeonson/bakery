"""프랜차이즈 확장 목표를 반영한 '확장성' 축 추가 평가.
확장성 = 브랜드 노출(유동 규모) + 단위경제 검증(점포당 제과매출) + 가맹 수용 시장(프랜차이즈 비중 40~70% 최적)
        + 복제 가능 상권(발달상권 가점, 관광특구·전통시장 감점)."""
import pandas as pd, numpy as np
from pathlib import Path
D = Path(__file__).parent / "data"
pd.set_option("display.width", 300); pd.set_option("display.max_columns", 30); pd.set_option("display.unicode.east_asian_width", True)
f = pd.read_csv(D / "scored_areas.csv")
pr = lambda s: s.rank(pct=True) * 100
fit = 100 - (f.프차비중.clip(0, 1) - 0.55).abs() / 0.55 * 100          # 55%에서 100점
typ = f.유형.map({"발달상권": 100, "골목상권": 55, "관광특구": 30, "전통시장": 20}).fillna(50)
f["S확장성"] = 0.3 * pr(f.유동) + 0.3 * pr(f.점포당_제과매출_월만) + 0.2 * fit.clip(0) + 0.2 * typ
f["종합"] = 0.6 * f.정량점수 + 0.4 * f.S확장성
f.to_csv(D / "scored_franchise.csv", index=False, encoding="utf-8-sig")
r = f.sort_values("종합", ascending=False).head(20).copy()
r["프차비중"] = (r.프차비중 * 100).round(0); r["cagr_유동"] = (r.cagr_유동 * 100).round(1)
for c in ["정량점수", "S확장성", "종합", "점포당_제과매출_월만"]: r[c] = r[c].round(0)
print(r[["유형", "상권", "점포", "제과점수", "프차비중", "cagr_유동", "점포당_제과매출_월만", "정량점수", "S확장성", "종합"]].to_string(index=False))
for n in ["왕십리역(왕십리)", "발산역(마곡)", "상계5동주민센터", "효창공원앞역 2번", "길동주민센터(강동도서관)", "가락시장역"]:
    x = f[f.상권 == n]
    if len(x): print(n, "순위", int((f.종합 > x.종합.iloc[0]).sum() + 1), "/", len(f), "확장성", round(x.S확장성.iloc[0]), "종합", round(x.종합.iloc[0]))
