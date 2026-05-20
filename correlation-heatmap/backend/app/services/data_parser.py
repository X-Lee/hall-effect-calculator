import uuid
import os
from pathlib import Path

import pandas as pd

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def save_uploaded_file(file_content: bytes, filename: str) -> str:
    file_id = str(uuid.uuid4())
    ext = Path(filename).suffix.lower()
    save_path = UPLOAD_DIR / f"{file_id}{ext}"
    save_path.write_bytes(file_content)
    return file_id


def parse_file(file_id: str) -> pd.DataFrame:
    for ext in [".csv", ".xlsx", ".xls"]:
        path = UPLOAD_DIR / f"{file_id}{ext}"
        if path.exists():
            if ext == ".csv":
                return pd.read_csv(path)
            else:
                return pd.read_excel(path)
    raise FileNotFoundError(f"File not found: {file_id}")


def get_file_info(df: pd.DataFrame) -> dict:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    preview = df.head(5).fillna("").values.tolist()
    return {
        "columns": df.columns.tolist(),
        "numeric_columns": numeric_cols,
        "row_count": len(df),
        "preview": preview,
    }


def cleanup_old_files(max_age_hours: int = 1):
    import time

    now = time.time()
    for f in UPLOAD_DIR.iterdir():
        if f.is_file() and (now - f.stat().st_mtime) > max_age_hours * 3600:
            f.unlink()
