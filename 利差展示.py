import pandas as pd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import func
from pandas_market_calendars import get_calendar

# 设置中文字体和负号显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def plot_spread_quantiles(bond_list, bond_ytms, date_to_index, save_path='spread_boxplot.png'):
    """
    用箱型图展示利差分位数（10/25/50/75/90分位）并单独保存

    参数：
        bond_list: 债券列表（如['bond1', 'bond2', 'bond3']）
        bond_ytms: 字典，键为债券名称，值为YTM序列（pd.Series）
        date_to_index: 日期到x轴坐标的映射字典（本函数未直接使用）
        save_path: 图片保存路径
    """
    # 准备数据容器
    spreads = {}

    # 计算所有利差组合
    if len(bond_ytms) >= 2:
        bond1 = bond_list[0]
        ytm1 = bond_ytms[bond1]

        # 计算1-N利差
        for i in range(1, len(bond_list)):
            bondN = bond_list[i]
            spread_name = f'1-{i + 1}'
            spreads[spread_name] = (ytm1 - bond_ytms[bondN]) * 100  # 转为bps

        # 计算2-3利差（如果存在）
        if len(bond_list) >= 3:
            spreads['2-3'] = (bond_ytms[bond_list[1]] - bond_ytms[bond_list[2]]) * 100

    # 如果没有有效利差则退出
    if not spreads:
        print("警告：无有效利差数据！")
        return

    # 创建DataFrame
    df_spreads = pd.DataFrame(spreads)

    # 创建箱型图
    fig, ax = plt.subplots(figsize=(10, 6))

    # 绘制箱型图（显示均值、分位数和离群点）
    boxprops = dict(linestyle='-', linewidth=1.5, color='#1f77b4')
    medianprops = dict(linestyle='-', linewidth=2, color='red')
    meanprops = dict(marker='D', markeredgecolor='black', markerfacecolor='green')

    df_spreads.plot(kind='box',
                    ax=ax,
                    patch_artist=True,
                    boxprops=boxprops,
                    medianprops=medianprops,
                    meanprops=meanprops,
                    showmeans=True,
                    whis=[10, 90],
                    showfliers=False)  # 将须线设为10%和90%分位

    # 设置图表属性
    ax.set_title('债券利差分位数箱型图', fontsize=14)
    ax.set_xlabel('利差组合', fontsize=12)
    ax.set_ylabel('利差(bps)', fontsize=12)
    ax.grid(True, linestyle=':', alpha=0.6)

    # 添加参考线
    ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax.text(1.02, 0.5,
            '箱型图说明：\n'
            '箱体范围 = 25%-75%分位\n'
            '须线范围 = 10%-90%分位\n'
            '中位数 = 红线\n'
            '均值 = 绿色菱形',
            transform=ax.transAxes,
            verticalalignment='center',
            bbox=dict(facecolor='white', alpha=0.8))

    # 调整布局并保存
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"箱型图已保存至：{save_path}")



def get_quarter_dates(season):
    """（原有函数保持不变）"""
    if 'Q' in season:
        year, quarter = season.split('Q')
        year = int(year)
        quarter = int(quarter)
        first_month = 3 * quarter - 2
        last_month = 3 * quarter
        start_date = pd.Timestamp(year=year, month=first_month, day=1)
        end_date = pd.Timestamp(year=year, month=last_month, day=1) + pd.offsets.QuarterEnd()
    else:
        year = int(season)
        start_date = pd.Timestamp(year=year, month=1, day=1)
        end_date = pd.Timestamp(year=year, month=12, day=31)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


# 输入参数
data_file = "利差分析四大行2年_final.csv"
issuer = "中华人民共和国财政部"
min_maturity = 28.0
max_maturity = 30.0
maturity = int(max_maturity)
season = "2024"
start_date = "2024-01-01"
end_date = "2024-12-31"

# ('2024S1', '2024-01-01', '2024-05-15'),
# ('2024S2', '2024-05-16', '2024-07-25'),
# ('2024S3', '2024-07-26', '2024-09-23'),
# ('2024S4', '2024-09-24', '2025-01-16'),
# ('2025S1', '2025-01-17', '2025-04-28'),
# ('2025S2', '2025-04-29', '2025-08-06'),
# 获取债券列表
bond_list = func.select_bond(data_file, start_date, end_date, issuer, min_maturity, max_maturity)
print(bond_list)

# 读取并筛选数据
df = pd.read_csv(data_file, parse_dates=['日期'])
df = df[(df['日期'] >= start_date) & (df['日期'] <= end_date)]
filtered_df = df[df['标的债券代码'].isin(bond_list)].copy()

if filtered_df.empty:
    print("警告：未找到指定债券的数据！请检查债券代码是否正确。")
else:
    # 获取中国交易日历并创建映射
    shsz_calendar = get_calendar('SSE')
    trading_days = shsz_calendar.valid_days(start_date=start_date, end_date=end_date)
    trading_days_str = [d.strftime('%Y-%m-%d') for d in trading_days]
    date_to_index = {date_str: idx for idx, date_str in enumerate(trading_days_str)}
    filtered_df = filtered_df[filtered_df['日期'].astype(str).isin(trading_days_str)]

    # 创建画布和子图
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 16), sharex=True)
    fig.suptitle(f'{issuer}-{season}-{maturity}年债券利差分析', fontsize=14)

    # 设置X轴（使用交易日索引）
    day_indices = range(len(trading_days))
    for ax in [ax1, ax2, ax3]:
        ax.set_xticks(day_indices[::5])  # 每5个交易日显示一个标签
        ax.set_xticklabels([trading_days[i].strftime('%m-%d') for i in day_indices[::5]])
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))

    # ========== 修改1：在图1右侧添加中债YTM ==========
    # 读取中债估值数据
    ytm_df = pd.read_excel(
        "30Y中债估值.xlsx",
        header=None,  # 关键修改：文件无列名
        names=['日期', 'YTM值'],  # 手动指定列名
        parse_dates=['日期']  # 解析日期列
    )

    # 过滤日期范围
    ytm_df = ytm_df[(ytm_df['日期'] >= pd.to_datetime(start_date)) &
                    (ytm_df['日期'] <= pd.to_datetime(end_date))]
    ytm_df = ytm_df[ytm_df['日期'].astype(str).isin(trading_days_str)]

    # 创建右侧Y轴
    ax1_right = ax1.twinx()
    ytm_dates = [date_to_index[d.strftime('%Y-%m-%d')] for d in ytm_df['日期']]
    ax1_right.plot(
        ytm_dates,
        ytm_df['YTM值'],  # 使用手动指定的列名
        color='purple',
        linestyle=':',
        linewidth=2,
        label='30Y中债YTM'
    )
    ax1_right.set_ylabel('中债YTM(%)', color='purple')
    ax1_right.tick_params(axis='y', colors='purple')
    ax1_right.legend(loc='upper right')

    # 子图1：绘制利差曲线（原有逻辑）
    bond_ytms = {}
    for bond in bond_list:
        bond_data = filtered_df[filtered_df['标的债券代码'] == bond]
        if not bond_data.empty:
            bond_ytms[bond] = bond_data.set_index('日期')['到期收益率']

    if len(bond_ytms) >= 2:
        bond1 = bond_list[0]
        ytm1 = bond_ytms[bond1]
        for i in range(1, len(bond_list)):
            bondN = bond_list[i]
            ytmN = bond_ytms[bondN]
            spread = (ytm1 - ytmN) * 100
            x_values = [date_to_index[d.strftime('%Y-%m-%d')] for d in spread.index]
            ax1.plot(x_values, spread.values, label=f'1-{i + 1}')
        if len(bond_list) >= 3:
            ytm2 = bond_ytms[bond_list[1]]
            ytm3 = bond_ytms[bond_list[2]]
            spread_23 = (ytm2 - ytm3) * 100
            x_values = [date_to_index[d.strftime('%Y-%m-%d')] for d in spread_23.index]
            ax1.plot(x_values, spread_23.values, label='2-3')
        ax1.axhline(y=0, color='red', linestyle='--', linewidth=0.8)
        ax1.set_ylabel('利差(bps)', fontsize=10)
        ax1.grid(True, linestyle='--', alpha=0.6)
        ax1.legend(title='债券利差', bbox_to_anchor=(1.08, 0.5), loc='center left')
        #plot_spread_quantiles(bond_list, bond_ytms, date_to_index, f'spread_demo_7_30/{issuer}-{season}-{maturity}年债券利差分位.png')
    # ========== 修改2：将图二单位改为亿元 ==========
    # 子图2：单券借贷余额和总借贷余额（单位改为亿元）
    total_loan = filtered_df.groupby('日期')['单券借贷余额（百万元）'].sum().reset_index()
    total_loan['单券借贷余额（亿元）'] = total_loan['单券借贷余额（百万元）'] / 100  # 百万元→亿元

    ranks = ["1st", "2nd", "3rd", "4th", "5th"][:len(bond_list)]
    for i, bond in enumerate(bond_list):
        bond_data = filtered_df[filtered_df['标的债券代码'] == bond]
        if not bond_data.empty:
            bond_data = bond_data.copy()  # 避免SettingWithCopyWarning
            bond_data['单券借贷余额（亿元）'] = bond_data['单券借贷余额（百万元）'] / 100  # 转换单位
            x_values = [date_to_index[d.strftime('%Y-%m-%d')] for d in bond_data['日期']]
            ax2.plot(
                x_values,
                bond_data['单券借贷余额（亿元）'],
                linestyle='-',
                marker='o',
                markersize=4,
                markeredgecolor='none',
                alpha=0.8,
                label=f'{bond}({ranks[i]})'
            )

    # 绘制总借贷余额曲线（亿元）
    x_values_total = [date_to_index[d.strftime('%Y-%m-%d')] for d in total_loan['日期']]
    ax2.plot(
        x_values_total,
        total_loan['单券借贷余额（亿元）'],
        linestyle='-',
        color='black',
        linewidth=2,
        label='总借贷余额'
    )
    ax2.set_ylabel('借贷余额(亿元)', fontsize=10)  # 单位改为亿元
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend(title='债券代码', bbox_to_anchor=(1.02, 1), loc='upper left')

    # 子图3：成交笔数曲线（保持不变）
    line_styles = ['-', '-', '-', '-', '-']
    line_widths = [2.0, 1.5, 1.5, 1.2, 1.2]
    for i, bond in enumerate(bond_list):
        bond_data = filtered_df[filtered_df['标的债券代码'] == bond]
        if not bond_data.empty:
            x_values = [date_to_index[d.strftime('%Y-%m-%d')] for d in bond_data['日期']]
            ax3.plot(
                x_values,
                bond_data['每日每券的成交笔数'],
                linestyle=line_styles[i] if i < len(line_styles) else '-',
                linewidth=line_widths[i] if i < len(line_widths) else 1.0,
                alpha=0.9,
                label=f'{bond}({ranks[i]})'
            )
    ax3.set_xlabel('日期', fontsize=10)
    ax3.set_ylabel('成交笔数', fontsize=10)
    ax3.grid(True, linestyle='--', alpha=0.6)
    ax3.legend(title='债券代码', bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.setp(ax3.get_xticklabels(), rotation=45)

    # 调整布局
    plt.tight_layout()
    plt.subplots_adjust(top=0.92, hspace=0.15)

    # 保存和显示
    plt.savefig(
        f'spread_demo_2y/{issuer}-{season}-{maturity}年债券利差分析.png',
        dpi=300,
        bbox_inches='tight'
    )
    plt.show()
    plt.close()