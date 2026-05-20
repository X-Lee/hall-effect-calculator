import uuid
import base64
import platform
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple, List

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from scipy import stats


def _configure_chinese_font():
    if platform.system() == "Windows":
        font_candidates = ["Microsoft YaHei", "SimHei", "SimSun", "KaiTi"]
    else:
        font_candidates = ["WenQuanYi Zen Hei", "WenQuanYi Micro Hei", "Noto Sans CJK SC", "SimHei"]

    available_fonts = {f.name for f in fm.fontManager.ttflist}

    chosen_font = None
    for font in font_candidates:
        if font in available_fonts:
            chosen_font = font
            break

    if chosen_font:
        plt.rcParams["font.sans-serif"] = [chosen_font] + plt.rcParams["font.sans-serif"]
    else:
        cjk_fonts = [f.name for f in fm.fontManager.ttflist if any(
            kw in f.name.lower() for kw in ["hei", "song", "kai", "cjk", "chinese", "wqy", "noto"]
        )]
        if cjk_fonts:
            plt.rcParams["font.sans-serif"] = [cjk_fonts[0]] + plt.rcParams["font.sans-serif"]

    plt.rcParams["axes.unicode_minus"] = False


_configure_chinese_font()

OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


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

    return pvals


def compute_lag_correlation(
    df: pd.DataFrame,
    columns: list,
    target_column: str,
    lag_periods: int,
    method: str,
):
    subset = df[columns].copy()

    if lag_periods > 0:
        subset[target_column] = subset[target_column].shift(-lag_periods)

    subset = subset.dropna()

    if len(subset) < 3:
        raise ValueError(
            f"应用滞后={lag_periods}后数据不足，仅剩{len(subset)}行（至少需要3行）"
        )

    corr_matrix = subset.corr(method=method)
    return corr_matrix, subset


def compute_lag_sweep(
    df: pd.DataFrame,
    columns: list,
    target_column: str,
    lag_start: int,
    lag_end: int,
    method: str,
) -> List[dict]:
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
            "feature": feature,
            "best_lag": best_lag,
            "best_correlation": round(best_corr, 4),
            "correlations_by_lag": [round(c, 4) if not np.isnan(c) else None for c in correlations],
        })

    return results


def significance_stars(p: float, levels: list[float]) -> str:
    sorted_levels = sorted(levels)
    if p < sorted_levels[0]:
        return "***"
    if p < sorted_levels[1]:
        return "**"
    if p < sorted_levels[2]:
        return "*"
    return ""


def generate_heatmap(
    corr_matrix: pd.DataFrame,
    pvalues: Optional[np.ndarray],
    colormap: str = "RdBu_r",
    show_values: bool = True,
    show_significance: bool = True,
    significance_levels: list = None,
    figure_size: list = None,
    font_size: int = 12,
    title: str = "Correlation Matrix",
    mask_upper: bool = True,
    vmin: float = -1.0,
    vmax: float = 1.0,
    annot_format: str = ".2f",
    dpi: int = 100,
) -> Tuple[str, str]:
    if significance_levels is None:
        significance_levels = [0.001, 0.01, 0.05]
    if figure_size is None:
        figure_size = [10, 8]

    fig, ax = plt.subplots(figsize=(figure_size[0], figure_size[1]))

    mask = None
    if mask_upper:
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

    annot = None
    if show_values:
        n = len(corr_matrix)
        annot = np.empty((n, n), dtype=object)
        for i in range(n):
            for j in range(n):
                val = corr_matrix.iloc[i, j]
                text = f"{val:{annot_format}}"
                if show_significance and pvalues is not None and i != j:
                    stars = significance_stars(pvalues[i, j], significance_levels)
                    text += stars
                annot[i, j] = text

    sns.heatmap(
        corr_matrix,
        mask=mask,
        annot=annot if show_values else False,
        fmt="" if show_values else annot_format,
        cmap=colormap,
        vmin=vmin,
        vmax=vmax,
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        ax=ax,
        annot_kws={"size": font_size - 2},
    )

    ax.set_title(title, fontsize=font_size + 2, pad=20)
    ax.tick_params(labelsize=font_size)
    plt.tight_layout()

    task_id = str(uuid.uuid4())

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")

    output_path = OUTPUT_DIR / f"{task_id}.png"
    fig.savefig(output_path, format="png", dpi=300, bbox_inches="tight")

    pdf_path = OUTPUT_DIR / f"{task_id}.pdf"
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")

    plt.close(fig)

    return task_id, f"data:image/png;base64,{image_base64}"
