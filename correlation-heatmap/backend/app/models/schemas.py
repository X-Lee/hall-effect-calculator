from __future__ import annotations

from pydantic import BaseModel
from typing import List, Optional


class UploadResponse(BaseModel):
    file_id: str
    columns: List[str]
    numeric_columns: List[str]
    row_count: int
    preview: List[list]


class GenerateRequest(BaseModel):
    file_id: str
    columns: List[str]
    method: str = "pearson"
    colormap: str = "RdBu_r"
    show_values: bool = True
    show_significance: bool = True
    significance_levels: List[float] = [0.05, 0.01, 0.001]
    figure_size: List[float] = [10, 8]
    font_size: int = 12
    title: str = "Correlation Matrix"
    mask_upper: bool = True
    vmin: float = -1.0
    vmax: float = 1.0
    annot_format: str = ".2f"
    target_column: Optional[str] = None
    lag_periods: int = 0
    lag_mode: str = "single"
    lag_range_start: int = 0
    lag_range_end: int = 10


class LagSweepResult(BaseModel):
    feature: str
    best_lag: int
    best_correlation: float
    correlations_by_lag: List[float]


class GenerateResponse(BaseModel):
    task_id: str
    image_base64: str
    correlation_matrix: List[List[float]]
    p_values: Optional[List[List[float]]] = None
    lag_sweep_results: Optional[List[LagSweepResult]] = None
