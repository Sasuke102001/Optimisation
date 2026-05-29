import os
from pathlib import Path
import site
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
VENDOR = ROOT / ".vendor"


def _load_dotenv_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue
        value = value.strip()
        if len(value) >= 2 and ((value[0] == value[-1] == '"') or (value[0] == value[-1] == "'")):
            value = value[1:-1]
        os.environ[key] = value


_load_dotenv_file(ROOT / ".env")

if VENDOR.exists():
    site.addsitedir(str(VENDOR))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from research_extraction.pipeline import main


if __name__ == "__main__":
    raise SystemExit(main())
