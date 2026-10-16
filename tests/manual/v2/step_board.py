"""Persistent operator steps. Display timers never change product deadlines."""
import math
import time
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget


class StepBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setVerticalSpacing(3)
        self.labels, self.clocks = [], []
        for row in range(8):
            label, clock = QLabel(), QLabel()
            label.setWordWrap(True)
            clock.setMinimumWidth(80)
            layout.addWidget(label,row,0)
            layout.addWidget(clock,row,1)
            self.labels.append(label);self.clocks.append(clock)
        layout.setColumnStretch(0,1)
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start()
        self.configure('manual')

    def configure(self, case):
        self.steps = [
            'Satz und Ablauf in Ruhe lesen · dann Start drücken',
            'Verbindung und Mikrofon starten · bitte warten',
            'Bereitmachen · Countdown abwarten',
            'Strg+Umschalt+F8 drücken' if case=='manual' else 'Jetzt Rufwort und Nutzsatz ohne Pause sprechen',
            'Den grünen Satz sprechen' if case=='manual' else 'Den grünen Satz zu Ende sprechen',
            'Strg+Umschalt+F9 kurz drücken · alle Tasten loslassen',
            'Text und Abschluss abwarten · im Testfenster bleiben',
            'Ergebnis prüfen · Wiederholen oder Übernehmen wählen',
        ]
        self.active = -1
        self.set_stage(0)

    def set_stage(self, stage, seconds=None):
        if stage < self.active:
            return False  # Late segment events cannot undo Finish/Review.
        if not 0 <= stage < len(self.steps):
            raise ValueError('Unknown operator step')
        self.active = stage
        self.since = time.monotonic()
        self.deadline = self.since+seconds if seconds is not None else None
        for row,(label,clock,text) in enumerate(zip(self.labels,self.clocks,self.steps)):
            done, current = row < stage, row == stage
            label.setText(('✓  ' if done else '▶  ' if current else f'{row+1}.  ')+text)
            style = ('color: #172b57; background: #e5efff; border: 2px solid #2563eb; font-weight: bold;'
                     if current else 'color: #41664b; background: #f3f8f4;' if done else
                     'color: #818895; background: #f2f3f5;')
            for widget in (label,clock):
                widget.setStyleSheet('font-size: 15px; padding: 5px; border-radius: 4px;'+style)
            clock.setText('✓' if done else '')
        self.update_clock()
        return True

    def update_clock(self):
        if self.deadline is not None:
            value = f'{max(0,math.ceil(self.deadline-time.monotonic()))} s'
        elif self.active in (0,3,7):
            value = 'Dein Tempo'
        else:
            value = f'{int(time.monotonic()-self.since)} s'
        self.clocks[self.active].setText(value)
