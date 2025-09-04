import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from pandas_market_calendars import get_calendar
import func
import numpy as np
import scipy.stats as stats  # 新增导入



# 设置中文字体和负号显示（解决中文乱码）
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows系统可用
# plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac系统可用
plt.rcParams['axes.unicode_minus'] = False
matplotlib.use('Agg')


def plot_relationship(bond_pairs, df, trading_days_str, date_to_index, issuer, season, maturity):
    """
    绘制成交笔数比与价差的关系图（在一个大图中显示4个子图）
    """
    # 创建大图（2行2列）
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    fig.suptitle(f'{issuer}-{season}-{maturity}年债券交易笔数比与价差分析', fontsize=16)
    order = int(2)
    for i, (bondA, bondB) in enumerate(bond_pairs):

        # 准备数据
        pair_df = df[df['标的债券代码'].isin([bondA, bondB])].copy()
        pivot_df = pair_df.pivot(index='日期', columns='标的债券代码',
                                 values=['到期收益率', '每日每券的成交笔数'])

        # 计算指标
        pivot_df['价差'] = (pivot_df[('到期收益率', bondA)] - pivot_df[('到期收益率', bondB)]) * 100
        pivot_df['成交笔数比'] = pivot_df[('每日每券的成交笔数', bondA)] / pivot_df[('每日每券的成交笔数', bondB)]
        pivot_df = pivot_df.replace([np.inf, -np.inf], np.nan).dropna()

        if len(pivot_df) < 3:
            print(f"警告：{bondA}-{bondB}的有效数据点不足，跳过绘图")
            continue

        # ========== 左上：散点图+回归线 ==========
        ax = axes[0, 0] if i == 0 else axes[0, 1]
        sns.regplot(
            x='成交笔数比', y='价差', data=pivot_df,
            scatter_kws={'alpha': 0.6, 'color': '#1f77b4'},
            line_kws={'color': 'red', 'linewidth': 2},
            ax=ax
        )

        # 计算Pearson相关系数
        r, p_value = stats.pearsonr(pivot_df['成交笔数比'], pivot_df['价差'])

        # 回归分析（确保在model被引用前执行）
        X = sm.add_constant(pivot_df['成交笔数比'])
        model = sm.OLS(pivot_df['价差'], X).fit()

        # 添加统计信息（合并回归和相关系数）
        stats_text = (
            f'回归方程: y = {model.params[1]:.2f}x + {model.params[0]:.2f}\n'
            f'R方 = {model.rsquared:.2f}\n'
            f'回归p值 = {model.pvalues[1]:.3f}\n'
            f'Pearson r = {r:.2f}\n'
            f'相关p值 = {p_value:.3f}'
        )

        ax.text(0.05, 0.95, stats_text,
                transform=ax.transAxes,
                bbox=dict(facecolor='white', alpha=0.8),
                fontsize=9)

        ax.set_title(f'1-{order}: 成交笔数比 vs 价差')
        ax.set_xlabel(f'成交笔数比({bondA}/{bondB})')
        ax.set_ylabel('价差(bps)')
        ax.grid(True, linestyle=':', alpha=0.6)
        # ========== 下方：双轴折线图 ==========
        ax = axes[1, 0] if i == 0 else axes[1, 1]

        # 左轴：价差
        ax.plot([date_to_index[d.strftime('%Y-%m-%d')] for d in pivot_df.index],
                pivot_df['价差'], color='blue', label='价差(bps)')
        ax.set_ylabel('价差(bps)', color='blue')
        ax.tick_params(axis='y', labelcolor='blue')

        # 右轴：成交笔数比
        ax2 = ax.twinx()
        ax2.plot([date_to_index[d.strftime('%Y-%m-%d')] for d in pivot_df.index],
                 pivot_df['成交笔数比'], color='orange', linestyle='--', label='成交笔数比')
        ax2.set_ylabel(f'成交笔数比({bondA}/{bondB})', color='orange')
        ax2.tick_params(axis='y', labelcolor='orange')

        # 设置x轴
        ax.set_xticks(range(0, len(trading_days_str), 5))
        ax.set_xticklabels([d[5:] for d in trading_days_str[::5]], rotation=45)
        ax.set_xlabel('日期')
        ax.set_title(f'{bondA}-{bondB} (1-{order}): 价差与成交笔数比的时间趋势')
        ax.grid(True, linestyle=':', alpha=0.6)
        order += 1

        # 合并图例
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines + lines2, labels + labels2, loc='upper right')

    # 调整布局
    plt.tight_layout()
    plt.subplots_adjust(top=0.9, hspace=0.3, wspace=0.25)

    # 保存图片
    plt.savefig(f'spread_demo_corr/{issuer}-{season}-综合分析.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"综合分析图已保存至: spread_demo_corr/{issuer}-{season}-综合分析.png")


# 主程序保持不变
if __name__ == "__main__":
    # 输入参数
    data_file = "利差分析四大行2年_final.csv"
    issuer = "中华人民共和国财政部"
    min_maturity = 28.0
    max_maturity = 30.0
    maturity = int(max_maturity)
    season = "2024S1"
    start_date = "2024-01-01"
    end_date = "2024-05-15"

    #('2024S1', '2024-01-01', '2024-05-15'),
    #('2024S2', '2024-05-16', '2024-07-25'),
    #('2024S3', '2024-07-26', '2024-09-23'),
    #('2024S4', '2024-09-24', '2025-01-16'),
    #('2025S1', '2025-01-17', '2025-04-28'),
    #('2025S2', '2025-04-29', '2025-08-06'),

    # 获取债券列表
    bond_list = func.select_bond(data_file, start_date, end_date, issuer, min_maturity, max_maturity)
    print("分析的债券:", bond_list)

    if len(bond_list) < 3:
        print("需要至少3只债券进行分析")
    else:
        # 读取并筛选数据
        df = pd.read_csv(data_file, parse_dates=['日期'])
        df = df[(df['日期'] >= start_date) & (df['日期'] <= end_date)]
        filtered_df = df[df['标的债券代码'].isin(bond_list)].copy()

        if filtered_df.empty:
            print("警告：未找到指定债券的数据！")
        else:
            # 获取交易日历
            shsz_calendar = get_calendar('SSE')
            trading_days = shsz_calendar.valid_days(start_date=start_date, end_date=end_date)
            trading_days_str = [d.strftime('%Y-%m-%d') for d in trading_days]
            date_to_index = {date_str: idx for idx, date_str in enumerate(trading_days_str)}

            # 只保留交易日数据
            filtered_df = filtered_df[filtered_df['日期'].astype(str).isin(trading_days_str)]

            # 分析1-2和1-3的关系
            bond_pairs = [(bond_list[0], bond_list[1]), (bond_list[0], bond_list[2])]
            plot_relationship(bond_pairs, filtered_df, trading_days_str, date_to_index,
                              issuer, season, maturity)