"""Read-only progress window. Closing it never stops the independent test."""
import argparse,json
from datetime import UTC,datetime
from pathlib import Path
from tests.manual.v2.suite_plan import ROOT


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--folder',type=Path,required=True);args=p.parse_args()
    folder=args.folder.resolve()
    if not folder.is_relative_to((ROOT/'build').resolve()):raise ValueError('Progress must be in project build')
    from PySide6.QtCore import QTimer,Qt
    from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QLabel,QProgressBar
    app=QApplication([]);w=QWidget();w.setAttribute(Qt.WA_ShowWithoutActivating)
    w.setWindowTitle('AP-IV2-020 – automatisierter 30-Minuten-Lauf')
    w.setMinimumWidth(540);layout=QVBoxLayout(w)
    title=QLabel('Automatisierter Dauertest · keine Bedienung nötig');title.setStyleSheet('font-size:18px;font-weight:bold;padding:10px')
    layout.addWidget(title);status=QLabel('Status wird geladen …');layout.addWidget(status)
    time_bar=QProgressBar();time_bar.setRange(0,1800);layout.addWidget(time_bar)
    count_bar=QProgressBar();count_bar.setRange(0,100);layout.addWidget(count_bar)
    details=QLabel();layout.addWidget(details)
    note=QLabel('Echte Sprachproben / Server-ASR · kontrollierter Mikrofon-/Paste-Rand\nFenster schließen beendet den Test nicht. USB-/EXE-Abnahme bleibt separat.');layout.addWidget(note)
    measurement_at=None
    def refresh():
        nonlocal measurement_at
        try:data=json.loads((folder/'progress.json').read_text(encoding='utf8'))
        except (OSError,ValueError):return
        if measurement_at is None:
            try:
                stamp=json.loads((folder/'result.json').read_text(encoding='utf8')).get('measurementStartedAtUtc')
                if stamp:measurement_at=datetime.fromisoformat(stamp)
            except (OSError,ValueError):pass
        elapsed=(max(0,(datetime.now(UTC)-measurement_at).total_seconds()) if measurement_at else 0) if data['state']=='RUNNING' else (data.get('seconds') or 0)
        completed=data.get('completed',0);remaining=max(0,1800-int(elapsed))
        state='BOOTSTRAP / MODELLE LADEN' if data['state']=='RUNNING' and measurement_at is None else data['state']
        status.setText(f"{state} · {int(elapsed)//60:02d}:{int(elapsed)%60:02d} Messzeit · {remaining//60:02d}:{remaining%60:02d} verbleibend")
        time_bar.setValue(min(1800,int(elapsed)));time_bar.setFormat('%v / 1800 Sekunden')
        count_bar.setValue(completed);count_bar.setFormat('%v / 100 abgeschlossen')
        latest=data.get('latest',{})
        details.setText(f"Aktivierungen: {data.get('activations','–')} · Finals: {data.get('finals','–')}\n"
            f"Tasks: {latest.get('tasks','–')} · ausstehende Commands: {latest.get('pendingCommands','–')} · privater Speicher: {latest.get('privateBytes',0)/1048576:.1f} MiB")
        title.setStyleSheet('font-size:18px;font-weight:bold;padding:10px;color:'+('#a02020' if data['state']=='FAIL' else '#126438'))
    timer=QTimer();timer.timeout.connect(refresh);timer.start(1000);refresh();w.show();app.exec()


if __name__=='__main__':main()
