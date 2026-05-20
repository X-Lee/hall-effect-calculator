import pandas as pd

data_g = pd.read_excel(r"C:\Users\LXC\Desktop\mer.xlsx")
data_g = data_g[['数据发布日期', '度量名称', '品种名称', '指标数据值']]
data_g['全称'] = data_g['度量名称'] + data_g['品种名称']
data_g = data_g[['数据发布日期', '全称', '指标数据值']]
data_g['数据发布日期'] = pd.to_datetime(data_g['数据发布日期'])
data_g['数据发布日期'] = data_g['数据发布日期'].dt.to_period('M')
result = data_g.groupby(['数据发布日期', '全称'])['指标数据值'].agg(['mean', 'sum', 'max', 'min']).reset_index()
print(result)

# 1. 执透视操作：以日期为索引，全称为新列，填充值为 mean
df_pivot = result.pivot(index='数据发布日期', columns='全称', values='mean')

# 2. 拼接列名，实现 “全称+mean” 的效果
df_pivot.columns = [f"{col}+mean" for col in df_pivot.columns]

# 3. 重置索引，让日期重新变成普通列（可选）
df_pivot = df_pivot.reset_index()
df_pivot.to_excel('./Tong.xlsx', index=False)
# 查看转换后的结果
print(df_pivot)