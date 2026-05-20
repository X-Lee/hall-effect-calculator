import os

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["NO_PROXY"] = "hf-mirror.com"
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForCausalLM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

# ==================== 配置区域 ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "true.csv")          # 输入数据文件路径
OUTPUT_DIR = SCRIPT_DIR                                     # 输出目录（图片和CSV保存位置）
LOCAL_MODEL_DIR = os.path.join(SCRIPT_DIR, "sundial-base-128m")  # 本地模型目录
FORECAST_LENGTH = 96    # 预测长度（96点 = 1天，每点15分钟）
NUM_SAMPLES = 20        # 模型采样次数（多次预测取均值，越大越稳定但越慢）
MAX_LOOKBACK = 2880     # 最大回看长度（2880点 = 30天 * 96点/天）

# 数据列名配置（根据实际CSV字段名修改）
COL_USER_ID = "CONS_ID"       # 用户编号列名
COL_DATE = "DATA_DATE"        # 日期列名
DATE_FORMAT = "%d/%m/%Y"      # 日期格式（如 1/10/2023 用 %d/%m/%Y，2023-10-01 用 %Y-%m-%d）
COL_VALUES_PREFIX = "P"       # 负荷值列名前缀（P1~P96 则填 "P"）
NUM_POINTS_PER_DAY = 96       # 每天的数据点数（与 P 列数量一致）
# ==================================================


def load_and_preprocess_data(filepath):
    df = pd.read_csv(filepath)
    df.columns = [c.strip().strip('"') for c in df.columns]
    df[COL_DATE] = pd.to_datetime(df[COL_DATE], format=DATE_FORMAT)
    p_cols = [f"{COL_VALUES_PREFIX}{i}" for i in range(1, NUM_POINTS_PER_DAY + 1)]
    for col in p_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.sort_values([COL_USER_ID, COL_DATE]).reset_index(drop=True)
    return df, p_cols


def detect_and_replace_outliers(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    mask = (series < lower) | (series > upper)
    series[mask] = np.nan
    series = series.interpolate(method="linear", limit_direction="both")
    return series


def process_user(user_df, p_cols):
    user_df = user_df.sort_values(COL_DATE).reset_index(drop=True)
    values = user_df[p_cols].values.flatten()
    values = pd.Series(values)
    values = values.interpolate(method="linear", limit_direction="both")
    values = detect_and_replace_outliers(values)
    values = values.fillna(method="ffill").fillna(method="bfill").fillna(0)
    return values.values


def mape(y_true, y_pred):
    mask = y_true != 0
    if mask.sum() == 0:
        return 0.0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def main():
    print("Loading data...")
    df, p_cols = load_and_preprocess_data(DATA_PATH)
    user_ids = df[COL_USER_ID].unique()
    print(f"Total users: {len(user_ids)}")

    print("Loading Sundial model...")
    if os.path.isdir(LOCAL_MODEL_DIR) and os.listdir(LOCAL_MODEL_DIR):
        print(f"Loading from local: {LOCAL_MODEL_DIR}")
        model_path = LOCAL_MODEL_DIR
    else:
        print("Local model not found, downloading from hf-mirror.com...")
        model_path = "thuml/sundial-base-128m"
    model = AutoModelForCausalLM.from_pretrained(
        model_path, trust_remote_code=True
    )
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    print(f"Model loaded on {device}")

    results = []

    for idx, uid in enumerate(user_ids):
        user_df = df[df[COL_USER_ID] == uid].copy()
        if len(user_df) < 2:
            continue

        train_df = user_df.iloc[:-1]
        test_df = user_df.iloc[-1:]

        train_series = process_user(train_df, p_cols)
        test_values = test_df[p_cols].values.flatten().astype(np.float64)

        scaler = MinMaxScaler()
        train_scaled = scaler.fit_transform(train_series.reshape(-1, 1)).flatten()

        lookback = train_scaled[-MAX_LOOKBACK:] if len(train_scaled) > MAX_LOOKBACK else train_scaled
        # Ensure length is divisible by patch_size (16)
        patch_size = 16
        trim_len = (len(lookback) // patch_size) * patch_size
        lookback = lookback[-trim_len:]

        input_tensor = torch.tensor(lookback, dtype=torch.float32).unsqueeze(0).to(device)

        with torch.no_grad():
            output = model.generate(
                input_tensor, max_new_tokens=FORECAST_LENGTH, num_samples=NUM_SAMPLES
            )

        pred_scaled = output.mean(dim=1).squeeze().cpu().numpy()
        pred_values = scaler.inverse_transform(pred_scaled.reshape(-1, 1)).flatten()

        user_mse = mean_squared_error(test_values, pred_values)
        user_mape = mape(test_values, pred_values)
        user_r2 = r2_score(test_values, pred_values)

        pred_date = test_df[COL_DATE].iloc[0]

        results.append({
            "USER_ID": uid,
            "PRED_DATE": pred_date,
            "MSE": user_mse,
            "MAPE": user_mape,
            "R2": user_r2,
            "true": test_values,
            "pred": pred_values,
        })

        if (idx + 1) % 50 == 0 or (idx + 1) == len(user_ids):
            print(f"Progress: {idx + 1}/{len(user_ids)} users processed")

    print("\n" + "=" * 60)
    print("Evaluation Results")
    print("=" * 60)

    mse_list = [r["MSE"] for r in results]
    mape_list = [r["MAPE"] for r in results]
    r2_list = [r["R2"] for r in results]

    print(f"{'User':<20} {'MSE':<12} {'MAPE(%)':<12} {'R2':<12}")
    print("-" * 56)
    for r in results[:20]:
        print(f"{r['USER_ID']:<20} {r['MSE']:<12.4f} {r['MAPE']:<12.2f} {r['R2']:<12.4f}")
    if len(results) > 20:
        print(f"... ({len(results) - 20} more users)")

    print("-" * 56)
    print(f"{'Average':<20} {np.mean(mse_list):<12.4f} {np.mean(mape_list):<12.2f} {np.mean(r2_list):<12.4f}")
    print(f"{'Std':<20} {np.std(mse_list):<12.4f} {np.std(mape_list):<12.2f} {np.std(r2_list):<12.4f}")

    # 保存汇总指标 CSV
    metrics_df = pd.DataFrame([{
        COL_USER_ID: r["USER_ID"],
        "PRED_DATE": r["PRED_DATE"].strftime("%Y-%m-%d"),
        "MSE": r["MSE"],
        "MAPE": r["MAPE"],
        "R2": r["R2"],
    } for r in results])
    metrics_path = os.path.join(OUTPUT_DIR, "prediction_metrics.csv")
    metrics_df.to_csv(metrics_path, index=False)
    print(f"\nMetrics saved to: {metrics_path}")

    # 保存逐点预测详情 CSV
    p_cols_out = [f"{COL_VALUES_PREFIX}{i}" for i in range(1, FORECAST_LENGTH + 1)]
    detail_rows = []
    for r in results:
        date_str = r["PRED_DATE"].strftime("%Y-%m-%d")
        true_row = {COL_USER_ID: r["USER_ID"], "PRED_DATE": date_str, "TYPE": "TRUE"}
        pred_row = {COL_USER_ID: r["USER_ID"], "PRED_DATE": date_str, "TYPE": "PRED"}
        for i, col in enumerate(p_cols_out):
            true_row[col] = r["true"][i]
            pred_row[col] = r["pred"][i]
        detail_rows.append(true_row)
        detail_rows.append(pred_row)
    details_df = pd.DataFrame(detail_rows)
    details_path = os.path.join(OUTPUT_DIR, "prediction_details.csv")
    details_df.to_csv(details_path, index=False)
    print(f"Details saved to: {details_path}")

    # 每个用户单独生成一张图
    plot_dir = os.path.join(OUTPUT_DIR, "user_plots")
    os.makedirs(plot_dir, exist_ok=True)
    for r in results:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(r["true"], label="True", linewidth=1.5)
        ax.plot(r["pred"], label="Predicted", linewidth=1.5, linestyle="--")
        ax.set_xlabel("Time Point (15min)")
        ax.set_ylabel("Load")
        ax.set_title(f"User: {r['USER_ID']}  Date: {r['PRED_DATE'].strftime('%Y-%m-%d')}")
        ax.legend(loc="upper right")
        ax.grid(True, alpha=0.3)
        text_str = f"MSE={r['MSE']:.4f}  MAPE={r['MAPE']:.2f}%  R2={r['R2']:.4f}"
        ax.text(0.02, 0.95, text_str, transform=ax.transAxes, fontsize=9,
                verticalalignment="top", bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
        plt.tight_layout()
        plt.savefig(os.path.join(plot_dir, f"{r['USER_ID']}.png"), dpi=100)
        plt.close()
    print(f"User plots saved to: {plot_dir}/ ({len(results)} files)")

    # 全局指标分布图
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    axes[0].hist(mse_list, bins=30, edgecolor="black", alpha=0.7)
    axes[0].set_title("MSE Distribution")
    axes[0].set_xlabel("MSE")
    axes[0].set_ylabel("Count")

    axes[1].hist(mape_list, bins=30, edgecolor="black", alpha=0.7, color="orange")
    axes[1].set_title("MAPE(%) Distribution")
    axes[1].set_xlabel("MAPE(%)")
    axes[1].set_ylabel("Count")

    axes[2].hist(r2_list, bins=30, edgecolor="black", alpha=0.7, color="green")
    axes[2].set_title("R2 Distribution")
    axes[2].set_xlabel("R2")
    axes[2].set_ylabel("Count")

    plt.suptitle("Evaluation Metrics Distribution Across Users", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "metrics_distribution.png"), dpi=150)
    plt.close()
    print(f"Metrics distribution plot saved to: {OUTPUT_DIR}/metrics_distribution.png")


if __name__ == "__main__":
    main()
