import pandas as pd
import glob
import os

# --- 讀取所有 NDX CSV 檔案 ---
csv_files = glob.glob(os.path.join(os.path.dirname(__file__), "Nasdaq 100 Historical Data*.csv"))

frames = []
for f in csv_files:
    df = pd.read_csv(f, thousands=",")
    frames.append(df)

ndx = pd.concat(frames, ignore_index=True)

# --- 清理資料 ---
ndx["Date"] = pd.to_datetime(ndx["Date"], format="%m/%d/%Y")
ndx["Price"] = ndx["Price"].astype(str).str.replace(",", "").astype(float)
ndx["Change %"] = (
    ndx["Change %"].astype(str).str.replace("%", "").astype(float) / 100
)

# 去除重複日期，以最新來源為準，按日期升序排列
ndx = ndx.drop_duplicates(subset="Date").sort_values("Date").reset_index(drop=True)

# --- 建立 NDX2L / NDX3L ---
# 從第一個交易日收盤價出發，每日複利放大
BASE_PRICE = 100.0

ndx["NDX2L_daily_return"] = ndx["Change %"] * 2
ndx["NDX3L_daily_return"] = ndx["Change %"] * 3

# 累積乘積：price[t] = base * Π(1 + r_i)
ndx["NDX2L"] = BASE_PRICE * (1 + ndx["NDX2L_daily_return"]).cumprod()
ndx["NDX3L"] = BASE_PRICE * (1 + ndx["NDX3L_daily_return"]).cumprod()

# 同步以相同基準正規化 NDX 本身
ndx["NDX_norm"] = BASE_PRICE * (1 + ndx["Change %"]).cumprod()

# --- 輸出結果 ---
out_cols = ["Date", "Price", "Change %", "NDX_norm", "NDX2L", "NDX3L",
            "NDX2L_daily_return", "NDX3L_daily_return"]
result = ndx[out_cols].copy()
result.columns = [
    "Date", "NDX_Close", "NDX_DailyReturn",
    "NDX_Indexed", "NDX2L", "NDX3L",
    "NDX2L_DailyReturn", "NDX3L_DailyReturn",
]

output_path = os.path.join(os.path.dirname(__file__), "ndx_leveraged.csv")
result.to_csv(output_path, index=False, float_format="%.6f")

# --- 統計摘要 ---
start = result["Date"].iloc[0].strftime("%Y-%m-%d")
end   = result["Date"].iloc[-1].strftime("%Y-%m-%d")
days  = len(result)

def cagr(series, n_years):
    return (series.iloc[-1] / series.iloc[0]) ** (1 / n_years) - 1

n_years = (result["Date"].iloc[-1] - result["Date"].iloc[0]).days / 365.25

print(f"資料期間：{start} ~ {end}（{days} 個交易日，約 {n_years:.1f} 年）")
print(f"\n期末指數化價值（基準 = {BASE_PRICE}）：")
print(f"  NDX  (1x): {result['NDX_Indexed'].iloc[-1]:>12.2f}  CAGR {cagr(result['NDX_Indexed'],  n_years)*100:.2f}%")
print(f"  NDX2L(2x): {result['NDX2L'].iloc[-1]:>12.2f}  CAGR {cagr(result['NDX2L'], n_years)*100:.2f}%")
print(f"  NDX3L(3x): {result['NDX3L'].iloc[-1]:>12.2f}  CAGR {cagr(result['NDX3L'], n_years)*100:.2f}%")

print(f"\n最大單日回報率：")
print(f"  NDX   max: {result['NDX_DailyReturn'].max()*100:.2f}%  min: {result['NDX_DailyReturn'].min()*100:.2f}%")
print(f"  NDX2L max: {result['NDX2L_DailyReturn'].max()*100:.2f}%  min: {result['NDX2L_DailyReturn'].min()*100:.2f}%")
print(f"  NDX3L max: {result['NDX3L_DailyReturn'].max()*100:.2f}%  min: {result['NDX3L_DailyReturn'].min()*100:.2f}%")

print(f"\n已儲存至：{output_path}")
