"""Read-before-start operator plan and evidence state; no product side effects."""
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit
import os
import uuid

ROOT = Path(__file__).resolve().parents[3]
RUNTIME = ROOT/'build/ap-iv2-020-suite'
PROFILE_RUNTIME = Path(os.environ.get('USERPROFILE', 'C:/Users/marco'))/'.voice-stt/qualification/AP-IV2-020'
TARGET = 'wss://pro.v2.voice-stt-server.marcosudau.com/ws/v2'
PREPARE_SECONDS = 10


def owned_path(path, root=None):
    path = Path(path).resolve()
    roots = [Path(root).resolve()] if root is not None else [RUNTIME.resolve(), PROFILE_RUNTIME.resolve()]
    if not any(path.is_relative_to(candidate) for candidate in roots):
        raise ValueError('Test runtime must stay inside its dedicated project or explicitly approved qualification directory')
    return path


def target_origin(url):
    parts = urlsplit(url)
    if (parts.scheme != 'wss' or parts.hostname not in (
            'pro.v2.voice-stt-server.marcosudau.com', 'v2.voice-stt-server.marcosudau.com')
            or parts.port not in (None, 443) or parts.path != '/ws/v2'
            or parts.username or parts.password or parts.query or parts.fragment):
        raise ValueError('Only the two explicitly selected TLS V2 targets are allowed')
    return 'https://'+parts.netloc


def task(key, title, requirements, phrase, steps, expected, secondary='finish'):
    return dict(id=key, title=title, requirements=requirements, phrase=phrase,
                steps=steps, expected=expected, secondary=secondary)


TASKS = [
    task('finish', '1 · Diktat mit F8 / Finish mit F9', ['M-01', 'M-04', 'M-11', 'O01'],
         'Dies ist die manuelle Hotkeyprobe.', [
             'Strg+Umschalt+F8 drücken; auf Aufnahme reagieren.',
             'Den grünen Satz sprechen. Direkt danach Strg+Umschalt+F9 drücken und alle Tasten loslassen.',
             'Text und Abschluss abwarten. Ergebnis unten bewerten; dann Versuch beenden.'],
         'Ein vollständiger Nutzsatz wird genau einmal eingefügt. Kein dauerhaft ausstehendes Diktat.'),
    task('followup', '2 · Zwei Sätze mit Denkpause', ['M-01', 'M-10'],
         'Der blaue Becher steht auf dem Tisch.\nDie grüne Lampe steht neben dem Fenster.', [
             'Strg+Umschalt+F8 drücken und den ERSTEN Satz sprechen.',
             'Etwa vier Sekunden schweigen. Dann den ZWEITEN Satz sprechen; F9 drücken und Tasten loslassen.',
             'Beide Sätze mit Leerzeichen abwarten und bewerten.'],
         'Zwei Segmente derselben Activation, beide Sätze vollständig; effektives Follow-up 5000 ms.'),
    task('cancel', '3 · Aufnahme ausdrücklich abbrechen', ['M-04', 'O01'],
         'Diese Aufnahme soll ausdrücklich abgebrochen werden und keinen späteren Text erzeugen.', [
             'Strg+Umschalt+F8 drücken. Den grünen Satz langsam zu sprechen beginnen.',
             'MITTEN IM SATZ Strg+Umschalt+F9 drücken, alle Tasten loslassen. F9 bedeutet hier CANCEL.',
             'Mindestens zehn Sekunden schweigen. Tray und Overlay vergleichen, unerwarteten Text notieren.'],
         'Cancel autoritativ bestätigt; keine neue Ausgabe aus dem abgebrochenen offenen Segment.', 'cancel'),
    task('refresh', '4 · Nachsprechfenster verlängern', ['M-04'],
         'Dies ist der erste Abschnitt.\nDies ist der Abschnitt nach dem Verlängern.', [
             'F8 drücken und den ERSTEN Satz sprechen; dann schweigen.',
             'In der Nachsprechphase F8 erneut drücken. Etwa drei Sekunden warten und den ZWEITEN Satz sprechen.',
             'F9 drücken, Tasten loslassen und beide Sätze abwarten.'],
         'Refresh derselben Activation statt neuer Activation; kein kumulativer Timer.'),
    task('none', '5 · Bewusst wirkungslose Zweittaste', ['M-04'],
         'Hier nichts sprechen.', [
             'F8 drücken, zwei Sekunden schweigen, F9 drücken. F9 ist NUR IN DIESER AUFGABE auf NONE gestellt.',
             'Weitere drei Sekunden beobachten: F9 darf die Eingabe nicht schließen.',
             'Den natürlichen Timeout abwarten und bewerten.'],
         'F9 erzeugt kein mutierendes Command. Danach regulärer Initial-Speech-Timeout.', 'none'),
    task('feedback', '6 · LED, Sound und Overlay in Ruhe', ['M-10'],
         'Diesen Satz nur lesen – bei diesem Versuch nichts sprechen.', [
             'F8 drücken; Aktivierungsblitz, wartenden Ring und Overlay beobachten.',
             'Schweigen und den vollständigen Timeout abwarten; auf Stoppton und Idle achten.',
             'Nach dem Timeout zwei weiße Idle-Pulse beobachten: Minimum30%, Maximum100% der Effekthelligkeit. Wird der Ring noch violett? Beobachtung unten notieren.'],
         'Fachliche Phasen stimmen überein; konkrete menschliche Wahrnehmung getrennt von Messwerten.'),
    task('mute', '7 · ReSpeaker Hardware-Mute', ['M-05', 'M-06'],
         'Diese Sprache darf während Hardware-Mute keine Aufnahme erzeugen.', [
             'Hardware-Mute am ReSpeaker einschalten. F8 drücken, den grünen Satz sprechen.',
             'Mindestens fünf Sekunden beobachten. Dann Hardware-Mute wieder ausschalten.',
             'F8 drücken: „Das Mikrofon ist wieder frei.“ sprechen, F9 drücken. Wirkung und LEDs notieren.'],
         'Mute tatsächlich diagnostiziert, keine Sprache während Mute; Wiederfreigabe ohne Autoactivation.'),
    task('usb', '8 · USB trennen und wieder verbinden', ['M-06'],
         'Vor dem Trennen beginnt diese Aufnahme.\nNach dem Verbinden funktioniert das Mikrofon wieder.', [
             'F8 drücken, den ERSTEN Satz zu sprechen beginnen; ReSpeaker-USB während der Aufnahme trennen.',
             'Zehn Sekunden warten. ReSpeaker wieder anschließen. Warten, bis die Live-Diagnose Audio verfügbar meldet.',
             'Erst dann F8, ZWEITER Satz, F9. Kein automatischer Start allein durch Wiederanschließen.'],
         'Realer Audioverlust und Recovery; kein automatischer neuer Trigger; alter/neuer Lifecycle getrennt.'),
    task('reconnect', '9 · Nur diesen Client wiederverbinden', ['M-05', 'M-07'],
         'Nach der Wiederverbindung ist dies ein neues Diktat.', [
             'OHNE offene Aufnahme unten „Diesen Testclient wiederverbinden“ klicken. Kein Server wird beendet.',
             'Auf neue Session und CLIENT BEREIT in der Live-Diagnose warten.',
             'F8, grünen Satz sprechen, F9. Zustand und Ausgabe prüfen.'],
         'Neue Generation/Session, Bootstrap vor Audio/Trigger; anschließend regulärer Manual-Pfad.'),
    task('reinsert', '10 · Bewusstes Wiedereinfügen', ['M-11'],
         'Dieser Satz wird einmal bewusst erneut eingefügt.', [
             'F8, grünen Satz sprechen, F9 und die erste Einfügung abwarten.',
             'Strg+Umschalt+F11 EINMAL drücken und Tasten loslassen.',
             'Genau zwei Exemplare mit Leerzeichen erwarten; dies ist ein ausdrücklich angefordertes Reinsert.'],
         'Ein ASR-Final plus genau eine ausdrücklich angeforderte Wiedereinfügung; keine automatische Doppelung.'),
    task('settings', '11 · Einstellungen, Verlauf und echte Logs', ['M-08', 'T01', 'T02'],
         'In dieser Aufgabe nichts sprechen. Keine Zugangsschlüssel in die Notizen schreiben.', [
             'Unten „Einstellungen öffnen“ klicken. Serverziel im Kopf prüfen; den Dialog für lokale Einstellungen öffnen.',
             'Logging, Verlauf und Erscheinungsbild/Feedback suchen. Echte Logansicht öffnen; Verbindungs-/Systemeinträge prüfen.',
             'Overlay-Lesbarkeit und Dauer bei Bedarf beurteilen. KEINE Serverdefaults oder Modelle ändern. Dialoge schließen und Beobachtung unten eintragen.'],
         'Tatsächlich zugängliche Tabs/Logdaten und sichtbares Ziel bestätigen; keine bloße Konstruktorprüfung.'),
]

WAKE_TASKS = []
for key, word, silent in [('wake_alexa','Alexa',False), ('wake_jarvis','Hey Jarvis',False), ('wake_silent','Alexa',True)]:
    item = task(key, 'Wake-FIX · '+word+(' · Sound AUS' if silent else ' · Sound AN'), ['W01','M-02','M-10'],
        word, [
            'Bei CLIENT BEREIT und nach der Vorbereitung das grüne Rufwort genau EINMAL sprechen. Keine Taste drücken.',
            'Danach schweigen und den normalen Eingabeschluss abwarten. '+('Es darf kein Sound kommen.' if silent else 'Start-/Stoppton, LED und Overlay beobachten.'),
            'Nach dem Eingabeschluss weitere fünf Sekunden schweigen. Erst bei abgeschlossener Ruheprüfung „Versuch beenden“ und Ergebnis übernehmen.'],
        'Genau eine Wake-Activation; Timeout ohne automatischen zweiten Start. '+('Kontrollvergleich ohne Soundausgabe.' if silent else 'Sound/LED/Overlay wahrnehmen und bewerten.'))
    item.update(wake=True, sounds=not silent)
    WAKE_TASKS.append(item)

ALL_TASKS = TASKS + WAKE_TASKS

DEFERRED = [
    'W01: konkreter Folgetrigger nach Fix in13Modellfällen und3aktuellen Mikrofon-/Soundkontrollen nicht mehr aufgetreten. Offen bleiben vollständige Wake-/Both-Parität und30min100.',
    'M-04: weitere Phasenkombinationen, Hotkey-Kollision und realer Watchdog bleiben gesonderte technische Nachweise.',
    'M-05: idle-Pausen/Reconnect/Neustart nachgewiesen; aktivierte Wakeengine und weitere Kombinationen noch offen.',
    'M-06: USB-Recovery und LED-only bei idle nachgewiesen; offener Input/Altfinal-Kombinationen noch offen.',
    'M-07: Netzverlust mit offenem Preview/Final und separater Logstore-Ausfall bleiben eigene Faulttests; kein fremder Serverstopp.',
    'M-08: Cancel/Finish/Vormerken einer Sessionänderung bei Aufnahme und ausstehendem Final separat vorbereiten.',
    'M-09: nativer Credential-Lebenszyklus isoliert nachgewiesen; Admin-/Dialog-/Exportfälle noch offen.',
    'M-10/M-11: Frozen-Build, erhöhte Anwendung, Clipboard-Konflikt und Prozessabbruch nahe Paste brauchen eigene Vorbereitung.',
]


def select_tasks(ids=None):
    if ids is None:
        return list(TASKS)
    by_id = {task['id']: task for task in ALL_TASKS}
    if not ids or len(set(ids)) != len(ids) or any(value not in by_id for value in ids):
        raise ValueError('Select distinct known task IDs')
    return [by_id[value] for value in ids]


class SuiteRecord:
    def __init__(self):
        self.attempts = []
        self.active = None

    def start(self, task_id):
        if self.active is not None:
            raise RuntimeError('Finish and decide the previous attempt first')
        self.active = dict(attemptId=uuid.uuid4().hex, taskId=task_id,
                           startedAtUtc=datetime.now(UTC).isoformat(),
                           evaluation='NOT_PROVEN_PENDING_AGENT_REVIEW')
        self.attempts.append(self.active)
        return self.active

    def stopped(self, exit_code):
        if self.active is None:
            raise RuntimeError('No active attempt')
        self.active.update(exitCode=exit_code, endedAtUtc=datetime.now(UTC).isoformat())

    def decide(self, decision, observation, notes):
        if self.active is None or 'exitCode' not in self.active:
            raise RuntimeError('Client must have stopped before the next attempt')
        if decision not in ('accept', 'repeat', 'skip'):
            raise ValueError('Unknown operator decision')
        self.active.update(decision=decision, humanObservation=observation, humanNotes=notes,
                           tester='marco: human Windows/ReSpeaker actions; Codex: instrumentation/evaluation')
        self.active = None
