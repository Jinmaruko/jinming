
# 化妆品贸易公司销售数据分析
# 作者：Jin Ming
# 工具：Python, pandas, matplotlib

# ============================================
# 第一步：环境准备
# ============================================
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

!wget -q -O SimHei.ttf https://raw.githubusercontent.com/StellarCN/scp_zh/master/fonts/SimHei.ttf
fm.fontManager.addfont("SimHei.ttf")
plt.rcParams["font.family"] = "SimHei"
plt.rcParams["axes.unicode_minus"] = False

# ============================================
# 第二步：读取数据
# 使用时请替换为你的实际文件路径
# ============================================
df = pd.read_excel("your_sales_data.xlsx")

# ============================================
# 第三步：数据基本情况
# ============================================
print(df.shape)
print(df.info())
print(df.describe())

# ============================================
# 第四步：各平台利润分析
# ============================================
df_sold = df[df["个数"] > 0]

platform_summary = df_sold.groupby("平台").agg(
    订单数=("个数", "count"),
    总利润=("利润", "sum"),
    平均利润=("利润", "mean")
).round(2)

print(platform_summary)

# ============================================
# 第五步：各平台利润可视化
# ============================================
df_plot = platform_summary[platform_summary.index != "样品"]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

df_plot["总利润"].plot(kind="bar", ax=ax1,
    color=["#FF6B6B","#4ECDC4","#45B7D1","#96CEB4","#FFEAA7"])
ax1.set_title("各平台总利润对比")
ax1.set_xlabel("平台")
ax1.set_ylabel("利润（元）")
ax1.tick_params(axis="x", rotation=45)

df_plot["平均利润"].plot(kind="bar", ax=ax2,
    color=["#FF6B6B","#4ECDC4","#45B7D1","#96CEB4","#FFEAA7"])
ax2.set_title("各平台平均利润对比")
ax2.set_xlabel("平台")
ax2.set_ylabel("利润（元）")
ax2.tick_params(axis="x", rotation=45)

plt.tight_layout()
plt.show()

# ============================================
# 第六步：退货率分析
# ============================================
total = df.groupby("平台")["个数"].count()
returns = df[df["个数"] < 0].groupby("平台")["个数"].count()
退货率 = (returns / total * 100).round(2)
print(退货率)

# ============================================
# 第七步：地区分布分析
# ============================================
df_sold = df[df["个数"] > 0].copy()
df_sold["省份"] = df_sold["收货人"].str.split("\n").str[-1].str[:3]

province_count = df_sold["省份"].value_counts().head(10)

fig, ax = plt.subplots(figsize=(12, 5))
province_count.plot(kind="bar", ax=ax, color="#4ECDC4")
ax.set_title("Top10省份订单分布")
ax.set_xlabel("省份")
ax.set_ylabel("订单数")
ax.tick_params(axis="x", rotation=45)

for i, v in enumerate(province_count):
    ax.text(i, v + 0.1, str(v), ha="center", fontsize=10)

plt.tight_layout()
plt.show()

# ============================================
# 第八步：扣除佣金后实际利润分析
# ============================================
# 读取平台账单
df_douyin = pd.read_csv("your_douyin_bill.csv", encoding="utf-8")
df_kuaishou = pd.read_excel("your_kuaishou_bill.xlsx")

# 处理抖音
df_douyin["订单号"] = df_douyin["订单号"].astype(str).str.replace("'", "")
df_douyin_settlement = df_douyin[df_douyin["动账场景"] == "货款结算入账"].copy()
df_douyin_fee = df_douyin_settlement[["订单号", "佣金", "平台服务费"]].copy()
df_douyin_fee["抖音总费用"] = (df_douyin_fee["佣金"] + df_douyin_fee["平台服务费"]).abs()

# 处理快手
df_kuaishou["订单号"] = df_kuaishou["订单号"].astype(str)
df_kuaishou_fee = df_kuaishou[["订单号", "达人佣金(元)", "技术服务费(元)"]].copy()
df_kuaishou_fee["快手总费用"] = (df_kuaishou_fee["达人佣金(元)"] + df_kuaishou_fee["技术服务费(元)"]).abs()

# 合并佣金
df["订单号"] = df["订单号"].astype(str)
df_merged = df.merge(df_douyin_fee[["订单号", "抖音总费用"]], on="订单号", how="left")
df_merged = df_merged.merge(df_kuaishou_fee[["订单号", "快手总费用"]], on="订单号", how="left")
df_merged["实际佣金"] = (df_merged["抖音总费用"].fillna(0) + df_merged["快手总费用"].fillna(0)).round(2)
df_merged["实际利润"] = (df_merged["利润"] - df_merged["实际佣金"]).round(2)

# 汇总
df_sold = df_merged[df_merged["个数"] > 0]
real_profit = df_sold.groupby("平台").agg(
    订单数=("个数", "count"),
    原始利润=("利润", "sum"),
    总佣金=("实际佣金", "sum"),
    实际利润=("实际利润", "sum")
).round(2)
real_profit["利润减少比例"] = (real_profit["总佣金"] / real_profit["原始利润"] * 100).round(1).astype(str) + "%"
print(real_profit)

# 可视化
df_plot = real_profit[~real_profit.index.isin(["样品"])]
fig, ax = plt.subplots(figsize=(12, 6))
x = range(len(df_plot))
width = 0.35

bars1 = ax.bar([i - width/2 for i in x], df_plot["原始利润"],
               width, label="原始利润", color="#4ECDC4")
bars2 = ax.bar([i + width/2 for i in x], df_plot["实际利润"],
               width, label="扣除佣金后实际利润", color="#FF6B6B")

ax.set_title("各平台原始利润 vs 实际利润对比")
ax.set_xlabel("平台")
ax.set_ylabel("利润（元）")
ax.set_xticks(x)
ax.set_xticklabels(df_plot.index)
ax.legend()

for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
            f"{bar.get_height():.0f}", ha="center", fontsize=9)
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
            f"{bar.get_height():.0f}", ha="center", fontsize=9)

plt.tight_layout()
plt.show()
