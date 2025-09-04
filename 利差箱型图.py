import pandas as pd
import matplotlib.ticker as ticker
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import func
import os

# 设置中文字体和负号显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def generate_spread_boxplots(data_file, issuer, min_maturity, max_maturity, periods):
    """
    生成多个时间周期的利差箱型图（子图形式）

    参数：
        data_file: 数据文件路径
        issuer: 发行人名称
        min_maturity: 最小剩余期限
        max_maturity: 最大剩余期限
        periods: 时间段列表，格式如 [('2023Q1', '2023-01-01', '2023-03-31'), ...]
    """
    # 创建输出目录
    os.makedirs('spread_boxplots', exist_ok=True)

    # 计算需要的子图行列数
    n_periods = len(periods)
    n_cols = min(3, n_periods)
    n_rows = (n_periods + n_cols - 1) // n_cols

    # 创建大图
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 6, n_rows * 4))
    if n_periods == 1:
        axes = [[axes]]
    elif n_rows == 1:
        axes = [axes]

    # 遍历每个时间段
    for idx, (period_name, start_date, end_date) in enumerate(periods):
        row = idx // n_cols
        col = idx % n_cols

        # 获取债券列表
        bond_list = func.select_bond(data_file, start_date, end_date, issuer, min_maturity, max_maturity)
        if not bond_list:
            print(f"警告：{period_name} 未找到符合条件的债券！")
            continue

        # 读取并筛选数据
        df = pd.read_csv(data_file, parse_dates=['日期'])
        df = df[(df['日期'] >= start_date) & (df['日期'] <= end_date)]
        filtered_df = df[df['标的债券代码'].isin(bond_list)].copy()

        if filtered_df.empty:
            print(f"警告：{period_name} 未找到指定债券的数据！")
            continue

        # 计算利差
        bond_ytms = {}
        for bond in bond_list:
            bond_data = filtered_df[filtered_df['标的债券代码'] == bond]
            if not bond_data.empty:
                bond_ytms[bond] = bond_data.set_index('日期')['到期收益率']

        if len(bond_ytms) < 2:
            print(f"警告：{period_name} 有效债券不足2个！")
            continue

        # 准备数据容器
        spreads = {}
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

        # 创建DataFrame
        df_spreads = pd.DataFrame(spreads)

        # 绘制箱型图
        ax = axes[row][col]

        # 箱型图样式设置
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
                        showfliers=False)

        ax.yaxis.set_major_locator(ticker.MultipleLocator(1))  # 1bp一个刻度
        ax.set_ylim(bottom=min(0, df_spreads.min().min() - 1),
                    top=df_spreads.max().max() + 1)  # 统一Y轴范围
        # 设置子图属性
        ax.set_title(f'{period_name} 利差分布', fontsize=12)
        ax.set_xlabel('')
        ax.set_ylabel('利差(bps)', fontsize=10)
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.axhline(0, color='gray', linestyle='--', alpha=0.5)

        # 添加说明文本框
        ax.text(1.02, 0.5,
                '箱型图说明：\n'
                '箱体=25%-75%\n'
                '须线=10%-90%\n'
                '中线=中位数\n'
                '◇=均值',
                transform=ax.transAxes,
                fontsize=8,
                verticalalignment='center',
                bbox=dict(facecolor='white', alpha=0.8))

    # 隐藏多余的子图
    for idx in range(n_periods, n_rows * n_cols):
        row = idx // n_cols
        col = idx % n_cols
        axes[row][col].axis('off')

    # 调整布局
    plt.tight_layout()

    # 保存和显示
    output_path = f'spread_demo_boxplots/{issuer}_{min_maturity}-{max_maturity}年利差箱型图.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"箱型图合集已保存至：{output_path}")


# 示例使用
if __name__ == "__main__":
    # 定义要分析的时间段列表
    periods = [
        ('2024S1', '2024-01-01', '2024-05-15'),
        ('2024S2', '2024-05-16', '2024-07-25'),
        ('2024S3', '2024-07-26', '2024-09-23'),
        ('2024S4', '2024-09-24', '2025-01-16'),
        ('2025S1', '2025-01-17', '2025-04-28'),
        ('2025S2', '2025-04-29', '2025-08-06'),
    ]

    generate_spread_boxplots(
        data_file="利差分析四大行2年_final.csv",
        issuer="中华人民共和国财政部",
        min_maturity=28.0,
        max_maturity=30.0,
        periods=periods
    )