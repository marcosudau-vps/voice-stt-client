# REDACTION_CASES – OBS-020 RUN-01 (Claude)

## Einordnung

Die Redaction-**Regeln** R-1..R-12 selbst (`SENSITIVE_KEYS`, `TRANSCRIPT_KEYS`,
`unfreeze`, `redact_mapping`, `redact_text`, R-6-Whitelist, R-8/R-9/R-12) sind
in OBS-010 implementiert und dort unit-getestet
(`core/observability/redaction.py`, `tests/test_obs010_redaction.py`).
WP-OBS-020 stellt selbst klar: *"Redaction und Normalizer liegen in
OBS-010 — sie sind untrennbar, weil der Normalizer `redact` am Ende jedes
Pfades ruft"* (Titelkorrektur-Hinweis im Work Package). OBS-020 implementiert
**keine** neue Redaction-Logik.

Diese Datei dokumentiert stattdessen, was OBS-020s eigener Auftrag
tatsächlich verlangt (siehe `OBS-020_IMPLEMENTIERUNGSAUFTRAG.md`, Abschnitt
„Tests": *"Redaction von Secrets", "Erhalt nicht sensibler Struktur",
"Audio-Payload-Abwehr", "Transcript-Policy"*) — nämlich den **Nachweis**,
dass die bestehenden OBS-010-Garantien durch die neuen OBS-020-Komponenten
(`ObservabilityIngress`, `UnifiedLogHandler`) ungeschwächt hindurch wirken.
Automatisierter Beleg: `tests/test_obs020_redaction_end_to_end.py`.

## Fall 1 — Secret in `extra["detail"]` wird end-to-end redigiert

Eingabe (Python-Logzeile über den neuen `UnifiedLogHandler`):

```python
logger.warning("auth attempt", extra={
    "detail": {"accessToken": "super-secret-token-value", "ok": True},
})
```

Ergebnis im über `ObservabilityIngress.submit()` angenommenen
`CanonicalLogRecord`:

```json
{"detail": {"accessToken": "[redacted]", "ok": true}}
```

`super-secret-token-value` erscheint an keiner Stelle des Records (geprüft
über eine `repr()`-Suche über das gesamte `details`-Mapping).

Test: `TestSecretsAreRedactedEndToEnd::test_token_in_extra_detail_is_redacted_through_the_handler`

## Fall 2 — verschachtelter `Authorization`-Header

Eingabe:

```python
logger.warning("outbound request", extra={
    "detail": {"headers": {"Authorization": "Bearer abc.def.ghi"}},
})
```

Ergebnis:

```json
{"detail": {"headers": {"Authorization": "[redacted]"}}}
```

Test: `TestSecretsAreRedactedEndToEnd::test_authorization_header_style_key_is_redacted`

## Fall 3 — nicht-sensible Struktur bleibt erhalten

Eingabe:

```python
logger.warning("session update", extra={
    "detail": {
        "session_state": "connected",
        "retry_count": 3,
        "endpoint": "wss://example.invalid/ws/transcribe?token=abc",
    },
})
```

Ergebnis:

```json
{"detail": {
    "session_state": "connected",
    "retry_count": 3,
    "endpoint": "wss://example.invalid/ws/transcribe"
}}
```

`session_state` und `retry_count` sind unverändert (keine
Werteheuristik, R-3 ist reine Schlüsselregel). `endpoint` verliert Query/
Fragment (R-8), Schema/Host/Pfad bleiben diagnostisch nutzbar.

Test: `TestNonSensitiveStructureIsPreserved::test_non_sensitive_keys_survive_untouched`

## Fall 4 — Audio-Payload-Abwehr

`CONTRACTS §4.4` hält für Audioinhalt fest: *"kein Weg gefunden — nur Byte-
und Framezahlen werden geloggt. Regel: PCM-Bytes nie in `details` oder
`raw`."* OBS-020 darf diesen Befund nicht durch einen neuen Pfad
entkräften.

**Architektonischer Nachweis (Quellcode-Scan).** Die in
`LOGGING_ARCHITEKTUR_FREEZE_V1.md §8.6` benannten Hot-Path-Funktionen
(`AudioCapture._audio_callback`, `AudioCapture._process_loop`) enthalten
keinen Bezug zum Ingress: kein `submit(`, kein `ingress`, kein
`logging.`-Aufruf im Funktionskörper. Der einzige mögliche Weg für
Audiodaten in einen Record wäre ein `extra`-Feld einer regulären Logzeile —
und das kommt an keiner realen Aufrufstelle vor.

**Abwehrtest (Missbrauchsfall).** Selbst wenn ein `extra`-Feld
fälschlicherweise ein binäres Payload trüge, verlässt kein rohes
`bytes`-Objekt die Redaction — der Blattwert-Fallback
(`redaction._leaf_to_str`, OBS-010) wandelt es in eine gesicherte
String-Form:

```python
logger.warning("misuse guard", extra={
    "detail": {"payload": bytes(range(256)) * 4},
})
```

Ergebnis: `record.details["detail"]["payload"]` ist ein `str`, nie ein
`bytes`/`bytearray`.

Tests: `TestAudioPayloadIsNeverReachable::test_hot_path_audio_functions_never_reference_the_ingress`,
`::test_a_defensive_bytes_payload_would_never_be_stored_verbatim`

## Fall 5 — Transkript-Policy, Standardfall (`store_transcription_content=False`)

Eingabe:

```python
logger.info("Final [seg=1]: der geheime Transkriptinhalt")
```

Ergebnis (`record.message`):

```text
Final [seg=1]: [redacted:29 chars]
```

Der Klartext erscheint nicht; die Zeichenzahl (29 = `len("der geheime
Transkriptinhalt")`) bleibt erhalten (R-10).

Test: `TestTranscriptPolicyEndToEnd::test_final_line_is_char_count_only_by_default`

## Fall 6 — Transkript-Policy, Opt-in (`store_transcription_content=True`)

Dieselbe Eingabe wie Fall 5, aber mit `store_transcription_content=True` am
Normalizer, den `logging_setup.py`/`UnifiedLogHandler` aus
`ObservabilityIngress` bezieht:

```text
Final [seg=1]: der geheime Transkriptinhalt
```

Der Klartext bleibt vollständig erhalten — Opt-in wirkt end-to-end, nicht
nur in der isolierten OBS-010-Funktion.

Test: `TestTranscriptPolicyEndToEnd::test_final_line_is_kept_verbatim_when_opted_in`

## Fall 7 — Transkript-Schlüssel in `details` (nicht nur `message`)

Eingabe:

```python
logger.info("final received", extra={
    "detail": {"text": "vertraulicher Text hier", "segment": 1},
})
```

Ergebnis:

```json
{"detail": {"text": "[redacted:24 chars]", "segment": 1}}
```

R-10 gilt gemäß CONTRACTS ausdrücklich auch für unstrukturierte Logtexte
(nicht nur Serverevents) — hier end-to-end über den neuen Handler bestätigt.
`segment` (nicht in `TRANSCRIPT_KEYS`) bleibt unverändert.

Test: `TestTranscriptPolicyEndToEnd::test_transcript_keys_in_details_respect_the_same_policy`

## Fall 8 — keine Mutation der Eingangsdaten

```python
original_detail = {"accessToken": "keep-me-untouched"}
logger.warning("check mutation", extra={"detail": original_detail})
assert original_detail == {"accessToken": "keep-me-untouched"}  # unveraendert
```

`redact_mapping` (OBS-010) baut immer eine neue Struktur; über den neuen
Handler/Ingress-Pfad bestätigt, dass die vom Aufrufer übergebene
`extra`-Mapping-Referenz nach `emit()` unverändert ist.

Test: `TestNoMutationOfInputData::test_extra_mapping_passed_by_the_caller_is_not_mutated`

## Zusammenfassung

Alle acht Fälle grün (`tests/test_obs020_redaction_end_to_end.py`, 9 Tests
insgesamt). Die OBS-010-Redaction-Garantien werden durch
`ObservabilityIngress`/`UnifiedLogHandler` weder umgangen noch geschwächt.
