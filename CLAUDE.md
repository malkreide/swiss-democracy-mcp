# CLAUDE.md

## Vor der Arbeit

Klon-Aktualität prüfen — Standard-Branch ermitteln, nicht `main` annehmen:

```bash
B=$(git ls-remote --symref origin HEAD | sed -n 's|^ref: refs/heads/\([^[:space:]]*\).*|\1|p')
git fetch origin "${B:?Standard-Branch nicht ermittelbar}" &&
  git rev-list --count HEAD..FETCH_HEAD
```

Drei Server im Portfolio heissen ihren Standard-Branch `master`
(`openlex-mcp`, `swiss-courts-mcp`, `swisstopo-mcp`); dort scheitert ein fest
verdrahtetes `origin/main` mit «couldn't find remote ref main». Wer das für ein
Netzproblem hält, arbeitet weiter auf genau dem veralteten Klon, vor dem dieser
Absatz warnt. Den `:?`-Schutz nicht weglassen: Bei leerem `B` fetcht git still
den Remote-HEAD und endet mit 0.

Ein veralteter Klon erzeugt eine rote CI, deren Ursache nicht im Diff steht.
Am 3.8.2026 zweimal passiert — beide Male fehlten genau die Commits, die
das Gate einführten, an dem der Branch scheiterte.

Gates lokal fahren, mit der GEPINNTEN ruff-Version aus der CI. Eine andere
Version meldet Abweichungen, die niemand verursacht hat.

## Tests

Gegenprobe ist Pflicht. Ein Test, der grün bleibt, wenn man die
Implementierung entfernt, prüft nichts. Jede neue Zusicherung einzeln
neutralisieren und zeigen, dass genau die zugehörigen Tests fallen.

Zwei Fallen, die beide grün blieben:

- Eine Fake-Uhr, die nur beim Schlafen vorrückt, kann eine Zusicherung über
  echte Zeit nicht widerlegen.
- `monkeypatch.setattr(modul.asyncio, "sleep", ...)` greift ins Modul
  `asyncio` selbst und entschärft die Mechanik im ganzen Prozess. Patche
  einen Modul-Alias (`_sleep = asyncio.sleep`), nicht das fremde Modul.

Handgeschriebene Fixtures kodieren die Annahme des Autors und können sie
nicht widerlegen. Mindestens eine aufgezeichnete Antwort pro externem
Endpunkt, mit Aufnahmedatum.

## Wenn etwas rot ist

Roter Live-Test: erst die Quelle abfragen, dann einordnen. Nicht aus der
Fehlermeldung schliessen. Am 3.8.2026 hiess "nicht gefunden" nicht, dass der
Datensatz weg war, sondern dass die Quelle die Schreibweise ihrer Kopfzeile
gewechselt hatte — vier von sechs Datensätzen produktiv kaputt, alle
Unit-Tests grün.

Die Regel gilt in beide Richtungen. Am 24.8.2026 war die Quelle tadellos —
714 Zeilen, Abstimmung 551 da, 28 AHV-Treffer, alles nachgefragt — und rot
war der eigene Prozess: pytest-asyncio gibt jedem Test einen eigenen
Event-Loop, der prozessglobale `httpx.AsyncClient` überlebt den Test, und der
zweite Live-Test erbte den Pool des ersten samt dessen geschlossenem Loop.
`RuntimeError: Event loop is closed`, gemeldet als `finding`, etikettiert als
`upstream`. Wer nur die Quelle prüft, findet dort nichts und hat trotzdem
nichts erklärt.

Der Wächter hat es nicht gesehen, weil er nicht danach sucht:
`_client()` prüft `is_closed`, und das ist genau dann False, wenn niemand
`aclose()` gerufen hat — also auch bei einem Client, dessen Loop tot ist. Eine
Prüfung, die den einen Zustand nicht kennt, wegen dem sie da ist. Seither steht
der Loop daneben, und zwei `-m "not live"`-Tests halten beides fest: dass ein
neuer Loop einen neuen Client bekommt, und dass derselbe Loop denselben behält
(sonst wäre der geteilte Pool aus SDK-001 stillschweigend weg).

Warum das nur der Live-Lauf sah: Produktiv hat der Server einen Loop, der so
lange lebt wie er selbst. Die Live-Suite ist der einzige Ort im Repo, an dem
zwei echte Netzaufrufe auf zwei Loops treffen — die autouse-Fixture
`reset_cache` leert den 24h-CSV-Cache vor jedem Test, also geht wirklich jeder
Live-Test ans Netz. Ein Fehler, den ausschliesslich der wöchentliche Lauf
zeigt, wird auch ausschliesslich dort bemerkt: zwischen dem ersten roten Lauf
(17.8.) und der Diagnose lag eine Woche und ein zweiter roter Lauf.

PR ohne jeden Check ist selten ein Repo ohne CI, meistens ein
Merge-Konflikt: GitHub berechnet dafür keinen Merge-Commit und startet nichts.

Ein Codex-Review auf einem PR wird beantwortet oder behoben, nie ignoriert.

## Wenn Codex gar nicht erst hinsieht

Die Zeile oben unterstellt, dass es einen Befund geben *kann*. Das ist nicht
immer so, und man sieht es dem PR nicht an.

Am 21.8.2026 war das Code-Review-Kontingent zwischen 08:41 und 09:48
aufgebraucht — davor echte Reviews, danach in 30 Repos nur noch:

```
You have reached your Codex usage limits for code reviews.
```

Wie lange die Sperre dauerte, geben die Beobachtungen nur als Spanne her. Vier
Zeitpunkte sind belegt: letzter gelungener Review am 21.8. um 08:41, erste
Limit-Meldung um 09:48, letzte beobachtete Limit-Meldung am 22.8. um 11:03,
erste *andere* Meldung am 23.8. um 08:22.

Zwischen erster und letzter Limit-Meldung liegen **25 h 15 min**. Das ist der
Abstand zweier Fehlschläge, nicht die Dauer einer Sperre. Wer ihn Untergrenze
nennt, hat die durchgehende Erschöpfung schon vorausgesetzt, die er belegen
soll: Öffnete sich das Fenster zwischendurch und schloss es sich durch neue
Auslöser wieder, waren es zwei kurze Sperren und nie eine von 25 Stunden.
Untergrenze einer *einzelnen* Sperre sind die 25 h 15 min nur unter genau dieser
Annahme — und die ist unbelegt.

Nach oben trägt die Rechnung dagegen. Die längste mit den Beobachtungen
verträgliche Sperre reicht vom letzten Erfolg um 08:41 bis zur abweichenden
Meldung um 08:22, also **47 h 41 min**; länger kann keine einzelne gewesen sein.
Wer stattdessen ab der ersten Limit-Meldung rechnet, unterschlägt die 67
Minuten, in denen das Kontingent schon weg gewesen sein kann, und nennt die
Spanne zwischen zwei Beobachtungen eine Obergrenze.

Beobachtungspunkte sind keine Messreihe — die 21 Stunden vor der abweichenden
Meldung liefen ganz ohne Codex-Auslöser, dort hat niemand gemessen.

In der Zwischenzeit sind 32 PRs mit formal erfülltem Häkchen gemergt worden,
ohne dass jemand hineingesehen hat, und am 22.8. noch einmal 43.

**Fünf** Gründe, warum Codex schweigt, und nur einer davon ist harmlos:

- **Kein Befund** — dann schreibt er einen gewöhnlichen Issue-Kommentar:

  ```
  Codex Review: Didn't find any major issues. Swish!
  ```

  Der Schlusssatz wechselt bei jedem Lauf («Delightful!», «Keep it up!»,
  «More of your lovely PRs please.», «Keep them coming!»); stabil ist nur der
  Satz davor. Der
  Infokasten, den Codex unter jeden Review setzt, behauptet weiterhin eine
  Reaktion («otherwise it will react with 👍») — am 23.8. kam in sechs Repos
  die Meldung und in keinem die Reaktion. Der Kasten ist keine Quelle.
- **Der PR ist ein Draft** — darauf läuft Codex nicht an.
- **Das Kontingent ist weg** — dann schreibt er die Meldung oben.
- **Für das Repo fehlt eine Environment** — dann schreibt er:

  ```
  To use Codex here, create an environment for this repo.
  ```
- **Der automatische Weg scheitert, wo der manuelle trägt** — dann steht die
  Environment-Meldung da, obwohl `@codex review` Sekunden später einen
  vollständigen Review liefert. Belegt am 28.8. weiter unten. Die Meldung ist
  dann keine Aussage über das Repo, sondern über diesen einen Weg.

Der vierte kam erst zum Vorschein, als der dritte wegfiel, und das ist kein
Zufall: Die Prüfungen liegen hintereinander. Dass es diese Reihenfolge ist und
nicht die umgekehrte, lässt sich an einem einzigen Repo ablesen — in
`swiss-public-data-mcp` bekam PR #54 am 22.8. um 10:56:55 die Kontingent-Meldung
und PR #56 am 23.8. um 08:22:20 die Environment-Meldung. Läge die
Environment-Prüfung vorn, hätte #54 sie schon am Vortag gesehen; die Environment
fehlte ja bereits. Zwei Meldungen aus demselben Repo schlagen hier jede
Vermutung über die Reihenfolge.

Praktisch heisst das: **Eine verschwundene Limit-Meldung ist keine Entwarnung.**
Sie kann bedeuten, dass das Kontingent wieder da ist — und dass jetzt etwas
anderes den Review verhindert. Belegt ist eine Prüfung erst durch ein
Review-Objekt **oder** eine Befundlos-Meldung. Wer nur das Objekt gelten lässt,
zählt jeden befundlosen Review als ungeprüft — und baut sich denselben Fehlalarm
ein, den dieser Abschnitt verhindern soll, nur in die andere Richtung.

«Kein Kommentar» heisst also nicht «geprüft und sauber». Unterscheiden lässt es
sich an der Form: Ein Review **mit** Befund ist ein Review-Objekt
(«💡 Codex Review», mit Commit-Angabe); ein Review **ohne** Befund und die
beiden Ausfallmeldungen — Kontingent wie Environment — sind gewöhnliche
Issue-Kommentare und trennen sich nur im Text. Beim Draft gibt es überhaupt
nichts, weil Codex nicht anläuft; ein kommentarloser Draft ist deshalb kein
Beleg, sondern ein nicht durchgeführter Test.

Das sind verschiedene Abfragen — `get_reviews` fürs Objekt, `get_comments` für
alles andere; wer nur eine nimmt, übersieht den Rest. Genau so ist die
Limit-Meldung zuerst durchgerutscht.

Der Kommentarzähler allein reicht ohnehin nicht: `comments: 1` kann die
Befundlos-, die Kontingent- **oder** die Environment-Meldung sein — drei
gegensätzliche Bedeutungen unter derselben Zahl. Den Text lesen, nicht die Zahl.
Und einen unbekannten vierten Text wörtlich zitieren, statt ihn in eine der
bekannten Schubladen zu zwingen: Dieser Abschnitt musste erst von drei auf vier
und dann auf fünf Gründe wachsen, und die 👍-Reaktion stand hier zwei Fassungen
lang als Tatsache.

Und ein befundloser Lauf ist kein Freispruch. Am 23.8. lief derselbe Text durch
42 Reviews: 36 meldeten denselben P2-Befund, 6 die Befundlos-Meldung — gleiche
Eingabe, gegenteiliges Urteil, alles in denselben neun Minuten. Ein sauberer
Lauf sagt damit etwas über den Lauf, nicht über den Text. Wer sein Häkchen
daran hängt, hängt es an einen Münzwurf.

Portfolio-weit nachsehen:

```
search_pull_requests: user:malkreide commenter:chatgpt-codex-connector[bot] updated:>=<Datum>
```

Findet nur, wo er *kommentiert* hat. Repos ohne PR-Aktivität tauchen nicht auf
— das ist kein Beleg, dass dort geprüft wurde.

Zweiter Weg, den Prüfer zu verlieren, ganz ohne Kontingentproblem: zu schnell
mergen. Am 21./22.8. lagen zwischen «ready for review» und Merge mehrfach drei
bis fünf Sekunden. Codex wird beim Umschalten von Draft auf ready ausgelöst und
braucht danach Zeit; wer sofort mergt, hat das Häkchen gesetzt und den Review
nicht abgewartet.

Dritter Weg, und der unangenehmste, weil er wie gar kein Problem aussieht: Der
automatische Auslöser liefert nichts, während der manuelle liefert. Belegt am
28.8.2026 an **einem PR, in derselben Minute** — deshalb ohne die Ausreden, die
jeden Vergleich über Stunden hinweg entwerten:

| PR #53 | Auslöser | Antwort |
|---|---|---|
| 18:43:37 ready | Draft → ready | 18:43:41 «To use Codex here, create an environment» |
| 18:43:51 `@codex review` | von Hand | 18:46:52 vollständiger Review, drei P2-Befunde |

Zehn Sekunden zwischen den beiden Auslösern. Kein Kontingent, keine Queue und
keine Repo-Konfiguration ändert sich in zehn Sekunden so, dass daraus der
Unterschied folgt. Was folgt: **Die Environment-Meldung des automatischen Wegs
sagt nichts darüber, ob der manuelle Weg prüft.** Ob er sie gar nicht braucht
oder ob die Prüfung nur unzuverlässig ist, bleibt offen — ein Fall trägt keine
Mechanik.

Diese Fassung ist die zweite. Die erste stützte sich auf PR #51 (ready
04:35:22, gemergt 04:44:00, nichts in 8 min 38 s; manuell um 18:33:48 →
Befundlos-Meldung um 18:36:45) und schloss daraus Zeit und Environment als
Ursachen aus. Beides hielt nicht, und beides hat Codex im Review dieses
Abschnitts selbst zerlegt:

- **Die Zeit ist nicht ausgeschlossen.** Ein manueller Lauf mit 2 min 57 s
  begrenzt nicht, wie lange der automatische Weg vierzehn Stunden früher
  gebraucht hätte — Queue-Last und Ausführungspfad können abweichen. Schlimmer:
  Der Merge um 04:44:00 beendet den PR, und ein noch laufender Job stirbt
  damit. «Nichts kam an» und «nichts wurde ausgelöst» sind dann nicht mehr
  unterscheidbar.
- **Die Environment ist nicht ausgeschlossen.** Der Ausschluss stand auf dem
  Satz, sie hänge am Repo und schwanke nicht über den Tag. Sieben Minuten nach
  dem Lauf, auf den er sich stützte, kam im selben Repo die Environment-Meldung
  — und eine Environment kann in vierzehn Stunden ohnehin angelegt worden sein.

Von #51 bleibt deshalb nur die nackte Beobachtung: Zwischen ready und Merge kam
keine der drei Meldungen und kein Review-Objekt. Warum, ist offen.

Ein dritter Fall taugt weniger, als er aussieht. #45 und #46 tragen denselben
Sekundenstempel bei der Eröffnung (08:53:57); #45 bekam um 08:55:43 ein
Review-Objekt — **automatisch**, denn vor diesem Zeitpunkt steht kein einziger
Kommentar auf dem PR —, #46 bis zu seinem Merge fünf Stunden später gar nichts.
Daraus «der Auslöser fällt pro PR aus» zu folgern, geht trotzdem nicht: Für #46
ist nicht belegt, dass er zum fraglichen Zeitpunkt überhaupt ready war. War er
Draft, ist es Grund 2 und kein Ausfall. Was der Fall belegt, ist nur die
Gegenrichtung — dass der automatische Weg **auch schon funktioniert hat**.

Der Vorgänger-PR #50 (ready 04:26:01, gemergt 04:26:04) erklärt sich dagegen
vollständig durch die drei Sekunden — er gehört nicht in diese Schublade. Wer
beide Fälle zusammenwirft, hat wieder eine Ursache aus einer Fehlermeldung
geschlossen.

Warum der automatische Weg auf #53 die Environment vermisste und der manuelle
zehn Sekunden später nicht, ist damit offen. Eine unbelegte Vermutung zu #51 —
er war nur **12 Sekunden** Draft, bevor er auf ready ging, vielleicht
registriert ein so kurzer Übergang nichts — erklärt #53 gerade nicht, denn dort
hat der Auslöser ja gefeuert und geantwortet, nur mit der falschen Antwort.

Praktisch zählt zweierlei:

**`@codex review` von Hand hat geliefert, wo der automatische Weg schwieg oder
scheiterte.** Dreimal belegt und erstaunlich gleichmässig: #45 in 2 min 31 s,
#51 in 2 min 57 s, #53 in 3 min 1 s. Auf #53 sogar zehn Sekunden nach der
Environment-Meldung desselben Repos.

Wer den Aufruf absetzt, wartet diese drei Minuten ab. Codex quittiert ihn
vorher mit einer 👀-Reaktion **auf dem auslösenden Kommentar** — das ist die
Empfangsbestätigung, nicht das Ergebnis. Auf #53 lagen zwischen 👀 und Review
gut drei Minuten; wer nach einer Minute nachsieht und nichts findet, hält einen
laufenden Review für einen ausgefallenen.

Die 👀 ist nebenbei die einzige Reaktion, die je beobachtet wurde. Der
Infokasten verspricht eine 👍 auf den PR; die kam in sechs Repos am 23.8. nicht
und auf #51 am 28.8. auch nicht (`reactions.total_count: 0`). Die 👀 sitzt an
anderer Stelle und bedeutet etwas anderes: gesehen, nicht geprüft.

**Er wirkt auch auf einem bereits gemergten PR.** #45 war beim manuellen
Aufruf seit 70 Minuten gemergt, #51 seit knapp 14 Stunden — beide bekamen ihren
Review. Ein zu früh gemergter PR ist also nicht verloren; der Review lässt sich
nachholen, solange jemand merkt, dass er fehlt.

Und der Umkehrschluss, der hier am teuersten ist: **Bleibt es nach dem
automatischen Auslöser still, sagt das nichts über die Ursache** — nicht
Kontingent, nicht Environment, nicht «der Auslöser ist ausgefallen», und schon
gar nicht «der Text ist sauber». Belegt ist allein, dass am PR kein Review
angekommen ist. Ob keiner lief, ob einer noch lief und der Merge ihn beendet
hat, ob einer scheiterte — das trennt von aussen nichts. Die Abhilfe ist
dieselbe: `@codex review` absetzen und drei Minuten warten.

Das Kontingent hängt am Konto, nicht am Repo, und Code-Reviews haben einen
eigenen Topf — nur GitHub-getriggerte Reviews zählen hinein. ChatGPT-Pläne
fahren ein rollendes Fünf-Stunden-Fenster plus Wochenlimits; welches greift,
steht im Codex-Dashboard. Welches hier griff, ist **offen**. Die Lücke oben
schliesst das Fünf-Stunden-Fenster nicht aus: Es kann sich zwischendurch
geöffnet und durch neue Auslöser wieder erschöpft haben. Das auszuschliessen
bräuchte den Nachweis, dass in der ganzen Spanne kein einziger Review durchlief
— den gibt es nicht, weil nur Fehlschläge beobachtet wurden. Eine lange Reihe
von Fehlschlägen belegt eine lange Reihe von Fehlschlägen, nicht ihre Ursache.

Zeigt das Dashboard freies Kontingent, während Reviews weiter scheitern, ist
das ein bekannter Fehler bei mehreren verbundenen Konten — dann den
GitHub-Connector in den Codex-Einstellungen trennen und neu verbinden.

Die Environment legt man unter `chatgpt.com/codex/cloud/settings/environments`
an, und zwar **je Repo**. Die Meldung sagt es selbst («for this repo»), und am
23.8. war es genau so: In `swiss-public-data-mcp` fehlte sie, dort kam kein
Review; in den übrigen Repos lief Codex am selben Morgen durch. Eine
Environment fürs Konto genügt also nicht — wer eine anlegt und den Rest für
erledigt hält, mergt weiter Ungeprüftes.

## Wenn zwei Agenten dasselbe tun

Vor dem Anlegen eines Branches mit vorgegebenem Namen prüfen, ob es ihn schon
gibt:

```bash
git ls-remote --heads origin claude/<name> | wc -l
```

Steht dort `1`, arbeitet jemand anderes daran — mit Schreibrecht auf denselben
Ref.

Ein PR mit leerem Diff wird geschlossen, nicht gemergt. Der Test ist
`get_files` auf dem PR: kommt `[]` zurück, ändert er nichts. Ein grüner Check
sagt dazu nichts — die CI prüft den Head, nicht die Differenz zur Basis.

Am 21.8.2026 liefen zwei Sessions dieselbe Aufgabe über 45 Repos, auf den
Branches `claude/codex-review-audit-templates-9sn6mx` und
`claude/codex-review-audit-7ioh56`. Wo die eine zuerst nach `main` kam, wurde
`main` in den Branch der anderen gemergt und der add/add-Konflikt zugunsten
von `main` aufgelöst. Übrig blieben 14 PRs, die durch sämtliche Gates grün
liefen und nichts enthielten; sie wurden gemergt und hinterliessen leere
Merge-Commits. Mit den zwei Folge-PRs, die aus demselben Grund gegenstandslos
waren, waren 16 der 59 PRs jenes Tages reine Reibung.

Dieselbe Klasse wie der handgeschriebene Stub, der denselben Feldnamen annahm
wie der Code: Nichts ist rot, weil nichts geprüft wird, worauf es ankommt.

## Dieses Repo

**ruff-Pin: eine Quelle.** `pyproject.toml`, `dev`-Extra, `ruff==0.16.3`.
Die CI hat keinen eigenen Pin-Schritt — `pip install ".[dev]"` genügt, lokal
wie dort. Eine `.pre-commit-config.yaml` gibt es nicht; wenn eine dazukommt,
muss sie dieselbe Version aus `pyproject.toml` beziehen und keine zweite
nennen. Beim Anheben `ruff format` einmal über `src/ tests/ scripts/` laufen
lassen und das Ergebnis mitcommitten.

Vor dem Lauf `ruff --version` prüfen: ein älteres ruff früher im `PATH`
schlägt den Pin, ohne dass der Install etwas meldet.

Gates, wörtlich aus `ci.yml` (Python 3.11/3.12/3.13):

```
python scripts/check_ruff_pin.py
python -m ruff check src/ tests/ scripts/
python -m ruff format --check src/ tests/ scripts/
PYTHONPATH=src python -m pytest tests/ -m "not live" -v
python scripts/check_version_sync.py
```

Alle vier laufen in einem Job auf allen drei Feldern — keine
`if:`-Ausnahme, kein zweiter lint-Job. Ein grünes 3.13 heisst hier wirklich,
dass alles auf 3.13 lief; im Portfolio ist das nicht durchgehend so. Ein
`fail-fast: false` steht nicht da.

Beide Auslöser sind auf `branches: [main]` eingeschränkt. Ein PR gegen einen
anderen Basis-Branch startet deshalb gar nichts — dieselbe leere Check-Liste
wie beim Merge-Konflikt oben, aber eine andere Ursache.

Dazu ein Gitleaks-Secret-Scan über die volle Historie (`fetch-depth: 0`) —
als eigener Job `secret-scan`, den keiner der Befehle oben nachstellt.

**Live-Tests: DRIFT-005 erfüllt, aber die Abdeckung ist ungleich.**
`.github/workflows/live-tests.yml` läuft geplant (`cron: "13 5 * * 1"`, dazu
`workflow_dispatch`) und öffnet/schliesst bei Bedarf ein `upstream`-Issue.
Die PR-CI schliesst die Live-Tests per `-m "not live"` aus — das ist hier
kein Verstoss, weil der geplante Lauf existiert. `schedule` greift nur auf
dem Default-Branch: Änderungen an dieser Datei wirken erst nach dem Merge,
vorher von Hand per `workflow_dispatch` auslösen.

**Der Lauf erreicht `swissvotes.ch`, sonst nichts.** Zwei der zehn Werkzeuge
sind live abgedeckt; `opendata.swiss`/BFS gar nicht, Polis nicht, weil es
`SRGSSR_CONSUMER_KEY`/`-SECRET` verlangt und der Workflow keine hereinreicht.
Der Workflow nannte trotzdem `api.srgssr.ch` als sein Ziel — die eine Quelle,
die er nicht abfragt — und legte seine Issues unter diesem Namen an. Bei
rotem Lauf zuerst die Quelle abzufragen heisst dann: die falsche abfragen.
`tests/test_live_abdeckung.py` hält beides fest, und es leitet die Abdeckung
aus den `-m live`-Tests ab statt sie aufzuschreiben — ein neues Werkzeug muss
dort eingeordnet werden, sonst fällt der Test.
