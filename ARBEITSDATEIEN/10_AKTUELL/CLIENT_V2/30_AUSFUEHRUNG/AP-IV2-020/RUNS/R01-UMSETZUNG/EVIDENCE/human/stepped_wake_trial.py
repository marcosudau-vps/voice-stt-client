"""Compatibility entry point; maintained implementation: tests/manual/v2/."""
from pathlib import Path
import sys
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'voice_stt_client').is_dir())
sys.path.insert(0, str(ROOT))
from tests.manual.v2.stepped_wake_trial import *
if __name__ == "__main__":
    raise SystemExit(main())
