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

## Zahlen, die eine Aufzählung wiederholen

Eine Zahl im Fliesstext, die eine Liste oder Tabelle daneben zählt, ist eine
Kopie. Sie wird beim nächsten Eintrag falsch — nicht irgendwann, sondern sofort.
Streichen statt nachführen: Die Aufzählung ist die Quelle, der Satz verweist auf
sie.

Am 29.8.2026 hat das in `docs/codex-reviews.md` eine Review-Runde nach der
anderen gekostet, und **jede Korrektur erzeugte die nächste:**

| Die Zahl | Warum sie fiel |
|---|---|
| «sechs» im Text gegen «sieben» in der Einleitung | zwei Zählstellen für dasselbe Archiv |
| Überschrift «Drei Fassungen» | beim Beheben war ein vierter Eintrag dazugekommen |
| «Acht Fassungen» | ein Listenpunkt war die überlebende Fassung, keine gescheiterte |
| «vier Fehlschläge» über einer Tabelle mit acht Zeilen | Tabelle gewachsen, Prosa nicht |
| «Zwei Fehlschläge der Tabelle» | Nenner entfernt, Zähler stehen gelassen |

Handgriffe daraus:

- **Der Zähler zählt auch.** «Zwei der vier» zu «Zwei» zu machen behebt nichts.
  Beide Zahlen hängen an derselben Aufzählung, und dieselbe Ergänzung macht
  beide falsch. Beim «Zwei Fehlschläge der Tabelle» war die Regel bereits
  bekannt und wurde trotzdem zur Hälfte angewandt.
- **Nicht die Länge messen, den Inhalt lesen.** `grep -c` über die Listenpunkte
  bestätigte «acht» — einer davon beschrieb aber die Fassung, die *stehen
  geblieben* war. Die mechanische Prüfung schützt gegen Drift und ist blind für
  Bedeutung.
- **Beim Ergänzen die Prosa daneben mitlesen**, nicht nur die Liste. Die
  Überschrift «Drei Fassungen», die «vier Fehlschläge» und der Zähler «Zwei»
  wurden alle dadurch falsch, dass ein Eintrag dazukam und ein Satz einen
  Absatz weiter unbemerkt veraltete.

## Wenn etwas rot ist

Roter Live-Test: erst die Quelle abfragen, dann einordnen. Nicht aus der
Fehlermeldung schliessen. Am 3.8.2026 hiess "nicht gefunden" nicht, dass der
Datensatz weg war, sondern dass die Quelle die Schreibweise ihrer Kopfzeile
gewechselt hatte — vier von sechs Datensätzen produktiv kaputt, alle
Unit-Tests grün.

**Ein 4xx ist kein Nein.** Am 29.8.2026 antwortete `past-publications` in
`swiss-procurement-mcp` auf jede Publikation mit Losen mit HTTP 400. Daraus war
geschlossen worden, die Quelle verweigere diese Auskunft; der Befund stand
datiert im Fixture-Nachweis, ein Test bestätigte ihn, alles blieb grün. Die
Spec desselben Endpunkts führt einen als *optional* deklarierten Parameter
`lotId` — für Publikationen mit Losen ist er Pflicht. Mit ihm antwortet
dieselbe Publikation mit 200. Ein Projekt trug sieben Vorgängerpublikationen,
die der Server als «Quelle nicht erreichbar» wegwarf.

Drei Handgriffe daraus:

- **Die Parameterliste der Spec durchgehen, bevor ein Statuscode eingeordnet
  wird.** «Optional» heisst dort oft «optional für die Mehrheit».
- **Einer deterministischen Absage keinen Wiederholungsrat geben.** «Nicht
  erreichbar, bitte später erneut» ist bei einem 400 falsch und liest sich für
  das Modell wie eine Störung. Den Status mitführen und den fehlenden
  Parameter benennen — den Status, nicht den Antwortkörper.
- **Beide Antworten aufzeichnen, mit und ohne den Parameter.** Eine
  Aufzeichnung nur des Fehlschlags kann nicht zeigen, dass er vermeidbar war;
  dass nur der 400er aufgezeichnet war, ist der Grund, warum der falsche
  Befund nicht auffiel.

**Und ein 403 ist gar keine Auskunft.** Am 29.8.2026 sollten für 42 Repos die
Dependabot-Labels nachgemessen werden. Alle 13 Abfragen des ersten Stapels
kamen zurück als:

```
Failed to find label: API rate limit already exceeded for user ID 8864492.
```

Der gefährliche Teil steht vorn: Das Werkzeug verpackt eine Sperre als
Fund-Fehlschlag. Wer die Zeile überfliegt oder nur auf ein leeres Ergebnis
prüft, zählt 39 Repos als «Label fehlt» und hat seine eigene Erschöpfung
gemessen. Das Limit hängt am Konto, nicht am Repo — derselbe Vormittag hatte
es mit 42 eröffneten und 42 gemergten PRs verbraucht.

Das ist der Absatz darüber, andersherum gelesen: dort war ein 400 eine echte,
wiederholbare Antwort und galt als Störung; hier ist eine Störung als Antwort
verpackt. Entscheidend ist nie der Statuscode, sondern ob die Quelle überhaupt
geantwortet hat.

- **Positivkontrolle im selben Repo.** Ein «nicht gefunden» wird erst dadurch
  zur Messung, dass eine gleichzeitige Abfrage etwas findet.
- **Die Messung entlang der Sperre teilen.** `raw.githubusercontent.com` ist
  ein CDN und nicht die REST-API. Um 11:19:27 UTC lieferte es für
  `register-mcp` HTTP 200, während die Label-Abfrage desselben Repos in
  derselben Minute die Sperre meldete. Alle 42 `dependabot.yml` kamen so
  durch, während die Label-Hälfte stand.
- **Am Token vorbei geht es nicht.** Beide Umwege enden am Agent-Proxy, und
  jeder mit einer eigenen irreführenden Begründung. `api.github.com` ohne
  Zugangsdaten:

  ```
  GitHub access is not enabled for this session. An org admin must connect
  the Claude GitHub App for this organization.
  ```

  Das ist keine Aussage über die Organisation, sondern das, was ohne Token
  kommt. Wer ihr folgt, sucht einen Admin für ein Problem, das keiner hat.
  Die HTML-Seite `github.com/<owner>/<repo>/labels` fällt ebenfalls, aber
  anders:

  ```
  This GitHub API path is not available: sessions are bound to their
  configured repositories. Use repository-scoped endpoints
  (repos/{owner}/{repo}/...).
  ```

  Der Proxy behandelt also auch `github.com` als API-Pfad; die zweite Meldung
  klingt nach einem Scope-Problem und ist doch nur dieselbe Sackgasse. Den
  Token aus der Umgebung in einen curl-Header zu setzen, blockiert der
  Klassifikator. Ob es überhaupt hülfe, ist offen: die Sperre nennt ein
  Nutzerkonto, und ob der Token zu diesem gehört, wurde nie geprüft.
- **Die Sperre gilt nicht dem Dienst, sondern dem Zugangspfad.** Unmittelbar
  nachdem eine Abfrage der Checks eines PR sauber durchlief, meldete die
  Label-Abfrage weiter die Sperre. Von einem blockierten Werkzeug also nicht
  auf «GitHub ist zu» schliessen — und umgekehrt eine gelungene Abfrage nicht
  als Entwarnung für die gesperrte nehmen. Das ist dieselbe Asymmetrie wie
  bei der verschwundenen Codex-Meldung weiter unten.

Wann die Sperre fällt, geben diese Beobachtungen nicht her. Die Meldung nennt
keinen Zeitpunkt, und die `X-RateLimit`-Kopfzeilen sind hinter dem Proxy nicht
zu sehen. Belegt sind drei gesperrte Zeitpunkte — 11:14, 11:16 und 11:19 UTC.
Wer daraus eine Dauer macht, hat sie erfunden.

**`results[0]` ist nur so verlässlich wie die Zusicherung danach.** Pinnt die
Abfrage einen bekannten Datensatz, ist der erste Treffer eine Drift-Wache und
in Ordnung. Hängt die Zusicherung dagegen davon ab, *welche* Variante die
Quelle heute zuoberst hat, prüft der Test den Tag: am 25.8.2026 rot, weil die
neueste Zürcher Publikation zufällig Lose hatte, am 26.8. grün, ohne dass sich
etwas geändert hätte. Den Fall gezielt wählen und beide Zweige fahren.

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
immer so, und man sieht es dem PR nicht an. Am 21./22.8.2026 sind 75 PRs mit
formal erfülltem Häkchen gemergt worden, ohne dass jemand hineingesehen hat.

**Die Belege zu allem hier — Zeitstempel, Einzelfälle, widerlegte Fassungen —
stehen in [`docs/codex-reviews.md`](docs/codex-reviews.md).** Wer eine der
Regeln anzweifelt oder fortschreiben will, liest dort nach.

### Prüfen, ob geprüft wurde

**Zwei Abfragen, immer beide:** `get_reviews` für das Review-**Objekt**
(«💡 Codex Review» — nur bei Befund), `get_comments` für alles andere. Wer nur
eine nimmt, übersieht die halbe Wahrheit; genau so ist die Kontingent-Meldung
zuerst durchgerutscht.

**Belegt ist eine Prüfung durch ein Review-Objekt *oder* eine
Befundlos-Meldung** («Codex Review: Didn't find any major issues.», Schlusssatz
wechselt). Alles andere belegt nichts.

**Den Text lesen, nicht die Zahl.** `comments: 1` hat fünf Bedeutungen — auch
einen abgeschlossenen Lauf *mit* Befund, denn der steht im Objekt und nicht
unter den Kommentaren. Einen unbekannten Text wörtlich zitieren, statt ihn in
eine bekannte Schublade zu zwingen.

**Die Reaktionen (👀, 👍) belegen nichts** — in keine Richtung.

### Fünf Gründe fürs Schweigen, einer davon harmlos

| Grund | Erkennbar an |
|---|---|
| Kein Befund | Befundlos-Meldung als Issue-Kommentar |
| PR ist Draft | meist gar nichts; am 29.8. kam auf *eine* Draft-Eröffnung doch eine Ausfallmeldung, auf die nächste wieder nicht — worauf ein Draft antwortet, ist offen |
| Kontingent weg | «You have reached your Codex usage limits for code reviews.» |
| Environment fehlt | «To use Codex here, create an environment for this repo.» |
| Environment-Meldung trotz Prüfbarkeit | dieselbe Meldung, aber der nächste Aufruf läuft durch |

**Eine verschwundene Limit-Meldung ist keine Entwarnung** — die Prüfungen
liegen hintereinander, es kann jetzt etwas anderes im Weg sein.

**Bleibt es nach dem automatischen Auslöser still, sagt das nichts über die
Ursache** — und schon gar nicht «der Text ist sauber». Belegt ist allein, dass
kein Review angekommen ist.

### Der Hebel: `@codex review` von Hand

Zwei bis drei Minuten Vorlauf, viermal belegt. Er läuft **auch auf einem Draft**
und **auf einem bereits gemergten PR** an (dort wird der Merge-Commit geprüft).
Nach einer Environment-Meldung lohnt der zweite Versuch.

Wer den Aufruf absetzt, wartet die drei Minuten ab: Die 👀 auf dem auslösenden
Kommentar ist die Empfangsbestätigung, nicht das Ergebnis. Wer nach einer
Minute nachsieht, hält einen laufenden Review für einen ausgefallenen.

**Fussangel:** Wer `@codex review` in einem Kommentar bloss *zitiert*, löst
damit vermutlich einen neuen Lauf aus.

### Ein befundloser Lauf ist kein Freispruch

Am 23.8. lief derselbe Text durch 42 Reviews: 36 mit Befund, 6 ohne — gleiche
Eingabe, gegenteiliges Urteil, in denselben neun Minuten. Ein Ergebnis sagt
etwas über den Lauf, nicht über den Text.

### Portfolio-weit

```
search_pull_requests: user:malkreide commenter:chatgpt-codex-connector[bot] updated:>=<Datum>
search_pull_requests: user:malkreide type:pr reviewed-by:chatgpt-codex-connector[bot] updated:>=<Datum>
```

Beide nötig, **dasselbe `updated:`-Fenster an beiden**, und beide bleiben
Vorfilter: `updated:` datiert den PR, nicht die Prüfung.

### Verfahren für Doku-PRs

Als Draft öffnen, den Review von Hand anfordern, Befunde einarbeiten — und
**nach jeder Korrekturrunde erneut anfordern**, auf dem neuen Head. Auf ready
geht es, wenn ein Lauf auf dem aktuellen Head nichts mehr findet.

Das ist ein Abbruchkriterium, kein Gütesiegel: Derselbe Text kann in der
nächsten Runde wieder einen Befund tragen, und irgendwo muss die Schleife
enden. Sie endet aus praktischen Gründen, nicht weil der Stand bewiesen sauber
wäre.

Die Schleife ergänzt die Reihenfolge, sie ersetzt sie nicht. Wer nach dem
Einarbeiten umschaltet, statt erneut anzufordern, hat genau den Stand
ungeprüft, den er mergt — der Review lief auf der Fassung davor, im
Draft-Zustand läuft kein automatischer nach, und nach dem Umschalten bleiben
erfahrungsgemäss Sekunden. Am 28.8. sind so zwei Fassungen ungeprüft in `main`
gelandet, **beide die Korrektur einer geprüften Fassung.**

Der Grund für den ganzen Aufwand hat mit der Trefferquote nichts zu tun:
**Bei einer ungeprüften Fassung liegt überhaupt kein Ergebnis vor.** Nicht ein
schlechtes, sondern keines.

Der Reihenfolge wegen: Der Review gehört vor den Merge, weil ein Befund danach
einen zweiten PR braucht. Am 28.8. kam einer 28 Sekunden vor dem Merge — die
Behebung landete in einem Nachzügler. Und am 29.8. lagen auf #59 zwischen
Befund und Merge 81 Sekunden; der Defekt stand damit in `main`.

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
