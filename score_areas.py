"""4축 중 수요·소비력·공급경쟁 3개 축을 정량 점수화 (촉매는 별도 조사)."""
import pandas as pd, numpy as np
from pathlib import Path
D = Path(__file__).parent / "data"
pd.set_option("display.width", 300); pd.set_option("display.max_columns", 40); pd.set_option("display.unicode.east_asian_width", True)
Q0, Q1, Q2 = "20234", "20244", "20254"   # 2년 전, 1년 전, 최신

sales = {q: pd.read_csv(D / f"sales_{q}.csv") for q in (Q0, Q1, Q2)}
stores = {q: pd.read_csv(D / f"stores_{q}.csv") for q in (Q0, Q1, Q2)}
fl = {q: pd.read_csv(D / f"flpop_{q}.csv").set_index("TRDAR_CD").TOT_FLPOP_CO for q in (Q0, Q1, Q2)}
rp = pd.read_csv(D / "repop_all.csv").pivot_table(index="TRDAR_CD", columns="STDR_YYQU_CD", values="TOT_REPOP_CO")
wp = pd.read_csv(D / "wrcpop_all.csv").pivot_table(index="TRDAR_CD", columns="STDR_YYQU_CD", values="TOT_WRC_POPLTN_CO")

def tot(q):  # 커피+제과점 합산 매출
    return sales[q].groupby("TRDAR_CD").THSMON_SELNG_AMT.sum()
bk = {q: sales[q][sales[q].SVC_INDUTY_CD_NM == "제과점"].set_index("TRDAR_CD") for q in sales}
bs = {q: stores[q][stores[q].SVC_INDUTY_CD_NM == "제과점"].set_index("TRDAR_CD") for q in stores}
st = stores[Q2].groupby("TRDAR_CD").agg(점포=("SIMILR_INDUTY_STOR_CO", "sum"), 프차=("FRC_STOR_CO", "sum"), 폐업=("CLSBIZ_STOR_CO", "sum"), 개업=("OPBIZ_STOR_CO", "sum"))
st0 = stores[Q0].groupby("TRDAR_CD").SIMILR_INDUTY_STOR_CO.sum()

df = bk[Q2][["TRDAR_SE_CD_NM", "TRDAR_CD_NM", "THSMON_SELNG_AMT", "THSMON_SELNG_CO"]].copy()
df.columns = ["유형", "상권", "제과매출", "제과건수"]
df["제과점수"] = bs[Q2].SIMILR_INDUTY_STOR_CO
df = df.join(st)
df["cagr_매출_카페베이커리"] = (tot(Q2) / tot(Q0)) ** 0.5 - 1
df["cagr_매출_제과"] = (bk[Q2].THSMON_SELNG_AMT / bk[Q0].THSMON_SELNG_AMT.reindex(df.index)) ** 0.5 - 1
df["객단가"] = df.제과매출 / df.제과건수
a = sales[Q2][sales[Q2].SVC_INDUTY_CD_NM == "제과점"].set_index("TRDAR_CD")
df["2030_비중"] = (a.AGRDE_20_SELNG_AMT + a.AGRDE_30_SELNG_AMT) / a.THSMON_SELNG_AMT
df["3040_비중"] = (a.AGRDE_30_SELNG_AMT + a.AGRDE_40_SELNG_AMT) / a.THSMON_SELNG_AMT
df["cagr_유동"] = (fl[Q2] / fl[Q0]) ** 0.5 - 1
df["cagr_상주"] = np.nan   # 상주인구는 23Q4 이후 갱신 없음 → 증가율 산출 불가, 규모만 사용
df["cagr_직장"] = wp[int(Q1)] / wp[int(Q0)] - 1   # 직장인구는 연 1회 갱신: 23Q4→24Q4 (24Q4=25Q4)
df["유동"] = fl[Q2]; df["상주"] = rp[int(Q2)]; df["직장"] = wp[int(Q2)]
df["점포증가_cagr"] = (df.점포 / st0) ** 0.5 - 1
df["프차비중"] = df.프차 / df.점포
df["폐업률"] = df.폐업 / df.점포
df["점포당_제과매출_월만"] = df.제과매출 / df.제과점수 / 3 / 1e4
df["수요공급"] = (df.유동 + df.상주 + df.직장) / df.점포   # 점포 1개당 배후인구

f = df[(df.제과점수 >= 4) & (df.제과매출 > 0) & (df.점포 >= 15)].replace([np.inf, -np.inf], np.nan).dropna(subset=["cagr_유동", "cagr_직장", "cagr_매출_카페베이커리"])
f = f[(f.유동 > 0)].copy()
for c, lo, hi in [("cagr_유동", -.25, .35), ("cagr_직장", -.3, .4), ("cagr_매출_카페베이커리", -.3, .45), ("cagr_매출_제과", -.3, .45), ("점포증가_cagr", -.2, .3)]:
    f[c] = f[c].clip(lo, hi)
f["프차비중"] = f.프차비중.clip(0, 1)
f["객단가"] = f.객단가.clip(f.객단가.quantile(.05), f.객단가.quantile(.95))
pr = lambda s, hi=True: (s.rank(pct=True) if hi else 1 - s.rank(pct=True)) * 100
f["S수요"] = (0.4 * pr(f.cagr_유동) + 0.25 * pr(f.cagr_직장) + 0.35 * pr(f.유동 + f.상주 + f.직장))
f["S소비력"] = (0.4 * pr(f.cagr_매출_카페베이커리) + 0.2 * pr(f.cagr_매출_제과.fillna(f.cagr_매출_제과.median())) + 0.25 * pr(f.객단가) + 0.15 * pr(f["2030_비중"] + f["3040_비중"]))
f["S공급"] = (0.3 * pr(f.수요공급) + 0.25 * pr(f.폐업률, False) + 0.25 * pr(f.프차비중, False) + 0.2 * pr(f.점포증가_cagr, False))
f["정량점수"] = 0.37 * f.S수요 + 0.38 * f.S소비력 + 0.25 * f.S공급
f.to_csv(D / "scored_areas.csv", encoding="utf-8-sig")
print("후보 상권 수:", len(f))
cols = ["유형", "상권", "점포", "제과점수", "프차비중", "폐업률", "cagr_유동", "cagr_상주", "cagr_직장", "cagr_매출_카페베이커리", "객단가", "S수요", "S소비력", "S공급", "정량점수"]
r = f.sort_values("정량점수", ascending=False)[cols].head(35)
for c in ["프차비중", "폐업률", "cagr_유동", "cagr_상주", "cagr_직장", "cagr_매출_카페베이커리"]: r[c] = (r[c] * 100).round(1)
for c in ["S수요", "S소비력", "S공급", "정량점수", "객단가"]: r[c] = r[c].round(0)
print(r.to_string(index=False))
