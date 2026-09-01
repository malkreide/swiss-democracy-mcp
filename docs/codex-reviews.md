# Codex-Reviews: was beobachtet wurde

Beobachtungssammlung zum Codex-Review-Bot (`chatgpt-codex-connector[bot]`).
Die **Handlungsregeln** stehen in `CLAUDE.md` — zum Prüfer im Abschnitt «Wenn
Codex gar nicht erst hinsieht», zur Pflege dieser Sammlung unter «Zahlen, die
eine Aufzählung wiederholen». Hier liegen die Belege dazu: Zeitstempel,
Einzelfälle und die Fassungen, die sich als falsch erwiesen haben.

Der Sinn der Trennung: `CLAUDE.md` wird beim Arbeitsbeginn gelesen und muss
kurz sein. Diese Datei wird gelesen, wenn jemand eine der Regeln anzweifelt,
fortschreiben will oder wissen muss, wie belastbar sie ist.

**Wer hier etwas ergänzt:** Eine Erklärung gehört erst hinein, wenn der
entscheidende Vergleich vorliegt. «Fassungen, die nicht hielten» führt die, die
daran gescheitert sind, mehr zu erklären als gemessen war — in zwei Gruppen,
eine zum ursprünglichen Abschnitt und eine zur stillen Draft-Eröffnung. Die
erste Gruppe
schliesst mit der Fassung, die stehen geblieben ist; sie gehört nicht zu den
gescheiterten und steht dort, weil der Unterschied zu ihnen der Punkt ist.

Eine Gesamtzahl steht hier nicht. Am 29.8. wurde sie in drei aufeinander
folgenden Review-Runden dreimal korrigiert: «sechs» gegen «sieben» an zwei
Stellen, dann eine Überschrift mit «drei» über vier Einträgen, dann «acht»,
das die überlebende Fassung mitzählte. Jede Korrektur erzeugte die nächste.

---

## 1. Die sechs Formen, in denen sich ein Lauf zeigt

| Form | Wo | Bedeutet |
|---|---|---|
| «💡 Codex Review» | Review-**Objekt** (`get_reviews`) | Lauf mit Befund |
| «Codex Review: Didn't find any major issues.» | Issue-Kommentar | Lauf ohne Befund |
| «You have reached your Codex usage limits for code reviews.» | Issue-Kommentar | Kontingent weg |
| «To use Codex here, create an environment for this repo.» | Issue-Kommentar | Environment-Meldung |
| Status-Kommentar «🔄 Running» / «✅ Completed» | Issue-Kommentar, **bearbeitet** | Lauf läuft / ist durch |
| gar nichts | — | nichts belegt |

Die ersten fünf verlangen **zwei** Abfragen: `get_reviews` für das Objekt,
`get_comments` für alles andere. Wer nur eine nimmt, übersieht den Rest —
genau so ist die Limit-Meldung zuerst durchgerutscht.

### Der Schlusssatz der Befundlos-Meldung wechselt

Beobachtet: «Swish!», «Delightful!», «Keep it up!», «More of your lovely PRs
please.», «Keep them coming!», «Hooray!», «Breezy!» — und am 29.8. stand dort
statt eines Satzes bloss ein 🚀. Stabil ist nur der Satz davor.

### Der Status-Kommentar (seit 29.8.)

Kenntlich am HTML-Marker `<!-- codex-pull-request-review-summary -->`. Codex
legt ihn zu Beginn eines Laufs an und **aktualisiert ihn an Ort und Stelle**
von «🔄 Running» auf «✅ Completed» — kein zweiter Kommentar, sondern ein
`issue_comment.edited`. Wer nur auf neue Kommentare achtet, sieht das Ende des
Laufs nicht.

Seine Tabelle nennt als Einzige **beides**: den geprüften Commit *und* den
Auslöser («Manual request», «Draft marked ready»). Die Befundlos-Meldung und
das Review-Objekt nennen nur den Commit.

Vorbehalte:

- Kein Beleg für eine abgeschlossene Prüfung — auf «Running» steht er auch
  dann, wenn nie ein Ergebnis folgt.
- Kein Protokoll, sondern **eine einzige Zeile mit dem letzten Lauf**. Ein
  neuer Auslöser überschreibt den vorigen spurlos: Am 29.8. verdrängte auf #61
  der ready-Lauf um 07:19:51 den manuellen von 07:18:38; dessen Ausgang steht
  seither nirgends mehr. Wer zwei Läufe auseinanderhalten will, braucht ihre
  Ergebnis-Kommentare — die bleiben einzeln stehen.

### `comments: 1` hat fünf Bedeutungen

Befundlos-, Kontingent-, Environment-Meldung oder Status-Kommentar — und der
zählt doppelt, weil «🔄 Running» und «✅ Completed» Gegenteiliges heissen.

Die letzte ist die tückischste: Endet ein Lauf **mit** Befund, steht der im
Review-Objekt und damit gar nicht unter den Kommentaren; als einziger Kommentar
bleibt der Status auf «Completed». `comments: 1` kann also einen
abgeschlossenen Lauf mit Befund bezeichnen — wer den Status-Kommentar pauschal
für «läuft noch» hält, verbucht einen fertigen Befund als laufende Prüfung.
Gefunden hat das Codex an der Fassung dieses Absatzes, die genau diesen Fehler
machte.

**Den Text lesen, nicht die Zahl** — und beim Status-Kommentar auch das Feld
daneben. Einen unbekannten Text wörtlich zitieren, statt ihn in eine der
bekannten Schubladen zu zwingen: Der Abschnitt musste erst von drei auf vier
und dann auf fünf Gründe wachsen, die Formen von vier auf sechs.

### Die Reaktionen belegen nichts

Der Infokasten unter jedem Review verspricht eine 👍. Es gibt sie — nur nicht
verlässlich: Am 29.8. trugen #59 und #60 nach ihrem befundlosen Lauf je
`reactions: {"+1": 1}`; in sechs Repos am 23.8. und auf #51 am 28.8. kam sie
nicht (`reactions.total_count: 0`). Zwei Fassungen des Abschnitts führten sie
als Tatsache, eine erklärte sie für widerlegt; beides ging über die
Beobachtungen hinaus.

Und selbst wo sie steht, belegt sie weniger, als sie verspricht: Auf #59 steht
die 👍 an einem PR, der eineinhalb Stunden zuvor einen zutreffenden P2-Befund
bekommen hatte. Sie folgt einem Lauf, nicht dem PR.

Die 👀 sitzt an anderer Stelle — auf dem **auslösenden Kommentar** — und
bedeutet etwas anderes: gesehen, nicht geprüft. Sie ist die
Empfangsbestätigung. Auf #53 stand sie, solange der Lauf lief, und war weg,
nachdem der Review stand; als nachträglicher Nachweis taugt sie damit auch
nicht.

Auch der Infokasten selbst ist keine Quelle: Am 29.8. trugen zwei Kommentare
desselben Bots auf demselben PR zwei verschiedene Fassungen davon — eine mit
`@codex security review` und der 👀/👍-Beschreibung, die andere ohne beides.

---

## 2. Die fünf Gründe fürs Schweigen — und ihre Reihenfolge

Der vierte Grund (Environment) kam erst zum Vorschein, als der dritte
(Kontingent) wegfiel, und das ist kein Zufall: Die Prüfungen liegen
hintereinander.

Dass es diese Reihenfolge ist und nicht die umgekehrte, lässt sich an einem
einzigen Repo ablesen — in `swiss-public-data-mcp` bekam PR #54 am 22.8. um
10:56:55 die Kontingent-Meldung und PR #56 am 23.8. um 08:22:20 die
Environment-Meldung. Läge die Environment-Prüfung vorn, hätte #54 sie schon am
Vortag gesehen; die Environment fehlte ja bereits.

Daraus die Regel: **Eine verschwundene Limit-Meldung ist keine Entwarnung.**
Sie kann bedeuten, dass das Kontingent wieder da ist — und dass jetzt etwas
anderes den Review verhindert.

---

## 3. Ein Ergebnis sagt etwas über den Lauf, nicht über den Text

Am 23.8. lief derselbe Text durch **42 Reviews**: 36 meldeten denselben
P2-Befund, 6 die Befundlos-Meldung — gleiche Eingabe, gegenteiliges Urteil,
alles in denselben neun Minuten.

Am 29.8. dasselbe an einem einzelnen benannten Fehler statt an einer
Verteilung, und deshalb schärfer, weil die richtige Antwort bekannt ist. Der
`reviewed-by:`-Abfrage fehlte das `updated:`-Fenster, das die
`commenter:`-Abfrage daneben trägt, während der Text dazu aufforderte, beide
Ergebnisse zusammenzunehmen. Drei Läufe auf denselben Defekt, neun Minuten:

| Zeit | Commit | Auslöser | Urteil |
|---|---|---|---|
| 07:00:06 | `37b8753` | `@codex review` | befundlos |
| 07:04:53 | `37b8753` | Draft → ready | **P2, zutreffend** |
| 07:09:27 | `789e901`, enthält denselben Defekt | `@codex review` | befundlos |

Zwei Freisprüche und ein Treffer für ein und denselben Fehler. Gefunden hat ihn
nur der Lauf, den niemand mit Absicht angestossen hat.

---

## 4. Drei Wege, den Prüfer zu verlieren

### 4.1 Zu schnell mergen

Am 21./22.8. lagen zwischen «ready for review» und Merge mehrfach drei bis fünf
Sekunden. Codex wird beim Umschalten ausgelöst und braucht danach Zeit.

Am 28.8. bei vier PRs: #50 (3 s), #54 (3 s), #55 (4 s), #56 (4 s) — bei rund
drei Minuten Vorlauf. Am 29.8. kam #63 mit **2 s** dazu (ready 09:43:48, Merge
09:43:50); dort war ohnehin kein Lauf zu verlieren, weil das Kontingent weg war
(«Kontingent und Environment»).

**Was diese Messung nicht hergibt:** Sie beginnt erst *nach* dem Umschalten auf
ready und sagt deshalb nichts darüber, ob ein als Draft gestarteter PR seltener
zu früh zugeht. Warum es so schnell ging, ist ebenfalls nicht gemessen:
Nachlässigkeit, Bedienführung oder etwas Drittes sind von aussen nicht zu
unterscheiden. Belastbar ist allein, dass vor dem Merge zusätzlich umgeschaltet
werden muss.

### 4.2 Der Review ist da, der Merge geht trotzdem durch

Am 29.8. auf #59: Um 07:04:53 stand der P2-Befund am PR, mit Datei und Zeile.
Um 07:06:14 wurde gemergt — 81 Sekunden später, mit dem befundbehafteten
Commit als Head. Der Fix-Commit existierte da noch nicht; er trägt 07:06:28.
Weiter trägt das Committer-Datum nicht — ob die Behebung schon fertig im
Arbeitsverzeichnis lag, sagt es nicht. Belegt ist allein, dass der Merge keinen
vorhandenen Commit übergehen konnte. Der Defekt stand in `main`, und es
brauchte den Nachzügler #60.

**Was von aussen messbar ist, ist der Zustand, nicht die Aufmerksamkeit.**
Belegt ist: Beim Merge war der Befund weder beantwortet noch im Head behoben.
Ob niemand hingesehen hat oder jemand gelesen und sich dagegen entschieden
hat, ist an denselben Zeitstempeln nicht zu unterscheiden — eine frühere
Fassung behauptete hier das Erste und konnte es nie belegen.

Der Unterschied zu 4.1 ist der Punkt: Dort ging der Prüfer verloren, hier hat
er geliefert und der Merge ging trotzdem durch. Deshalb steht die Checkliste
im PR-Template auf «beantwortet oder behoben», nicht auf «Review gelaufen» —
sie fragt genau den Zustand ab, der messbar ist.

### 4.3 Derselbe PR bekommt auf dieselbe Frage verschiedene Antworten

Am 28.8. auf PR #53, alles innerhalb von acht Minuten:

| Zeit | Auslöser | Antwort |
|---|---|---|
| 18:43:41 | Draft → ready (18:43:37) | «To use Codex here, create an environment» |
| 18:46:52 | `@codex review` (18:43:51) | vollständiger Review, drei P2-Befunde |
| 18:51:30 | Kommentar (18:51:20) bzw. Push | «To use Codex here, create an environment» |

Fehlschlag, Erfolg, Fehlschlag — derselbe PR, dasselbe Repo, dasselbe Konto.
**Warum, ist offen.** Zwei Erklärungen sind verträglich:

- **Der Auslöser entscheidet.** Der automatische Weg verlangt die Environment,
  der ausdrückliche Aufruf umgeht sie. Dann fehlt die Environment durchgehend.
- **Die Prüfung selbst ist unstet.** Dann sagt der Weg nichts.

Die dritte Zeile könnte entscheiden — aber genau bei ihr ist der Auslöser nicht
eindeutig. Was es bräuchte: ein Erfolg **und** ein Fehlschlag auf demselben
zweifelsfrei bestimmten Auslöser.

**Eine Beobachtung kommt nahe heran.** PR #60 wurde am 29.8. um 07:09:06 als
Draft eröffnet, um 07:09:10 ging genau ein `@codex review` hinaus:

| Zeit | Antwort |
|---|---|
| 07:09:17 | «To use Codex here, create an environment for this repo» |
| 07:09:24 | Lauf startet, Auslöser laut Status-Kommentar «Manual request» |

Sieben bzw. vierzehn Sekunden nach demselben Aufruf, Fehlschlag und Erfolg.
Zweifelsfrei ist es trotzdem nicht: Dass ein Draft die automatischen Auslöser
nicht anlaufen lässt, ist eine Behauptung dieser Sammlung, keine hier gemessene
Grösse. Gilt sie nicht, kann die Environment-Meldung von der Eröffnung vier
Sekunden zuvor stammen — und dafür spricht seit dem 29.8. die Beobachtung
gleich unten. Diese Zeile trägt damit weniger, als sie beim Aufschreiben trug.

**Der Versuch ist am 29.8. halb gelaufen — und er fiel gegen die Behauptung.**
PR #64 wurde um 09:52:31 als Draft eröffnet. Elf Sekunden später, um 09:52:42,
stand die Kontingent-Meldung da, Kommentar-ID `5461650608`. Der einzige
`@codex review` auf diesem PR trägt dieselbe Sekunde, aber die höhere ID
`5461650666` — er kam danach, und eine Wirkung geht ihrer Ursache nicht voraus.
Der PR-Text nennt `@codex` nirgends. Als Ursache blieb damit die Eröffnung —
bis der saubere Versuch elf Minuten später das Gegenteil zeigte.

Halb gelaufen, weil der Versuch einen Draft **ohne** jeden Aufruf verlangte und
hier acht Sekunden darauf doch einer kam, mit eigener Antwort um 09:52:50. Für
die Reihenfolge reicht es trotzdem.

**Was es nicht zeigt:** dass eine Draft-Eröffnung einen *Lauf* auslöst.
Beobachtet ist eine Ausfallmeldung bei erschöpftem Kontingent. Ob der Connector
auf jedes PR-Ereignis mit dieser Meldung antwortet und den Review dennoch erst
ab ready startet, ist offen; dafür bräuchte es denselben Versuch bei freiem
Kontingent. Belegt ist nur: Auf diesem einen Draft kam vor jedem Aufruf eine
Antwort.

**Die saubere Replikation misslang — elf Minuten später, im selben Repo.**
PR #65 wurde um 10:03:12 als Draft eröffnet, diesmal **ohne jeden** `@codex
review`. Das ist der Versuch, wie er oben verlangt war. Nach 5 min 17 s war
weder ein Kommentar noch ein Review-Objekt da — das Vierzehnfache der
beobachteten Obergrenze von 22 Sekunden.

**Weiter als diese 317 Sekunden trägt die Beobachtung nicht.** Löst eine
Eröffnung aus und antwortet der Connector erst später — oder scheitert er vor
dem sichtbaren Ergebnis —, sieht das im Messfenster genauso aus. «Der manuelle
Aufruf: was belegt ist» hält für #51 fest, warum sich das von aussen nicht
trennen lässt: «nichts kam an» ist nicht «nichts wurde ausgelöst». Der
Kontingentzustand während der 317 Sekunden ist ebenfalls nicht beobachtet;
belegt sind Sperren um 10:00:34
und um 10:11:22, davor und danach.

**Was #65 hergibt, in einem Satz:** Auf eine Draft-Eröffnung kam binnen
317 Sekunden keine sichtbare Antwort. Nicht mehr — weder über das Auslösen noch
über spätere Antworten noch über das Kontingent. Drei frühere Fassungen dieses
Absatzes behaupteten jeweils mehr; sie stehen unter «Fassungen, die nicht
hielten».

Damit fällt die Zuschreibung, nicht die Beobachtung. Auf #64 kam eine Antwort
vor meinem Aufruf — die Kommentar-IDs sind monoton, daran ändert #65 nichts. Ob
die Eröffnung sie ausgelöst hat, ist offen. Übrig bleiben zwei Lesarten,
zwischen denen hier nichts entscheidet: Der Connector antwortet auf Eröffnungen nur manchmal,
oder auf #64 wirkte etwas, das in den Ereignissen nicht sichtbar ist.

**Der Vergleich innerhalb eines PRs macht es noch deutlicher.** #65 lieferte
beides, acht Minuten auseinander, am selben PR:

| Ereignis auf #65 | Antwort |
|---|---|
| Eröffnung als Draft 10:03:12 | nach 5 min 17 s nichts |
| ready 10:11:20 | Meldung nach **2 s** |

Derselbe PR, derselbe Connector. **Dass ready auslöst, ist gut belegt** — zwei
saubere Messungen, beide zwei Sekunden. Über die Eröffnung sagt die Zeile
darüber nur, dass binnen 317 Sekunden nichts sichtbar wurde. Die Antwort auf #64 vor meinem Aufruf bleibt als Einzelfall stehen und
ist nicht erklärt.

**Eine zusammenfassende Regel steht hier nicht mehr.** Alle Fassungen, die es
versucht haben, sind daran gescheitert, aus zwei Zeitreihen eine Aussage über
Ursachen zu machen; «Fassungen, die nicht hielten» zählt sie. Die letzte
behauptete noch, «ein Draft löst nie etwas aus» sei widerlegt —
wofür es einen kausal zugeordneten Fall bräuchte, den weder #64 noch #65
hergibt. Was gemessen ist, steht oben und in der Tabelle. Wer mehr will,
braucht Wiederholungen bei freiem Kontingent, wo ein Lauf und nicht nur eine
Ausfallmeldung zu sehen wäre.

**Ein Push auf denselben Draft blieb 100 Sekunden lang ohne sichtbare Antwort.** Um 09:56:42 ging ein
zweiter Commit auf #64 hinaus; 100 Sekunden später stand immer noch keine
weitere Meldung da. Die beobachtete Obergrenze für Ausfallmeldungen liegt bei
22 Sekunden, das Fünffache war also verstrichen — und der Connector unterdrückt
Wiederholungen nicht, er hatte auf diesem PR schon zweimal binnen acht Sekunden
geantwortet. Beweisend ist ein einzelnes stilles Fenster trotzdem nicht; es
passt aber zu der Zeile unter «Zum Verfahren für Doku-PRs», wonach im
Draft-Zustand nach einer Korrektur kein Lauf nachkommt. Eröffnung und Push sind
hier verschiedene Dinge, und nur nach der Eröffnung wurde etwas sichtbar. Was
jeweils ausgelöst wurde, sagt auch dieser Absatz nicht — aus demselben Grund wie
oben.

**Vermutlich eine Fussangel:** Die dritte Zeile oben kam zehn Sekunden nach
einem Kommentar, der `@codex review` in einer Tabelle bloss *zitierte*, und
siebzig Sekunden nach einem Push. Der Abstand spricht für den Kommentar — die
beiden anderen Läufe antworteten nach vier und zehn Sekunden —, entscheiden
lässt es sich mit einer Beobachtung nicht. Wer beim Beantworten eines Reviews
aus ihm zitiert, sollte mit einem neuen Lauf rechnen.

---

## 5. Der manuelle Aufruf: was belegt ist

Viermal geliefert, erstaunlich gleichmässig:

| PR | Vorlauf |
|---|---|
| #45 | 2 min 31 s |
| #51 | 2 min 57 s |
| #53 | 3 min 1 s |
| #55 (Draft!) | 2 min 14 s |

Einmal gescheitert (#53 um 18:51:30, siehe den Abschnitt über die schwankenden
Antworten). Nach einem Fehlschlag lohnt der zweite Versuch.

**Auf einem Draft läuft er an** — #55 ist der Beleg. Dass umgekehrt die
automatischen Auslöser den ready-Zustand *brauchen*, stand hier lange
unwidersprochen daneben; seit dem 29.8. ist es fraglich (siehe den Abschnitt
über die schwankenden Antworten).

**Auf einem gemergten PR läuft er an** — #45 war seit 70 Minuten gemergt, #51
seit knapp 14 Stunden; beide bekamen ihren Review. Geprüft wird dann allerdings
der **Merge-Commit**, nicht der Branch-Stand: Der Aufruf auf dem gemergten #59
am 29.8. um 07:07:24 lieferte um 07:09:27 einen Review von `789e901`.

**Ein Lauf kann einen Merge überleben.** Auf #60 startete am 29.8. um 07:11:27
ein Lauf, um 07:11:53 wurde gemergt, und um 07:12:44 stand er auf «Completed».
Was zwei Fassungen lang als eigener Grund dastand — der Merge töte einen
laufenden Job — ist damit als allgemeine Regel widerlegt.

**Überleben heisst aber nicht, dass ein Ergebnis ankommt.** Schon für diesen
#60-Lauf ist keines zuzuordnen: Die Befundlos-Meldung von 07:11:04 liegt
**vor** seinem Start um 07:11:27 und gehört damit zu einem früheren Lauf. Nach
dem Merge kam nur noch die «Completed»-Zeile.

Auf #79 dasselbe, dort ohne Verwechslungsmöglichkeit: Aufruf 18:31:52, Lauf ab
18:32:05, ready 18:32:33, Merge 18:32:40, «Completed» um 18:34:05 — 85 Sekunden
nach dem Merge. Auf dem PR steht überhaupt keine Ergebnis-Meldung: kein
Review-Objekt und keine Befundlos-Meldung (`get_reviews` leer, insgesamt zwei
Kommentare, nachgeprüft um 18:37).

Was das **nicht** hergibt: ob die Läufe nichts gefunden haben oder ob nach dem
Schliessen nichts mehr zugestellt wird. Von aussen sieht beides gleich aus —
dieselbe Trennung wie zwischen «nichts kam an» und «nichts wurde ausgelöst».
Dazu kommt, dass sich die beiden Läufe auf #79 nicht auseinanderhalten lassen:
Die Statuszeile nannte zuletzt «Draft marked ready» und hatte den manuellen
Auslöser von 18:32:05 damit überschrieben.

**Auf #88 dann ohne diesen Vorbehalt.** Am 31.8. war der ready-Lauf der einzige
im Fenster, und seine Zeile blieb unüberschrieben: ready 04:43:45, Start
04:43:50, Merge 04:43:53, «Completed» um 04:46:12 — 139 Sekunden nach dem
Merge. Angekommen ist nichts: kein Review-Objekt zu `1466fd7`, und die einzige
Befundlos-Meldung trägt 04:29:23, liegt damit **vor** dem Start dieses Laufs
und gehört zum manuellen Aufruf davor. Dieselbe Prüfung wie bei #60, nur dass
hier kein zweiter Lauf danebensteht, der die Zuordnung zerreden könnte.

Das klärt aber nur, *welcher* Lauf kein Ergebnis lieferte, nicht warum. Ob er
nichts fand oder ob nach dem Schliessen nichts mehr zugestellt wird, ist auch
hier nicht zu unterscheiden — die Frage darüber bleibt offen, und eine saubere
Zuordnung beantwortet sie nicht.

**Zugestellt wird aber durchaus.** Auf #80 wurde um 18:48:36 gemergt, und um
18:48:45 — neun Sekunden danach — erschien ein Review-Objekt mit Befund zum
Head `836568f`. Ein Ergebnis kann den Merge also überholen; dass auf #60 und
#79 keines ankam, liegt nicht daran, dass nach dem Schliessen grundsätzlich
nichts mehr zugestellt würde.

Praktisch heisst das: **Nach einem frühen Merge kann am PR nicht mehr
ablesbar sein, ob geprüft wurde** — verlassen kann man sich weder darauf noch
auf das Gegenteil. Wer es wissen muss, sieht nach: `get_reviews` für das
Objekt, `get_comments` für die Befundlos-Meldung. Steht dort nichts, ist der
Rückgriff ein neuer Aufruf von Hand — er läuft auf dem gemergten PR an, prüft
dann aber den Merge-Commit.

### Beide Wege können funktionieren

Automatisch hat geliefert (#45 um 08:55:43, ohne jeden vorherigen Kommentar auf
dem PR) und versagt (#53 um 18:43:41); von Hand hat geliefert (#45, #51, #53,
#55) und versagt (#53 um 18:51:30). Über den *Einfluss* des Wegs sagt das
nichts: Bei 1 Fehlschlag von 2 gegen 1 von 4 wäre ein Unterschied mit diesen
Zahlen nicht zu sehen.

### Fälle, die weniger taugen, als sie aussehen

**#51** (ready 04:35:22, gemergt 04:44:00, nichts in 8 min 38 s; manuell um
18:33:48 → Befundlos-Meldung um 18:36:45): Warum dort nichts kam, ist offen.
Ein manueller Lauf mit knapp drei Minuten begrenzt nicht, wie lange der
automatische Weg vierzehn Stunden früher gebraucht hätte, und «nichts kam an»
ist von aussen nicht von «nichts wurde ausgelöst» zu trennen.

**#50** (ready 04:26:01, gemergt 04:26:04) gehört dagegen in 4.1: drei Sekunden
erklären ihn vollständig.

**#45 gegen #46:** Beide tragen denselben Sekundenstempel bei der Eröffnung
(08:53:57), #45 bekam um 08:55:43 seinen automatischen Review, #46 bis zum
Merge fünf Stunden später gar nichts. Daraus «der Auslöser fällt pro PR aus» zu
folgern geht nicht: Für #46 ist nicht belegt, dass er zum fraglichen Zeitpunkt
überhaupt ready war.

---

## 6. Kontingent und Environment

### Der Ausfall vom 21./22.8.2026

Zwischen 08:41 und 09:48 am 21.8. war das Code-Review-Kontingent aufgebraucht —
davor echte Reviews, danach in 30 Repos nur noch die Limit-Meldung. In der
Zwischenzeit sind 32 PRs mit formal erfülltem Häkchen gemergt worden, ohne dass
jemand hineingesehen hat, und am 22.8. noch einmal 43.

Vier Zeitpunkte sind belegt: letzter gelungener Review am 21.8. um 08:41, erste
Limit-Meldung um 09:48, letzte beobachtete Limit-Meldung am 22.8. um 11:03,
erste *andere* Meldung am 23.8. um 08:22.

**Zur Dauer.** Zwischen erster und letzter Limit-Meldung liegen 25 h 15 min.
Das ist der Abstand zweier Fehlschläge, nicht die Dauer einer Sperre. Wer ihn
Untergrenze nennt, hat die durchgehende Erschöpfung schon vorausgesetzt, die er
belegen soll: Öffnete sich das Fenster zwischendurch und schloss es sich durch
neue Auslöser wieder, waren es zwei kurze Sperren.

Nach oben trägt die Rechnung dagegen: Die längste verträgliche Sperre reicht
vom letzten Erfolg um 08:41 bis zur abweichenden Meldung um 08:22, also
**47 h 41 min**. Wer ab der ersten Limit-Meldung rechnet, unterschlägt die 67
Minuten, in denen das Kontingent schon weg gewesen sein kann.

Beobachtungspunkte sind keine Messreihe — die 21 Stunden vor der abweichenden
Meldung liefen ganz ohne Codex-Auslöser.

### Die zweite Episode am 29.8.2026

Dass sie nicht dieselbe ist wie die vom 21./22.8., ist belegt und nicht bloss
plausibel: Dazwischen liefen Reviews durch, an diesem Morgen noch in diesem
Repo. Der letzte gelungene Lauf trägt **07:27:07** — Review-Objekt auf #61 zum
Commit `2f04077`, der Status-Kommentar nennt «Completed
2026-08-29T07:27:10.829173Z».

Danach diese Fehlschläge, alle mit derselben Meldung:

| Zeit | PR | Auslöser | Abstand |
|---|---|---|---|
| 09:12:25 | #62 | `@codex review` um 09:12:03 | 22 s |
| 09:29:43 | #62 | Merge um 09:29:40 | 3 s |
| 09:39:26 | #63 | `@codex review` um 09:39:17 | 9 s |
| 09:43:51 | #63 | ready 09:43:48, Merge 09:43:50 | 3 s bzw. 1 s |
| 09:52:42 | #64 | Eröffnung als Draft um 09:52:31 | 11 s |
| 09:52:50 | #64 | `@codex review` um 09:52:42 | 8 s |
| 10:00:34 | #64 | ready 10:00:32, **ohne** Merge | 2 s |
| 10:11:22 | #65 | ready 10:11:20, **ohne** Merge | 2 s |
| 10:15:03 | #66 | ready 10:15:02, Merge 10:15:03 | 1 s bzw. 0 s |
| 10:45:33 | #66 | `@codex review` um 10:45:22 | 11 s |

**Der Beginn ist auf 1 h 45 min 18 s eingegrenzt** — zwischen dem letzten
Erfolg um 07:27:07 und dem ersten Fehlschlag um 09:12:25. Das entsprechende
Fenster beim Ausfall vom 21./22.8. war mit 67 Minuten **enger**, um 38 min 18 s.

**Das Ende ist auf 1 h 10 min 2 s eingegrenzt** — zwischen dem letzten
Fehlschlag um 10:45:33 und dem ersten wieder gelungenen Lauf um 11:55:35, den
der Status-Kommentar auf #66 als «Completed» führt und der einen P2 lieferte.
Auch die erste Episode hat ein eingegrenztes Ende — zwischen der letzten
Limit-Meldung am 22.8. um 11:03 und der abweichenden Meldung am 23.8. um 08:22,
also 21 h 19 min, und genau diese Grenze führt der Abschnitt darüber schon als
obere Schranke. Der belegte Unterschied ist deshalb nicht «offen gegen
eingegrenzt», sondern die Weite: 1 h 10 min 2 s gegen 21 h 19 min. Beim Beginn
liegt es umgekehrt.

**Zur Dauer gibt sie trotzdem so wenig her wie die erste.** Zwischen erstem und
letztem Fehlschlag liegen 1 h 33 min 8 s, dichter abgetastet als im August — die
Punkte der Tabelle oben gegen dort zwei, und ihre Auslöser sind voneinander
unabhängig. Dichter heisst trotzdem nicht lückenlos: Zwischen zwei Fehlschlägen
kann sich das Fenster geöffnet und durch den nächsten Auslöser wieder
geschlossen haben.

**Das Dashboard blieb zu.** `chatgpt.com/codex/cloud/settings/usage` beantwortet
einen Abruf ohne ChatGPT-Anmeldung mit HTTP 403. Welches Limit griff — rollendes
Fünf-Stunden-Fenster oder Wochenlimit —, ist deshalb auch für diese Episode
offen. Die Frage lässt sich ohne Anmeldung nicht am Dashboard klären, wohl aber
am Verhalten des Bots: Er sagt selbst, dass er nicht kann.

**Eine Sperre bremst die Auslöser nicht.** Mehrere Zeilen der Tabelle hängen
zeitlich an einem Merge, der während der Sperre stattfand — bei #62 eindeutig,
bei #63 und #66 bleibt offen, ob ready oder der Merge auslöste, weil beide in
dieselbe oder die benachbarte Sekunde fallen. Warum diese PRs gerade da gemergt
wurden, ist von aussen nicht zu sehen und steht deshalb nicht hier. Festzuhalten
ist nur, dass eine Sperre weitere Versuche nicht verhindert. Ob ein abgewiesener
Versuch selbst etwas kostet, ist nicht bekannt.

### Die Meldung hat am 29.8. einen zweiten Satz bekommen

Beobachtet auf PR #62 um 09:12:25, wörtlich:

```
You have reached your Codex usage limits for code reviews. You can see your
limits in the [Codex usage dashboard](https://chatgpt.com/codex/cloud/settings/usage).
```

Bis dahin war nur der erste Satz beobachtet. Der zweite nennt erstmals eine
Adresse: `chatgpt.com/codex/cloud/settings/usage` — nicht dieselbe wie die für
die Environment (`.../environments`) und nicht dieselbe, die der Infokasten
verlinkt (`.../general`).

Die Antwort kam **22 Sekunden** nach dem Aufruf — der höchste beobachtete Wert.
Die Untergrenze liegt tiefer als die vier Sekunden, die hier zuerst standen:
Die beiden automatischen Auslöser derselben Episode antworteten nach drei
Sekunden ab Merge (#62) und nach drei Sekunden ab ready beziehungsweise einer
ab Merge (#63, die beiden Ereignisse liegen zwei Sekunden auseinander). Welches
der beiden auslöst, trennen diese Beobachtungen nicht — unter beiden Lesarten
fällt die frühere Grenze.

**Der saubere Fall kam um 10:00:32.** #64 wurde auf ready umgeschaltet, ohne
Merge dahinter; zwei Sekunden später stand die Meldung da. Hier ist der Auslöser
eindeutig, weil kein zweites Ereignis danebenliegt. Die Untergrenze stützt sich
deshalb auf diesen Fall und nicht auf die mehrdeutige Sekunde aus #63 — die
bleibt stehen, trägt aber nichts.

Elf Minuten später wiederholte sich der Wert: #65, ready 10:11:20, Meldung
10:11:22, ebenfalls ohne Merge dahinter. **Zwei saubere Messungen, beide
zwei Sekunden.**

Beobachtet sind damit 2 bis 22 Sekunden für eine Ausfallmeldung gegen zwei bis
drei Minuten für einen echten Lauf. Wer nach einer halben Minute etwas sieht,
sieht keinen Review.

### Die Korrekturschleife verbraucht das Kontingent

Das Verfahren für Doku-PRs verlangt nach jeder Korrekturrunde einen neuen Lauf.
PR #58 brauchte davon fünf, und am 28./29.8. sind über beide Sessions hinweg
rund fünfzehn Läufe an einem einzigen Abschnitt zusammengekommen. Am 29.8. um
09:12 war das Kontingent weg — ausgerechnet auf dem PR, der diese Sammlung
anlegt.

Ein Zusammenhang ist damit **nicht belegt**: Was sonst noch auf das Konto ging,
ist von hier aus nicht zu sehen, und die Sperre kann andere Ursachen haben. Wer
das Verfahren anwendet, sollte aber wissen, dass es nicht gratis ist und bei
langen Korrekturketten an eine Grenze stossen kann. Blockiert es, bleibt der PR
Draft, bis wieder ein Lauf durchgeht.

### Wie das Kontingent funktioniert

Es hängt am Konto, nicht am Repo, und Code-Reviews haben einen eigenen Topf —
nur GitHub-getriggerte Reviews zählen hinein. ChatGPT-Pläne fahren ein
rollendes Fünf-Stunden-Fenster plus Wochenlimits; welches greift, steht im
Codex-Dashboard.

Welches 2026 im August griff, ist **offen**. Die Lücke oben schliesst das
Fünf-Stunden-Fenster nicht aus: Es kann sich zwischendurch geöffnet und durch
neue Auslöser wieder erschöpft haben. Eine lange Reihe von Fehlschlägen belegt
eine lange Reihe von Fehlschlägen, nicht ihre Ursache.

Zeigt das Dashboard freies Kontingent, während Reviews weiter scheitern, sagt
das noch nicht, woran es liegt: Ein Draft, eine fehlende Environment und die
unstete Prüfung aus «Ein Ergebnis sagt etwas über den Lauf, nicht über den
Text» erzeugen dasselbe Bild. Bekannt ist, dass es bei mehreren verbundenen
Konten einen Fehler gibt, den ein Trennen und
Neuverbinden des GitHub-Connectors behebt — aber das ist eine Möglichkeit unter
mehreren. Wer sofort trennt, kostet unter Umständen eine funktionierende
Verbindung für eine Diagnose, die er nicht gestellt hat. Vorher die anderen
Gründe in ihrer Reihenfolge ausschliessen (siehe die Gründe fürs Schweigen und
ihre Reihenfolge).

### Die Environment

Anlegen unter `chatgpt.com/codex/cloud/settings/environments`, und zwar **je
Repo**. Die Meldung sagt es selbst («for this repo»), und am 23.8. war es genau
so: In `swiss-public-data-mcp` fehlte sie, dort kam kein Review; in den übrigen
Repos lief Codex am selben Morgen durch. Eine Environment fürs Konto genügt
nicht.

---

## 7. Portfolio-weit nachsehen

Zwei Abfragen, aus demselben Grund, aus dem am einzelnen PR `get_reviews` und
`get_comments` beide nötig sind:

```
search_pull_requests: user:malkreide commenter:chatgpt-codex-connector[bot] updated:>=<Datum>
```

Findet, wo er *kommentiert* hat — Befundlos-Meldung und die beiden
Ausfallmeldungen, die aber nicht voneinander; dafür ist der Text zu lesen. Ein
Review **mit** Befund ist kein Kommentar und taucht hier nicht auf.

```
search_pull_requests: user:malkreide type:pr reviewed-by:chatgpt-codex-connector[bot] updated:>=<Datum>
```

Findet die Review-**Objekte**, also die Läufe mit Befund. Hier fehlt umgekehrt
jeder befundlose Review.

Keine der beiden allein beantwortet «wurde geprüft?». Wer sich auf `commenter:`
verlässt, übersieht die Repos mit Befund; wer sich auf `reviewed-by:` verlässt,
hält die befundlos geprüften für ungeprüft.

**Dasselbe `updated:`-Fenster gehört an beide**, sonst sind ihre Ergebnisse
nicht zusammenzurechnen: Ohne Fenster liefert `reviewed-by:` jeden je geprüften
PR, und ein Repo mit einem Review vom Juni sähe im August-Fenster geprüft aus.

Auch mit Fenster bleiben es Vorfilter. `updated:` datiert den **PR**, nicht die
Prüfung — ein im Juni geprüfter PR, den im August irgendein Kommentar berührt,
fällt weiterhin hinein. Und beide zusammen reichen nur so weit, wie es
PR-Aktivität gab; Repos ohne tauchen in keiner auf.

### Die Messung vom 23.8.2026

Über die 41 Server-Repos: **25 mit mindestens einem echten Review, 16 nur mit
Absagen.** Zwei Vorbehalte: «Belegt» heisst «damals» — ein Review vom 16.8.
sagt über den heutigen Stand nichts. Und aus der Abfrage fällt nur die 25; die
16 verlangt, dass jemand in diesen Repos die Kommentartexte gelesen hat. Wer
sie als 41 − 25 ausrechnet, zählt jeden befundlosen Review als Absage.

Nicht mit der anderen Zahl desselben Tages verrechnen: Die 25 zählt Repos, die
42 aus «Ein Ergebnis sagt etwas über den Lauf, nicht über den Text» zählt
Reviews.

---

## 8. Zum Verfahren für Doku-PRs

Das Verfahren selbst steht in `CLAUDE.md`. Hier, was bei seiner Einführung
beobachtet wurde.

**Der erste Einsatz hat den Fehler nicht verhindert.** PR #57, der das
Verfahren einträgt, wurde nach dem manuellen Aufruf zu früh auf ready gesetzt
und 2 min 30 s später gemergt — vor seinem Review. Wer das Verfahren
übernimmt, soll wissen, dass es beim ersten Mal nicht eingehalten wurde und
woran es lag: am Umschalten, nicht am Aufruf.

**Die Korrekturschleife kam erst durch einen Befund hinein.** Die erste Fassung
verlangte nur «Draft, Review, dann ready» — und liess damit ausgerechnet den
Stand ungeprüft, der gemergt wird: Sobald der erste Review einen Befund
liefert, verändert dessen Einarbeitung den Head. An den Daten belegt: Von den
Fassungen des Abschnitts sind am 28.8. zwei ungeprüft in `main` gelandet, und
**beide waren die Korrektur einer geprüften Fassung** (`465fd9b` nach
`4c19aff`, `abc15e3` nach `ccf476d`).

**Der Abschnitt selbst brauchte fünf Runden.** Sieben P2-Befunde, keiner
bestritten, danach ein befundloser Lauf auf dem aktuellen Head. Der Text hat in
jeder Runde Behauptungen verloren und keine gewonnen.

**Befund und Merge in derselben gemessenen Sekunde.** Auf #76 ging das
Review-Objekt zu Head `65519e8` um 17:20:46 UTC ein; der Merge trägt denselben
Sekundenwert. Was das **nicht** hergibt: einen Abstand von null, und nicht
einmal die Reihenfolge — feiner ist hinter dem Proxy nicht zu messen. Was es
hergibt: dass hier keine nutzbare Reaktionszeit nachweisbar ist. Eine Warnung
auf dem PR stand gut eine halbe Minute später und kam zu spät; der Befund («die
letzte Zeile» einer wachsenden Tabelle) stand damit in `main` und brauchte #78.
Die Checkliste «kein offener Befund beim Merge» blieb unabgehakt und stimmte
damit. Neben den 28 Sekunden vom 28.8. und den 81 Sekunden auf #59 ist das der
Fall, in dem Aufpassen nichts mehr ausrichtet — wer sicher sein will, wartet
das Ergebnis ab.

**Umschalten auf ready ist hier die Merge-Entscheidung.** Der ready-Auslöser
startet einen Lauf; sein Ergebnis kam in diesen drei Fällen erst nach dem
Merge:

| PR | ready | Merge | Abstand | Ergebnis des ready-Laufs |
|---|---|---|---|---|
| #83 | 18:13:32 | 18:13:33 | 1 s | 18:14:35, 62 s nach dem Merge |
| #84 | 18:22:00 | 18:22:02 | 2 s | 18:23:40, 98 s danach |
| #86 | 03:41:18 | 03:41:21 | 3 s | 03:42:50, 89 s danach |

Die Ergebniszeiten stammen aus der Statuszeile des jeweiligen Laufs mit
Auslöser «Draft marked ready». **Nicht mit den zwei bis drei Minuten der
manuellen Aufrufe verrechnen:** Diese ready-Läufe brauchten **63 bis 100
Sekunden ab dem Umschalten** — die Zahlen in der Tabelle sind die Abstände zum
Merge und ein bis zwei Sekunden kleiner. Der Abstand von ein bis drei
Sekunden liegt weit darunter — mehr sagt die Tabelle nicht, und für andere
Fälle ist die Reihenfolge damit nicht behauptet. **Die Spanne ist auch kein
Deckel:** Der ready-Lauf auf #88 stand am 31.8. um 04:43:50 auf «Running» und
um 04:46:12 auf «Completed», also 142 Sekunden reine Laufzeit. Das ist aus der
Statuszeile des Laufs gemessen und damit ab seinem Start, während die 63 bis
100 Sekunden ab dem Umschalten laufen — einem Zeitpunkt wenige Sekunden davor.
In beiden Bezugsrahmen liegt der Wert über der Spanne. **Was das kostet,
ist an #83 gemessen:** Dort lag seit 18:05:51 ein P1 offen — die Löschregel
löschte ungemergte Branches, an einem Bare-Repo nachgestellt —, und der Merge
um 18:13:33 nahm ihn mit nach `main`. Behoben erst in #84.

**Der Rückweg fehlt.** Ein Umschalten lässt sich nicht zurücknehmen:
`update_pull_request` mit `draft: true` scheitert mit «does not have permission
to convert the pull request to draft». Wer umschaltet, hat einen Auslöser
betätigt, den er nicht mehr anhält.

**#87 hat den Befund beim eigenen Merge vorgeführt.** Der PR, der diesen
Abschnitt einträgt, wurde am 31.8. zwei Sekunden nach dem Umschalten gemergt:

| Zeit (UTC) | Ereignis | Quelle |
|---|---|---|
| 04:06:22 | Lauf startet auf `567e2ce`, Auslöser «Manual request» | Statuszeile, Fassung von 04:06:24 |
| 04:07:26 | Umschalten auf ready | `pull_request.ready_for_review` |
| 04:07:28 | gemergt | `merged_at` |
| 04:07:35 | Lauf startet auf `567e2ce`, Auslöser «Draft marked ready» | Statuszeile, Fassung von 04:07:38 |
| 04:09:48 | P2-Befund zu `567e2ce` | Review-Objekt |

Was der Ablauf hergibt:

- **Der Merge hält einen betätigten Auslöser nicht an.** Der ready-Lauf
  startete sieben Sekunden *nach* dem Merge. Dass ein Lauf einen Merge
  überlebt, hält der Abschnitt «Der manuelle Aufruf: was belegt ist» schon
  fest; dass einer danach überhaupt erst anläuft, ist der Fall daneben — und
  die schärfere Fassung von «der Rückweg fehlt».
- **Der Befund kam 140 Sekunden nach dem Merge** und stand damit in `main`.
  Behoben im Folge-PR, dieselbe Reihenfolge wie bei #59/#60 und #85/#86.
- **Die Überschreibung der Statuszeile, zum dritten Mal.** Die Zeile mit
  «Manual request» verschwand, als der ready-Lauf die Tabelle belegte — nicht
  danebengestellt, ersetzt. Beide Startzeiten stehen oben nur, weil die
  Webhook-Ereignisse die frühere Fassung konserviert haben; auf dem PR selbst
  ist sie nicht mehr zu sehen. Am Verhalten ist damit nichts neu: Dasselbe
  steht unter «Die sechs Formen, in denen sich ein Lauf zeigt» für #61, wo der
  ready-Lauf um 07:19:51 den manuellen von 07:18:38 verdrängte, und unter «Der
  manuelle Aufruf: was belegt ist» für #79. Der Fall zählt als weiterer Beleg,
  nicht als neuer Befund — und er führt vor, was die Überschreibung kostet.

Was der Fall **nicht** hergibt: welcher der beiden Läufe den Befund von
04:09:48 lieferte. Das Review-Objekt nennt den Commit, nicht den Auslöser;
beide Läufe sassen auf `567e2ce`. Aus dem jeweiligen Start ergäbe sich eine
Dauer von 206 Sekunden für den manuellen und 133 für den ready-Lauf; beide
liegen über der Spanne, die für ihre Art bisher gemessen ist, und keine der
beiden ist damit ausgeschlossen. Die Statuszeile, die es entscheiden könnte,
führt nur noch einen der beiden.
Der Fall ist damit dieselbe Sackgasse wie #79, diesmal von Anfang an
protokolliert.

Daraus der Handgriff: **Bei Änderungen an Regeldateien nicht umschalten, ohne
den Lauf abzuwarten.** Auf #85 war genau dieser ready-Lauf derjenige, der den
Befund brachte — 15 Sekunden nachdem ein anderer Lauf denselben Commit
befundlos genannt hatte.

**Was dabei wie ein übergangener Fix aussieht, ist keiner.** Auf #85 schien der
Merge einen bereits gepushten Fix übersprungen zu haben: Befund 18:42:49, Merge
18:43:04, Fix `509894d`. Die Zeitstempel widerlegen das — der Fix-Commit trägt
**18:43:48**, also 44 Sekunden **nach** dem Merge. Weiter trägt das
Committer-Datum nicht: Ob die Änderung da schon fertig im Arbeitsverzeichnis
lag und nur noch nicht committed war, sagt es nicht, und über den
Push-Zeitpunkt sagt es gar nichts. Belegt ist allein, dass der Merge keinen
vorhandenen Commit übergehen konnte.

Das ist derselbe Fehlschluss wie in «Der Review ist da, der Merge geht
trotzdem durch» zu #59, und er ist auf demselben Repo ein zweites Mal
unterlaufen —
ausgerechnet im PR-Text von #86, der die Behebung trug. **Eine frühere Fassung
verwies hier auf «Fassungen, die nicht hielten»; dort ist er nie festgehalten
worden.** Der Verweis behauptete damit eine Korrektur, die es nicht gab, und
deckte zugleich zu, dass die #59-Stelle den Fehlschluss selbst beging und
unbemerkt trug. Beide Stellen sind jetzt auf die Existenzaussage eingeschränkt.
Der Handgriff: **Commit-Datum gegen `merged_at` halten, bevor man dem Merge
etwas zuschreibt** — und mehr als «der Commit existierte noch nicht» trägt es
nicht.

**Der «Abstand null» kam nach seiner Streichung zurück.** Auf `0bd7f78` als
Befund entfernt, auf `cff9ee5` beim Kürzen desselben Absatzes unbemerkt wieder
eingebaut und im Folge-Commit erneut gestrichen. Daraus ein Handgriff, der sonst
nirgends steht: **Wer eine Stelle strafft, prüft, ob die kürzere Fassung eine
Behauptung zurückholt, die ein Review schon entfernt hat.** Beim Kürzen sucht
man nach Wörtern, nicht nach Aussagen — und die Aussage ist das, was der Befund
getroffen hatte.

---

## 9. Fassungen, die nicht hielten

Der Abschnitt über die schwankenden Antworten stand vor seinem Merge
mehrfach falsch da. Jede Fassung scheiterte an derselben Sache: Sie erklärte
mehr, als sie gemessen hatte.

1. **«Der Auslöser feuert nicht, Zeit und Environment sind ausgeschlossen.»**
   Der Zeit-Ausschluss verglich einen manuellen Lauf mit einem automatischen
   vierzehn Stunden früher; der Environment-Ausschluss stützte sich auf einen
   Lauf, dem sieben Minuten später die Environment-Meldung folgte.
2. **«Der manuelle Weg trägt, wo der automatische scheitert.»** Vier Minuten
   später kam die Meldung auf einen Aufruf, der manuell ausgesehen hat.
3. **«Die Prüfung ist unstet, der Weg ist nicht die Variable.»** Beides war zu
   viel. Aus «beide Wege haben schon geliefert und schon versagt» folgt nur,
   dass keiner immer funktioniert.
4. Die vierte nennt keine Ursache mehr, sondern die Beobachtung und das, was
   sie entscheiden würde.

Zwei weitere Sätze sind später gefallen, beide aus demselben Grund:

- **«Der Merge tötet einen laufenden Job»** — widerlegt durch #60, siehe «Der
  manuelle Aufruf: was belegt ist».
- **«Die 👀 ist die einzige je beobachtete Reaktion»** — widerlegt durch #59
  und #60, siehe die Formen, in denen sich ein Lauf zeigt.

### Fassungen zur stillen Draft-Eröffnung

Am 29.8. in vier Review-Runden binnen sechzehn Minuten abgeräumt. Die ersten
drei wurden je von der nächsten Fassung ersetzt; die vierte nicht — sie wurde
gestrichen, und an ihrer Stelle steht seither keine Regel mehr. Dieselbe
Krankheit bei allen vieren: aus Stille auf Ursachen schliessen.

1. **«Der Vergleich steht bei durchgehend gesperrtem Kontingent.»** Für die
   Eröffnung um 10:03:12 war der Kontingentzustand nie beobachtet, und gerade
   die Stille kann eine Sperre nicht bestätigen.
2. **«Beide Kontingentzustände hätten etwas Sichtbares erzeugt, der Schluss
   gilt also unabhängig davon.»** Die Fallunterscheidung übersieht den dritten
   Ausgang — ein Trigger, der angenommen wird und unsichtbar scheitert — und
   setzt voraus, dass jeder Lauf einen Status-Kommentar hinterlässt. Beides
   unbelegt, und den dritten Ausgang hält «Der manuelle Aufruf: was belegt
   ist» für #51 längst fest.
3. **«Eine Eröffnung erzeugt nicht verlässlich eine sichtbare Antwort.»** Zu
   allgemein: Antwortet der Connector nach mehr als 317 Sekunden, sieht #65 im
   Messfenster genauso aus und kann trotzdem verlässlich später antworten.
   Belegt ist nur die Stille *innerhalb* des gemessenen Fensters.
4. **«‹Ein Draft löst nie etwas aus› ist widerlegt, durch genau einen Fall.»**
   Der zusammenfassende Absatz, der die drei Korrekturen überlebt hatte. Eine
   Widerlegung braucht einen kausal zugeordneten Fall; #64 gibt ihn nicht her
   (die Antwort kam vor dem Aufruf, die Ursache ist offen) und #65 auch nicht
   (Stille sagt nichts über das Auslösen). Er wurde nicht ersetzt, sondern
   gestrichen.

Eine fünfte Fassung gibt es nicht: An der Stelle steht jetzt die Sekundenzahl
und sonst nichts.

---

## 10. Zahlen, die eine Aufzählung wiederholen

Die Handlungsregel steht in `CLAUDE.md`. Hier die Fälle, an denen sie entstand:
am 29.8.2026 an dieser Datei, eine Review-Runde nach der anderen, und **jede
Korrektur erzeugte die nächste.**

| Die Zahl | Warum sie fiel |
|---|---|
| «sechs» im Text gegen «sieben» in der Einleitung | zwei Zählstellen für dasselbe Archiv |
| Überschrift «Drei Fassungen» | beim Beheben war ein vierter Eintrag dazugekommen |
| «Acht Fassungen» | ein Listenpunkt war die überlebende Fassung, keine gescheiterte |
| «vier Fehlschläge» über einer Tabelle mit acht Zeilen | Tabelle gewachsen, Prosa nicht |
| «Zwei Fehlschläge der Tabelle» | Nenner entfernt, Zähler stehen gelassen |
| «die Mehrzahl der Fälle oben» | im Abschnitt, der die Regel aufschrieb |

Am lehrreichsten ist «die Mehrzahl der Fälle oben»: Diese Zeile entstand beim
Aufräumen der anderen. Ich hatte drei absolute Zählungen entfernt und dabei eine
relative eingebaut — «Zahl» als Ziffer gelesen statt als Aussage über eine
Menge.

Die Überschrift «Drei Fassungen», die «vier Fehlschläge» und der Zähler «Zwei»
wurden alle dadurch falsch, dass ein Eintrag dazukam und ein Satz einen Absatz
weiter unbemerkt veraltete. Wer eine Aufzählung ergänzt, liest die Prosa daneben
mit, nicht nur die Liste.

**Was die Fälle nicht hergeben:** dass jede Ergänzung jede Zahl falsch macht.
Kommt zu einer Tabelle mit Fehlschlägen ein erfolgreicher Fall hinzu, bleibt die
Zahl der Fehlschläge richtig. Entscheidend ist, ob der Zuwachs die Aussage
trifft: Eine Ziffer fällt, sobald er in ihre Bezugsmenge gehört; eine relative
Angabe an einem Punkt, den nur das Verhältnis verrät. Deshalb
steht die Regel in `CLAUDE.md` als Prüfauftrag und nicht als Verbot von Zahlen.

**Der Kipppunkt ist die hartnäckigste Stelle des Abschnitts.** Fassung um
Fassung wollte angeben, *wann* eine relative Angabe fällt — «mit dem nächsten
Eintrag», «sobald die Bezugsmenge wächst», «mit dem ersten unpassenden» —, und
jede war mit einem Zahlenbeispiel zu widerlegen; die späteren entstanden beim
Beheben der jeweils vorigen. Auch die vorsichtige Umkehrung fiel: «nicht beim
ersten unpassenden Eintrag» ist falsch, sobald die Aufzählung klein ist — zwei
von drei werden zwei von vier, und die Mehrzahl ist weg. Die Fassung, die
hielt, gibt den Zeitpunkt gar nicht an. Wer eine Regel über Zahlen schreibt,
will sie präzisieren und präzisiert sie falsch.

**Der Abschnitt hat seine eigene Regel mehrfach verletzt, und nicht nur mit
Zahlen.** Eine relative Zählung («die Mehrzahl der Fälle oben»), ein Verweis auf
eine Abschnittsnummer statt auf einen Titel, und ein Verweis auf «die letzte
Zeile» einer Tabelle, die ausdrücklich fortgeschrieben werden soll. Nur die
Zählung ist eine Zahl, die beiden Verweise sind Positionen; die Regel dazu steht
in `CLAUDE.md`. Dass sie dort als Prüfauftrag steht und nicht als Vorhersage,
liegt an diesen Gegenbeispielen: Ein Abschnitt hinter dem verwiesenen lässt
dessen Nummer stehen, einer davor verschiebt sie; eine Zeile mitten in der
Tabelle lässt «die letzte Zeile» stehen, eine am Ende nicht. Ansehen kann man
es keinem von beiden.
