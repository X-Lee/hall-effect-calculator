"""
相关性分析独立脚本
用法:
    python correlation_analysis.py data.xlsx --columns 温度 压力 产量 --method pearson --output result.xlsx
    python correlation_analysis.py data.xlsx --columns 温度 压力 产量 --target 产量 --lag 3
    python correlation_analysis.py data.xlsx --columns 温度 压力 产量 --target 产量 --sweep 0 10
"""
import argparse
import platform
import sys
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns


def _configure_chinese_font():
    if platform.system() == "Windows":
        font_candidates = ["Microsoft YaHei", "SimHei", "SimSun", "KaiTi"]
    else:
        font_candidates = ["WenQuanYi Zen Hei", "WenQuanYi Micro Hei", "Noto Sans CJK SC", "SimHei"]

    available_fonts = {f.name for f in fm.fontManager.ttflist}
    for font in font_candidates:
        if font in available_fonts:
            plt.rcParams["font.sans-serif"] = [font] + plt.rcParams["font.sans-serif"]
            break
    else:
        cjk_fonts = [f.name for f in fm.fontManager.ttflist if any(
            kw in f.name.lower() for kw in ["hei", "song", "kai", "cjk", "chinese", "wqy", "noto"]
        )]
        if cjk_fonts:
            plt.rcParams["font.sans-serif"] = [cjk_fonts[0]] + plt.rcParams["font.sans-serif"]

    plt.rcParams["axes.unicode_minus"] = False


_configure_chinese_font()


def compute_correlation(df: pd.DataFrame, columns: list, method: str):
    subset = df[columns].dropna()
    corr_matrix = subset.corr(method=method)
    return corr_matrix, subset


def compute_pvalues(df: pd.DataFrame, columns: list, method: str):
    n = len(columns)
    pvals = np.ones((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            x = df[columns[i]].dropna()
            y = df[columns[j]].dropna()
            common = x.index.intersection(y.index)
            if len(common) < 3:
                pvals[i, j] = pvals[j, i] = 1.0
                continue

            if method == "pearson":
                _, p = stats.pearsonr(x[common], y[common])
            elif method == "spearman":
                _, p = stats.spearmanr(x[common], y[common])
            else:
                _, p = stats.kendalltau(x[common], y[common])
            pvals[i, j] = pvals[j, i] = p

    return pd.DataFrame(pvals, index=columns, columns=columns)


def compute_lag_correlation(df: pd.DataFrame, columns: list, target_column: str, lag_periods: int, method: str):
    subset = df[columns].copy()

    if lag_periods > 0:
        subset[target_column] = subset[target_column].shift(-lag_periods)

    subset = subset.dropna()

    if len(subset) < 3:
        raise ValueError(f"应用滞后={lag_periods}后数据不足，仅剩{len(subset)}行（至少需要3行）")

    corr_matrix = subset.corr(method=method)
    return corr_matrix, subset


def compute_lag_sweep(df: pd.DataFrame, columns: list, target_column: str, lag_start: int, lag_end: int, method: str):
    feature_columns = [c for c in columns if c != target_column]
    results = []

    for feature in feature_columns:
        correlations = []
        for lag in range(lag_start, lag_end + 1):
            subset = df[[feature, target_column]].copy()
            if lag > 0:
                subset[target_column] = subset[target_column].shift(-lag)
            subset = subset.dropna()

            if len(subset) < 3:
                correlations.append(float("nan"))
                continue

            corr_val = subset.corr(method=method).iloc[0, 1]
            correlations.append(float(corr_val))

        valid_corrs = [(i + lag_start, c) for i, c in enumerate(correlations) if not np.isnan(c)]
        if valid_corrs:
            best_lag, best_corr = max(valid_corrs, key=lambda x: abs(x[1]))
        else:
            best_lag, best_corr = 0, 0.0

        results.append({
            "影响因素": feature,
            "最优滞后期": best_lag,
            "最强相关系数": round(best_corr, 4),
            **{f"lag={lag}": round(c, 4) if not np.isnan(c) else None
               for lag, c in zip(range(lag_start, lag_end + 1), correlations)},
        })

    return pd.DataFrame(results)


def read_data(filepath: str) -> pd.DataFrame:
    ext = filepath.rsplit(".", 1)[-1].lower()
    if ext == "csv":
        return pd.read_csv(filepath)
    elif ext in ("xlsx", "xls"):
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"不支持的文件格式: .{ext}，仅支持 csv/xlsx/xls")


def plot_heatmap(corr_matrix: pd.DataFrame, pval_matrix: pd.DataFrame, title: str, output_path: str):
    n = len(corr_matrix)
    fig, ax = plt.subplots(figsize=(max(8, n * 1.2), max(6, n * 1.0)))

    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

    annot = np.empty((n, n), dtype=object)
    for i in range(n):
        for j in range(n):
            val = corr_matrix.iloc[i, j]
            text = f"{val:.2f}"
            p = pval_matrix.iloc[i, j]
            if i != j:
                if p < 0.001:
                    text += "***"
                elif p < 0.01:
                    text += "**"
                elif p < 0.05:
                    text += "*"
            annot[i, j] = text

    sns.heatmap(
        corr_matrix,
        mask=mask,
        annot=annot,
        fmt="",
        cmap="RdBu_r",
        vmin=-1, vmax=1,
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        ax=ax,
        annot_kws={"size": 10},
    )
    ax.set_title(title, fontsize=14, pad=20)
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  热力图已保存: {output_path}")


def plot_lag_sweep(sweep_df: pd.DataFrame, target_column: str, lag_start: int, lag_end: int, output_path: str):
    lag_cols = [c for c in sweep_df.columns if c.startswith("lag=")]
    lags = list(range(lag_start, lag_end + 1))

    fig, ax = plt.subplots(figsize=(10, 6))

    for _, row in sweep_df.iterrows():
        values = [row[c] for c in lag_cols]
        valid_lags = [l for l, v in zip(lags, values) if v is not None and not (isinstance(v, float) and np.isnan(v))]
        valid_vals = [v for v in values if v is not None and not (isinstance(v, float) and np.isnan(v))]
        ax.plot(valid_lags, valid_vals, marker="o", markersize=5, label=row["影响因素"])

        best_lag = row["最优滞后期"]
        best_corr = row["最强相关系数"]
        ax.scatter([best_lag], [best_corr], s=120, zorder=5, edgecolors="red", facecolors="none", linewidths=2)

    ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("滞后期数", fontsize=12)
    ax.set_ylabel(f"与 {target_column} 的相关系数", fontsize=12)
    ax.set_title(f"滞后相关性搜索（目标: {target_column}）", fontsize=14)
    ax.legend(loc="best", fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  滞后搜索图已保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="相关性分析工具（支持滞后）")
    parser.add_argument("file", help="输入数据文件路径（Excel 或 CSV）")
    parser.add_argument("--columns", nargs="+", help="参与计算的列名（不指定则使用所有数值列）")
    parser.add_argument("--method", default="pearson", choices=["pearson", "spearman", "kendall"], help="相关性方法")
    parser.add_argument("--target", help="目标列名（滞后变量）")
    parser.add_argument("--lag", type=int, default=0, help="滞后期数")
    parser.add_argument("--sweep", nargs=2, type=int, metavar=("START", "END"), help="最优滞后搜索范围")
    parser.add_argument("--output", "-o", default="correlation_result.xlsx", help="输出文件路径")
    parser.add_argument("--no-plot", action="store_true", help="不生成图片")

    args = parser.parse_args()

    print(f"读取文件: {args.file}")
    df = read_data(args.file)
    print(f"数据维度: {df.shape[0]} 行 x {df.shape[1]} 列")

    if args.columns:
        columns = args.columns
        missing = [c for c in columns if c not in df.columns]
        if missing:
            print(f"错误: 以下列不存在: {missing}")
            print(f"可用列: {list(df.columns)}")
            sys.exit(1)
    else:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
        print(f"自动选择数值列: {columns}")

    if len(columns) < 2:
        print("错误: 至少需要2个数值列")
        sys.exit(1)

    if args.target:
        if args.target not in df.columns:
            print(f"错误: 目标列 '{args.target}' 不存在")
            print(f"可用列: {list(df.columns)}")
            sys.exit(1)
        if args.target not in columns:
            columns.append(args.target)
            print(f"已自动将目标列 '{args.target}' 加入分析列")

    with pd.ExcelWriter(args.output, engine="openpyxl") as writer:
        # 基础相关矩阵
        if args.target and (args.lag > 0):
            print(f"计算滞后相关性: 目标列={args.target}, 滞后={args.lag}期, 方法={args.method}")
            corr_matrix, lag_subset = compute_lag_correlation(df, columns, args.target, args.lag, args.method)
            lag_subset.to_excel(writer, sheet_name="滞后数据", index=False)
            print(f"  滞后后剩余 {len(lag_subset)} 行")
        else:
            print(f"计算相关矩阵: 方法={args.method}")
            corr_matrix, _ = compute_correlation(df, columns, args.method)

        corr_matrix.to_excel(writer, sheet_name="相关矩阵")
        print(f"  相关矩阵 ({len(columns)}x{len(columns)}) 已计算")

        # P值矩阵
        pval_matrix = compute_pvalues(df, columns, args.method)
        pval_matrix.to_excel(writer, sheet_name="P值矩阵")

        # 最优滞后搜索
        if args.target and args.sweep:
            lag_start, lag_end = args.sweep
            print(f"最优滞后搜索: 目标列={args.target}, 范围=[{lag_start}, {lag_end}]")
            sweep_df = compute_lag_sweep(df, columns, args.target, lag_start, lag_end, args.method)
            sweep_df.to_excel(writer, sheet_name="最优滞后", index=False)
            print("  最优滞后结果:")
            for _, row in sweep_df.iterrows():
                print(f"    {row['影响因素']}: 最优滞后={row['最优滞后期']}期, 相关系数={row['最强相关系数']}")

    print(f"\n结果已导出到: {args.output}")

    # 画图
    if not args.no_plot:
        output_stem = Path(args.output).stem

        # 热力图
        heatmap_title = f"相关矩阵（{args.method}）"
        if args.target and args.lag > 0:
            heatmap_title += f" - {args.target} 滞后{args.lag}期"
        plot_heatmap(corr_matrix, pval_matrix, heatmap_title, f"{output_stem}_heatmap.png")

        # 滞后搜索折线图
        if args.target and args.sweep:
            plot_lag_sweep(sweep_df, args.target, args.sweep[0], args.sweep[1], f"{output_stem}_lag_sweep.png")


if __name__ == "__main__":
    main()
