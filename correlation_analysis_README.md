# correlation_analysis.py 使用说明

## 功能简介

本脚本用于对 Excel/CSV 数据进行相关性分析，支持：

- 计算 Pearson / Spearman / Kendall 相关矩阵及 P 值
- 滞后相关性分析（目标变量对影响因素存在时间滞后）
- 最优滞后期自动搜索
- 结果导出为 Excel（多 sheet）
- 自动生成热力图和滞后搜索折线图

---

## 环境依赖

```
pandas >= 1.5
numpy >= 1.24
scipy >= 1.10
matplotlib >= 3.7
seaborn >= 0.13
openpyxl >= 3.1
```

安装：
```bash
pip install pandas numpy scipy matplotlib seaborn openpyxl
```

---

## 使用方法

### 基本语法

```bash
python correlation_analysis.py <数据文件> [参数]
```

### 示例

```bash
# 1. 基础相关性分析（自动选择所有数值列）
python correlation_analysis.py data.xlsx

# 2. 指定列和方法
python correlation_analysis.py data.xlsx --columns 温度 压力 产量 --method spearman

# 3. 滞后相关性（目标列滞后3期）
python correlation_analysis.py data.xlsx --columns 温度 压力 产量 --target 产量 --lag 3

# 4. 最优滞后搜索（搜索范围 0~10 期）
python correlation_analysis.py data.xlsx --columns 温度 压力 --target 产量 --sweep 0 10

# 5. 同时使用固定滞后和搜索
python correlation_analysis.py data.xlsx --columns 温度 压力 --target 产量 --lag 3 --sweep 0 10

# 6. 指定输出文件名，不生成图片
python correlation_analysis.py data.xlsx --target 产量 --lag 3 -o my_result.xlsx --no-plot
```

---

## 参数详解

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `file` | 是 | - | 输入数据文件路径（支持 .xlsx / .xls / .csv） |
| `--columns` | 否 | 所有数值列 | 参与分析的列名，空格分隔 |
| `--method` | 否 | pearson | 相关性方法：pearson / spearman / kendall |
| `--target` | 否 | - | 目标列名（滞后变量），不指定则不做滞后分析 |
| `--lag` | 否 | 0 | 滞后期数，需配合 --target 使用 |
| `--sweep START END` | 否 | - | 最优滞后搜索范围，如 `--sweep 0 10` |
| `--output` / `-o` | 否 | correlation_result.xlsx | 输出 Excel 文件路径 |
| `--no-plot` | 否 | False | 添加此参数则不生成图片 |

**注意事项：**
- `--target` 指定的列如果不在 `--columns` 中，脚本会自动将其加入
- 列名包含空格时需要用引号包裹，如 `"相对价格 指数铜+mean"`
- `--lag` 和 `--sweep` 可以同时使用

---

## 输出说明

### Excel 文件（多 sheet）

| Sheet 名称 | 生成条件 | 内容 |
|------------|----------|------|
| 相关矩阵 | 始终生成 | N×N 相关系数矩阵 |
| P值矩阵 | 始终生成 | N×N 显著性 P 值矩阵 |
| 滞后数据 | --target + --lag > 0 | 滞后处理后的原始数据（已对齐、已去除 NaN 行） |
| 最优滞后 | --target + --sweep | 每个因素的最优滞后期、最强相关系数、各期相关系数 |

### 图片文件

| 文件名 | 生成条件 | 内容 |
|--------|----------|------|
| `{output_stem}_heatmap.png` | 默认生成 | 相关性热力图（下三角，带显著性星号标注） |
| `{output_stem}_lag_sweep.png` | --target + --sweep | 滞后搜索折线图（红圈标记最优点） |

显著性标注规则：
- `***` : P < 0.001
- `**` : P < 0.01
- `*` : P < 0.05

---

## 滞后相关性原理

### 什么是滞后相关性

当因素 X 在时刻 t 发生变化，目标 Y 在时刻 t+k 才体现效果时，直接计算 X 和 Y 的相关性会低估真实关联。

滞后相关性通过将目标列 Y 向前平移 k 期（即计算 corr(X_t, Y_{t+k})），使因果对齐后再计算相关系数。

### 固定滞后模式

指定一个滞后期数 k，将目标列平移后计算完整的相关矩阵。

```
原始:  X = [x1, x2, x3, x4, x5, x6]
       Y = [y1, y2, y3, y4, y5, y6]

lag=2: X = [x1, x2, x3, x4]
       Y = [y3, y4, y5, y6]   （Y 向前平移2期，末尾截断）
```

### 最优滞后搜索模式

对每个因素列，遍历指定范围内的所有滞后期数，找出使相关系数绝对值最大的滞后期。

---

## 常见问题

### Q: 列名包含空格怎么办？
用引号包裹：
```bash
--columns "相对价格 指数铜+mean" "市场价格 环氧树脂+mean"
```

### Q: 提示 "目标列不存在"？
检查列名是否完全匹配（包括空格、加号等特殊字符）。可以先不指定 --columns 运行一次，脚本会打印所有可用列名。

### Q: 滞后后数据不足？
数据行数必须大于滞后期数 + 3。例如 32 行数据最多支持 lag=29（但实际有意义的滞后期通常远小于数据长度的一半）。

### Q: 图片中文显示为方块？
确保系统安装了中文字体（Windows 默认有微软雅黑，Linux 需安装 `fonts-wqy-zenhei`）。

### Q: 如何只看某几列与目标的关系？
```bash
python correlation_analysis.py data.xlsx --columns 因素A 因素B --target 目标Y --sweep 0 10
```
脚本会自动将目标列加入分析。
