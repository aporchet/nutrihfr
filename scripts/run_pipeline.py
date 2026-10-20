"""Relance tout le pipeline depuis les données brutes.

Usage :  python scripts/run_pipeline.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nutrihfr import config as C  # noqa: E402
from nutrihfr.pipeline import NutriPipeline  # noqa: E402

if __name__ == "__main__":
    if C.MODE == "synthetic" and not (C.DATA_RAW / "synthetic" / "inca3").exists():
        import runpy
        runpy.run_path(str(Path(__file__).parent / "make_synthetic_data.py"), run_name="__main__")
    res = NutriPipeline().run()
    print(res["validation"].round(3).to_string(index=False))
