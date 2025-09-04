import pandas as pd
from datetime import datetime


def select_bond(data_path, start_date, end_date, issuer, min_maturity, max_maturity):
    """
    分析债券历史行情数据

    参数:
        data_path (str): CSV文件路径
        start_date (str): 开始日期(格式: 'YYYY-MM-DD')
        end_date (str): 结束日期(格式: 'YYYY-MM-DD')
        issuer (str): 债务主体名称
        min_maturity (float): 剩余期限下限(年)
        max_maturity (float): 剩余期限上限(年)

    返回:
        打印不重复债券数量和最活跃前三只债券
    """
    # 读取数据
    try:
        df = pd.read_csv(data_path, parse_dates=['日期'])
    except Exception as e:
        print(f"读取文件出错: {e}")
        return

    # 数据清洗
    df = df.dropna(subset=['标的债券代码', '债务主体', '剩余期限', '每日每券的成交笔数'])
    df['剩余期限'] = pd.to_numeric(df['剩余期限'], errors='coerce')
    df = df.dropna(subset=['剩余期限'])

    # 日期过滤
    mask = (df['日期'] >= pd.to_datetime(start_date)) & \
           (df['日期'] <= pd.to_datetime(end_date)) & \
           (df['债务主体'] == issuer) & \
           (df['剩余期限'] >= min_maturity) & \
           (df['剩余期限'] <= max_maturity)

    filtered_df = df.loc[mask]

    if filtered_df.empty:
        print("没有找到符合条件的债券数据")
        return

    # 统计不重复债券数量
    unique_bonds = filtered_df['标的债券代码'].nunique()
    print(
        f"在{start_date}至{end_date}期间，{issuer}的剩余期限{min_maturity}-{max_maturity}年的不重复债券数量: {unique_bonds}只")

    # 计算每只债券的平均成交笔数
    bond_activity = filtered_df.groupby('标的债券代码')['每日每券的成交笔数'].mean().reset_index()
    bond_activity.columns = ['债券代码', '平均成交笔数']

    # 获取最活跃的三只债券
    top3_active = bond_activity.sort_values('平均成交笔数', ascending=False).head(5)

    print("\n最活跃的前三只债券:")
    for i, (bond_code, avg_trades) in enumerate(zip(top3_active['债券代码'], top3_active['平均成交笔数']), 1):
        print(f"第{i}名: 债券代码 {bond_code}, 平均每日成交笔数 {avg_trades:.2f}")

    return top3_active['债券代码'].tolist()



def select_bond_fromstart(data_path, start_date, end_date, issuer, min_maturity, max_maturity):
    """
    分析债券历史行情数据

    参数:
        data_path (str): CSV文件路径
        start_date (str): 开始日期(格式: 'YYYY-MM-DD')
        end_date (str): 结束日期(格式: 'YYYY-MM-DD')
        issuer (str): 债务主体名称
        min_maturity (float): 剩余期限下限(年)
        max_maturity (float): 剩余期限上限(年)

    返回:
        打印不重复债券数量和最活跃前三只债券
    """
    # 读取数据
    try:
        df = pd.read_csv(data_path, parse_dates=['日期'])
    except Exception as e:
        print(f"读取文件出错: {e}")
        return

    # 数据清洗
    df = df.dropna(subset=['标的债券代码', '债务主体', '剩余期限', '每日每券的成交笔数'])
    df['剩余期限'] = pd.to_numeric(df['剩余期限'], errors='coerce')
    df = df.dropna(subset=['剩余期限'])

    # 将日期转换为datetime
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)

    # 获取开始日期所在周的第一天（周一）
    start_week_start = start_datetime - pd.to_timedelta(start_datetime.dayofweek, unit='D')
    # 获取开始日期所在周的最后一天（周日）
    start_week_end = start_week_start + pd.to_timedelta(6, unit='D')

    # 找出在开始日期所在周就已经存在的债券
    existing_bonds = df[(df['日期'] >= start_week_start) &
                        (df['日期'] <= start_week_end) &
                        (df['债务主体'] == issuer)]['标的债券代码'].unique()

    if len(existing_bonds) == 0:
        print(f"在{start_week_start.date()}至{start_week_end.date()}期间没有找到{issuer}的任何债券数据")
        return

    # 日期过滤（主时间段）
    mask = (df['日期'] >= start_datetime) & \
           (df['日期'] <= end_datetime) & \
           (df['债务主体'] == issuer) & \
           (df['剩余期限'] >= min_maturity) & \
           (df['剩余期限'] <= max_maturity) & \
           (df['标的债券代码'].isin(existing_bonds))

    filtered_df = df.loc[mask]

    if filtered_df.empty:
        print("没有找到符合条件的债券数据")
        return

    # 统计不重复债券数量
    unique_bonds = filtered_df['标的债券代码'].nunique()
    print(
        f"在{start_date}至{end_date}期间，{issuer}的剩余期限{min_maturity}-{max_maturity}年的不重复债券数量: {unique_bonds}只")
    print(f"（仅包含在{start_week_start.date()}至{start_week_end.date()}期间已存在的债券）")

    # 计算每只债券的平均成交笔数
    bond_activity = filtered_df.groupby('标的债券代码')['每日每券的成交笔数'].mean().reset_index()
    bond_activity.columns = ['债券代码', '平均成交笔数']

    # 获取最活跃的三只债券
    top3_active = bond_activity.sort_values('平均成交笔数', ascending=False).head(5)

    print("\n最活跃的前三只债券:")
    for i, (bond_code, avg_trades) in enumerate(zip(top3_active['债券代码'], top3_active['平均成交笔数']), 1):
        print(f"第{i}名: 债券代码 {bond_code}, 平均每日成交笔数 {avg_trades:.2f}")

    return top3_active['债券代码'].tolist()