"""Retired AP-IV2-020 starter after explicit human removal of its server.

Deliberately contains no Docker operations, profile I/O, process startup or IPC.
The existing shortcut may open this information window, but cannot restart the
removed qualification server or silently select a different server.
"""
import sys

RETIRED_MESSAGE = (
    "Dieser Teststarter ist deaktiviert.\n\n"
    "Der zusätzliche Qualifikationsserver wurde auf deinen Wunsch entfernt.\n"
    "Es wird kein Server und kein Testclient gestartet."
)


def start_client(status):
    raise RuntimeError(RETIRED_MESSAGE)


def main():
    from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
    app = QApplication.instance() or QApplication([])
    window = QWidget()
    window.setWindowTitle('V2-Testinstanz – deaktiviert')
    window.resize(600, 250)
    layout = QVBoxLayout(window)
    label = QLabel(RETIRED_MESSAGE)
    label.setWordWrap(True)
    label.setStyleSheet('font-size:18px;padding:14px;')
    layout.addWidget(label)
    start = QPushButton('Teststarter deaktiviert')
    start.setEnabled(False)
    layout.addWidget(start)
    close = QPushButton('Schließen')
    close.clicked.connect(window.close)
    layout.addWidget(close)
    window.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
