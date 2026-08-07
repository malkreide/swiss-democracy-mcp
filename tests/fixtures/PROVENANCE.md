# Herkunft der Fixtures

**Erzeugt von `scripts/record_fixtures.py`. Nicht von Hand pflegen.**

Aufgezeichnet am **2026-08-07**.

Ohne Datum ist «aufgezeichnet» nach zwei Jahren von «ausgedacht» nicht
mehr zu unterscheiden — die Datei sieht gleich aus.

## Die Auswahlregel ist hier der Punkt

Der Swissvotes-Datensatz hat am Aufzeichnungstag **714 Zeilen** und
874 Spalten. Ausgeschnitten wird **nach Merkmal, nicht nach Position**.
«Die ersten N Zeilen» wuerde genau die Zellen wegschneiden, wegen derer es
die Fixture gibt: die Fuellwerte `9999` («keine Angabe») und `.` («nicht
anwendbar»), die in 667 der 714 Abstimmungen vorkommen. Eine Fixture ohne
sie saehe sauber aus und belegte nichts.

Welche Zeile welches Merkmal belegt, steht unten bei der Datei. Trifft eine
Regel eines Tages nichts mehr, bricht das Skript ab, statt eine Fixture zu
schreiben, die weniger belegt, als sie aussieht.

**Das BOM bleibt drin.** Das Original stellt der ersten Spalte `anr` ein
Byte-Order-Mark voran, und der Server entfernt es ausdruecklich. Ohne BOM
koennte die Fixture nicht belegen, dass er das muss.

## NICHT aufgezeichnet

### `polis_*.json`

- **Quelle:** `https://api.srgssr.ch/polis/v1/votations`
- **Grund:** SRGSSR_CONSUMER_KEY/SRGSSR_CONSUMER_SECRET nicht gesetzt. Ohne OAuth2-Token antwortet der Endpunkt mit HTTP 200 und `<!DOCTYPE html>
<html  lang="en" dir="lt…` — also mit der Entwicklerportal-Seite, nicht mit Daten. NICHT aufgezeichnet.

Die Polis-Payloads stehen weiterhin als Literale im Testmodul. Sie sind
damit **ausgedacht** und tragen kein Datum — das ist der Ist-Zustand und
keine Nachlaessigkeit dieses Laufs. Wer Zugangsdaten hat, setzt sie und
ergaenzt den Zweig im Skript.

## `swissvotes_rows.csv`

- **Quelle:** `https://swissvotes.ch/storage/f3cca8daa882cb2bac8142647eadd7965765be127f720817f18eaaa12643019a`
- **Aufgezeichnet:** 2026-08-07
- **Auswahl:** Kopfzeile unveraendert (874 Spalten); 3 von 714 Zeilen, **nach Merkmal ausgewaehlt statt nach Position**. Abstimmung 1: traegt `9999` in einer Parteispalte — der Fuellwert «keine Angabe»; traegt `.` in einer Zahlenspalte (`zh-japroz`) — dort muss der Parser `None` liefern und nicht raten. Abstimmung 2: traegt `.` in `br-pos` — «nicht anwendbar» statt einer Position. Abstimmung 681: juengste Abstimmung mit vollstaendigen Parolen und Resultat — der Fall, in dem alles da ist
- **Groesse:** 18277 B
- **SHA-256:** `2eba6cd8e935640b19c213f188fe230c111bd80dff1ac52df42ca17b97da1b08`

## `bfs_package_national.json`

- **Quelle:** `https://ckan.opendata.swiss/api/3/action/package_show?id=echtzeitdaten-am-abstimmungstag-zu-eidgenoessischen-abstimmungsvorlagen`
- **Aufgezeichnet:** 2026-08-07
- **Auswahl:** `resources` auf die 5 juengsten von 135 gekuerzt, `num_resources` unveraendert (135); alles uebrige vollstaendig
- **Groesse:** 42758 B
- **SHA-256:** `260daa8a5973cbbf118b849e041604ce42d7170faf9714e5c3177fcb0f444726`

## `bfs_package_cantonal.json`

- **Quelle:** `https://ckan.opendata.swiss/api/3/action/package_show?id=echtzeitdaten-am-abstimmungstag-zu-kantonalen-abstimmungsvorlagen`
- **Aufgezeichnet:** 2026-08-07
- **Auswahl:** `resources` auf die 5 juengsten von 42 gekuerzt, `num_resources` unveraendert (42); alles uebrige vollstaendig
- **Groesse:** 32711 B
- **SHA-256:** `1ecc3bb86c30885232e97afcd2d961b50e63bf43df609b182c61b5f37794e33c`
