import uuid
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
import matplotlib

from ..models.schemas import UploadResponse, GenerateRequest, GenerateResponse
from ..services.data_parser import save_uploaded_file, parse_file, get_file_info, cleanup_old_files
from ..services.heatmap_gen import (
    compute_correlation, compute_pvalues, compute_lag_correlation,
    compute_lag_sweep, generate_heatmap, OUTPUT_DIR,
)

router = APIRouter(prefix="/api")


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No file provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in (".csv", ".xlsx", ".xls"):
        raise HTTPException(400, "Only CSV and Excel files are supported")

    cleanup_old_files()

    content = await file.read()
    file_id = save_uploaded_file(content, file.filename)
    df = parse_file(file_id)
    info = get_file_info(df)

    return UploadResponse(file_id=file_id, **info)


@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    try:
        df = parse_file(req.file_id)
    except FileNotFoundError:
        raise HTTPException(404, "File not found or expired")

    missing = [c for c in req.columns if c not in df.columns]
    if missing:
        raise HTTPException(400, f"Columns not found: {missing}")

    lag_sweep_results = None

    if req.target_column and req.target_column not in req.columns:
        raise HTTPException(400, f"目标列 '{req.target_column}' 必须在所选列中")

    try:
        if req.target_column and req.lag_mode == "sweep":
            lag_sweep_results = compute_lag_sweep(
                df, req.columns, req.target_column,
                req.lag_range_start, req.lag_range_end, req.method,
            )
            corr_matrix, _ = compute_lag_correlation(
                df, req.columns, req.target_column, req.lag_periods, req.method,
            )
        elif req.target_column and req.lag_periods > 0:
            corr_matrix, _ = compute_lag_correlation(
                df, req.columns, req.target_column, req.lag_periods, req.method,
            )
        else:
            corr_matrix, _ = compute_correlation(df, req.columns, req.method)
    except ValueError as e:
        raise HTTPException(400, str(e))

    pvalues = None
    if req.show_significance:
        pvalues = compute_pvalues(df, req.columns, req.method)

    title = req.title
    if req.target_column and req.lag_periods > 0:
        title += f"（滞后 {req.lag_periods} 期）"

    task_id, image_base64 = generate_heatmap(
        corr_matrix=corr_matrix,
        pvalues=pvalues,
        colormap=req.colormap,
        show_values=req.show_values,
        show_significance=req.show_significance,
        significance_levels=req.significance_levels,
        figure_size=req.figure_size,
        font_size=req.font_size,
        title=title,
        mask_upper=req.mask_upper,
        vmin=req.vmin,
        vmax=req.vmax,
        annot_format=req.annot_format,
    )

    return GenerateResponse(
        task_id=task_id,
        image_base64=image_base64,
        correlation_matrix=corr_matrix.values.tolist(),
        p_values=pvalues.tolist() if pvalues is not None else None,
        lag_sweep_results=lag_sweep_results,
    )


@router.get("/export/{task_id}")
async def export_image(task_id: str, format: str = Query("png", pattern="^(png|pdf)$"), dpi: int = Query(300)):
    if format == "png":
        path = OUTPUT_DIR / f"{task_id}.png"
        media_type = "image/png"
    else:
        path = OUTPUT_DIR / f"{task_id}.pdf"
        media_type = "application/pdf"

    if not path.exists():
        raise HTTPException(404, "Image not found or expired")

    return FileResponse(path, media_type=media_type, filename=f"heatmap.{format}")


@router.get("/colormaps")
async def get_colormaps():
    cmaps = [
        "RdBu_r", "coolwarm", "viridis", "plasma", "inferno",
        "magma", "cividis", "RdYlBu_r", "RdYlGn_r", "Spectral_r",
        "BrBG_r", "PiYG_r", "PRGn_r", "PuOr_r", "seismic",
    ]
    return {"colormaps": cmaps}


@router.post("/export-lag-data")
async def export_lag_data(req: GenerateRequest):
    try:
        df = parse_file(req.file_id)
    except FileNotFoundError:
        raise HTTPException(404, "File not found or expired")

    if not req.target_column:
        raise HTTPException(400, "未指定目标列")

    if req.target_column not in req.columns:
        raise HTTPException(400, f"目标列 '{req.target_column}' 必须在所选列中")

    try:
        _, subset = compute_lag_correlation(
            df, req.columns, req.target_column, req.lag_periods, req.method,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    buf = BytesIO()
    subset.to_excel(buf, index=False)
    buf.seek(0)

    filename = f"lag_data_{req.target_column}_lag{req.lag_periods}.xlsx"
    encoded_filename = quote(filename)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
        },
    )
