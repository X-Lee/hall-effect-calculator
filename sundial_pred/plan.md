# Sundial 时序大模型负荷预测 — 使用与维护手册

## 一、项目概述

基于 Sundial 时序大模型（thuml/sundial-base-128m）的电力负荷预测程序。对每个用户独立预测未来若干时间点的负荷值，输出预测结果 CSV 和可视化图片。

- 脚本文件：`sundial_process.py`
- 模型：Sundial-base-128M（零样本时序预测，无需训练）
- 预测方式：输入历史负荷序列 → 模型生成未来负荷预测

## 二、运行环境

| 项目 | 要求 |
|------|------|
| Python | `D:/ProgramData/miniconda3/envs/llm_sql/python.exe` |
| transformers | **4.40.1**（必须，不可高于4.40.x或低于4.39.0） |
| torch | 支持 CUDA 的版本（CPU 也可运行，但较慢） |
| 其他依赖 | pandas, numpy, scikit-learn, matplotlib |

### 安装依赖

```bash
D:/ProgramData/miniconda3/envs/llm_sql/python.exe -m pip install transformers==4.40.1 torch pandas numpy scikit-learn matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

## 三、输入数据要求

输入文件为 CSV 格式，必须包含以下字段：

| 字段 | 说明 |
|------|------|
| CONS_ID | 用户编号（唯一标识） |
| DATA_DATE | 日期，格式 `d/m/yyyy`（如 1/10/2023） |
| P1 ~ P96 | 每日96个时间点的负荷值（每15分钟一个点） |

- 每个用户至少需要 2 天数据（1天训练 + 1天验证）
- 数据按用户分组、按日期排序后拼接为连续时序
- 缺失值自动线性插值处理
- 异常值自动 IQR 法则检测并替换

## 四、配置参数说明

脚本顶部 `配置区域` 中的参数：

```python
# ==================== 配置区域 ====================
DATA_PATH              # 输入数据文件路径
OUTPUT_DIR             # 输出目录（图片和CSV保存位置）
LOCAL_MODEL_DIR        # 本地模型目录路径
FORECAST_LENGTH        # 预测长度（点数）
NUM_SAMPLES            # 模型采样次数（多次预测取均值，越大越稳定但越慢）
MAX_LOOKBACK           # 最大回看长度（点数）

# 数据列名配置
COL_USER_ID            # 用户编号列名
COL_DATE               # 日期列名
DATE_FORMAT            # 日期格式
COL_VALUES_PREFIX      # 负荷值列名前缀
NUM_POINTS_PER_DAY     # 每天的数据点数
# ==================================================
```

### 参数详解

| 参数 | 默认值 | 说明 | 修改建议 |
|------|--------|------|----------|
| `DATA_PATH` | `true.csv` | 输入数据文件 | 替换为新数据文件路径即可 |
| `OUTPUT_DIR` | 脚本所在目录 | 结果输出位置 | 可改为任意目录路径 |
| `LOCAL_MODEL_DIR` | `sundial-base-128m` | 模型权重目录 | 如使用其他模型，修改此路径 |
| `FORECAST_LENGTH` | 96 | 预测未来多少个点 | 96=1天，192=2天，48=半天 |
| `NUM_SAMPLES` | 20 | 采样次数取均值 | 增大更稳定但更慢，建议10~50 |
| `MAX_LOOKBACK` | 2880 | 输入历史最大长度 | 2880=30天，增大可能提升精度但更慢 |
| `COL_USER_ID` | `"CONS_ID"` | CSV中用户编号的列名 | 根据实际数据修改 |
| `COL_DATE` | `"DATA_DATE"` | CSV中日期的列名 | 根据实际数据修改 |
| `DATE_FORMAT` | `"%d/%m/%Y"` | 日期解析格式 | 如 `2023-10-01` 改为 `"%Y-%m-%d"` |
| `COL_VALUES_PREFIX` | `"P"` | 负荷值列名前缀 | 如列名为 V1~V96 则改为 `"V"` |
| `NUM_POINTS_PER_DAY` | 96 | 每天数据点数 | 与负荷值列数量一致 |

## 五、如何修改预测场景

### 场景1：更换输入数据

修改 `DATA_PATH` 并根据新数据的列名调整配置：
```python
DATA_PATH = os.path.join(SCRIPT_DIR, "new_data.csv")

# 如果新数据的列名不同，同步修改：
COL_USER_ID = "USER_NO"          # 用户编号列名
COL_DATE = "DATE"                 # 日期列名
DATE_FORMAT = "%Y-%m-%d"          # 日期格式
COL_VALUES_PREFIX = "V"           # 如列名为 V1~V96
NUM_POINTS_PER_DAY = 96           # 每天点数
```

只要数据满足"每行一天、每天N个点"的结构，修改这几个配置即可适配。

### 场景2：修改预测窗口（输出长度）

修改 `FORECAST_LENGTH`：
```python
FORECAST_LENGTH = 192   # 预测未来2天（192个15分钟点）
```

注意：预测越长精度越低，建议不超过 336（3.5天）。

### 场景3：修改输入窗口（回看长度）

修改 `MAX_LOOKBACK`：
```python
MAX_LOOKBACK = 4800   # 使用最近50天的数据作为输入
```

- 必须是 16 的整数倍（脚本会自动裁剪，但建议直接设为16的倍数）
- 越长模型能看到更多历史模式，但推理更慢、显存占用更大
- 建议范围：960（10天）~ 4800（50天）

### 场景4：调整采样次数（NUM_SAMPLES）

Sundial 是概率预测模型，每次预测同一段未来会给出略有不同的结果。`NUM_SAMPLES` 就是让模型"预测N次"然后取平均值。次数越多结果越稳定，但耗时线性增长。

```python
NUM_SAMPLES = 50   # 更多采样，结果更稳定
```

- 快速测试用 5~10
- 正式预测用 20~50

### 场景5：只预测部分用户

在 `main()` 函数中，修改用户循环：
```python
# 只预测前10个用户（测试用）
for idx, uid in enumerate(user_ids[:10]):
```

或指定用户列表：
```python
target_users = [3400100000758, 3400100002625]
for idx, uid in enumerate(target_users):
    user_df = df[df["CONS_ID"] == uid].copy()
```

## 六、输出文件说明

| 文件 | 说明 |
|------|------|
| `prediction_metrics.csv` | 每用户汇总指标：CONS_ID, PRED_DATE, MSE, MAPE, R2 |
| `prediction_details.csv` | 逐点预测结果，每用户2行（TRUE+PRED），列为 CONS_ID, PRED_DATE, TYPE, P1~P96 |
| `user_plots/{CONS_ID}.png` | 每用户独立折线图，标注 MSE/MAPE/R² |
| `metrics_distribution.png` | 全部用户的 MSE/MAPE/R² 分布直方图 |

### prediction_details.csv 格式示例

```
CONS_ID,PRED_DATE,TYPE,P1,P2,...,P96
3400100000758,2023-12-18,TRUE,120.5,118.3,...,125.0
3400100000758,2023-12-18,PRED,119.2,117.8,...,123.5
```

## 七、执行命令

```bash
D:/ProgramData/miniconda3/envs/llm_sql/python.exe sundial_process.py
```

## 八、常见问题

### Q: 报错 ImportError: cannot import name 'EosTokenCriteria'
A: transformers 版本过低，需安装 4.40.1：
```bash
pip install transformers==4.40.1
```

### Q: 报错 standardize_cache_format 相关
A: transformers 版本过高（>4.40），需降级到 4.40.1。

### Q: 模型下载超时
A: 使用本地模型目录。将模型文件放在 `sundial-base-128m/` 子目录下，脚本会自动检测并从本地加载。

### Q: 显存不足 (CUDA out of memory)
A: 减小 `MAX_LOOKBACK`（如改为 960），或设置 CPU 运行：
```python
device = torch.device("cpu")
```

### Q: 想用其他 Sundial 模型（如更大的版本）
A: 下载模型到本地目录，修改 `LOCAL_MODEL_DIR` 指向新目录即可。
