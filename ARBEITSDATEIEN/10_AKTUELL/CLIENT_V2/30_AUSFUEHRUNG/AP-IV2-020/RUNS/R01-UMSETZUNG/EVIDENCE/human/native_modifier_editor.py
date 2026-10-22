"""Native-only task labels on the reusable tests/manual/v2 editor.

Only an editor presentation adapter; product/runtime/native input is untouched.
"""
import argparse
from pathlib import Path
import sys

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'voice_stt_client').is_dir())
sys.path.insert(0,str(ROOT))
from native_modifier_trial import STEPS
from tests.manual.v2.step_board import StepBoard

original=StepBoard.configure
def configure(self,case):
    original(self,case)
    if case=='native':
        self.steps=list(STEPS)
        self.set_stage(0)
StepBoard.configure=configure


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check',action='store_true')
    args=parser.parse_args()
    if args.self_check:
        from PySide6.QtWidgets import QApplication
        app=QApplication([]);board=StepBoard();board.configure('native')
        assert board.steps==STEPS and board.active==0
        board.set_stage(3)
        assert 'F9' in board.labels[3].text() and board.clocks[3].text()=='Dein Tempo'
        board.set_stage(7)
        assert not board.set_stage(4) and board.active==7
        print('PASS: actual Qt native-task labels, own tempo and monotonic progress; no runtime/input')
    else:
        from tests.manual.v2.human_test_editor import run
        raise SystemExit(run())
