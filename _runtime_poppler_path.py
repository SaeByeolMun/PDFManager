# src/_runtime_poppler_path.py
import os, sys, pathlib

def _add_poppler_to_path():
    base = pathlib.Path(getattr(sys, "_MEIPASS", pathlib.Path(sys.argv[0]).resolve().parent))
    poppler = base / "poppler_bin"
    if poppler.exists():
        try:
            # Windows 10+에서 DLL 로딩 경로 보장
            os.add_dll_directory(str(poppler))
        except Exception:
            pass
        os.environ["PATH"] = str(poppler) + os.pathsep + os.environ.get("PATH", "")

_add_poppler_to_path()
