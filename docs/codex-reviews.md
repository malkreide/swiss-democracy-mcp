# Codex-Reviews: was beobachtet wurde

Beobachtungssammlung zum Codex-Review-Bot (`chatgpt-codex-connector[bot]`).
Die **Handlungsregeln** stehen in `CLAUDE.md`, Abschnitt «Wenn Codex gar nicht
erst hinsieht»; hier liegen die Belege dazu — Zeitstempel, Einzelfälle und die
Fassungen, die sich als falsch erwiesen haben.

Der Sinn der Trennung: `CLAUDE.md` wird beim Arbeitsbeginn gelesen und muss
kurz sein. Diese Datei wird gelesen, wenn jemand eine der Regeln anzweifelt,
fortschreiben will oder wissen muss, wie belastbar sie ist.

**Wer hier etwas ergänzt:** Eine Erklärung gehört erst hinein, wenn der
entscheidende Vergleich vorliegt. Acht Fassungen sind daran gescheitert,
mehr zu erklären als gemessen war — vier am ursprünglichen Abschnitt, vier an
der stillen Draft-Eröffnung; sie stehen unten als Mahnung.

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

Zwei Vorbehalte:

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
(Abschnitt 6).

**Was diese Messung nicht hergibt:** Sie beginnt erst *nach* dem Umschalten auf
ready und sagt deshalb nichts darüber, ob ein als Draft gestarteter PR seltener
zu früh zugeht. Warum es so schnell ging, ist ebenfalls nicht gemessen:
Nachlässigkeit, Bedienführung oder etwas Drittes sind von aussen nicht zu
unterscheiden. Belastbar ist allein, dass vor dem Merge zusätzlich umgeschaltet
werden muss.

### 4.2 Der Review ist da, und niemand sieht hin

Am 29.8. auf #59: Um 07:04:53 stand der P2-Befund am PR, mit Datei und Zeile.
Um 07:06:14 wurde gemergt — 81 Sekunden später, mit dem befundbehafteten
Commit als Head. Die Behebung war da noch nicht geschrieben; ihr Commit trägt
07:06:28. Der Defekt stand damit in `main`, und es brauchte den Nachzügler #60.

Der Unterschied zu 4.1 ist der Punkt: Dort ging der Prüfer verloren, hier hat
er geliefert und niemand hat hingesehen. Deshalb steht die Checkliste im
PR-Template auf «beantwortet oder behoben», nicht auf «Review gelaufen».

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
dem sichtbaren Ergebnis —, sieht das im Messfenster genauso aus. Abschnitt 5
hält für #51 fest, warum sich das von aussen nicht trennen lässt: «nichts kam
an» ist nicht «nichts wurde ausgelöst». Der Kontingentzustand während der
317 Sekunden ist ebenfalls nicht beobachtet; belegt sind Sperren um 10:00:34
und um 10:11:22, davor und danach.

**Was #65 hergibt, in einem Satz:** Auf eine Draft-Eröffnung kam binnen
317 Sekunden keine sichtbare Antwort. Nicht mehr — weder über das Auslösen noch
über spätere Antworten noch über das Kontingent. Drei frühere Fassungen dieses
Absatzes behaupteten jeweils mehr; sie stehen in Abschnitt 9.

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
Ursachen zu machen; Abschnitt 9 zählt sie. Die letzte behauptete noch, «ein Draft löst nie etwas aus» sei widerlegt —
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
passt aber zu der Zeile in Abschnitt 8, wonach im Draft-Zustand nach einer
Korrektur kein Lauf nachkommt. Eröffnung und Push sind hier verschiedene Dinge,
und nur nach der Eröffnung wurde etwas sichtbar. Was jeweils ausgelöst wurde,
sagt auch dieser Absatz nicht — aus demselben Grund wie oben.

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

Einmal gescheitert (#53 um 18:51:30, siehe 4.3). Nach einem Fehlschlag lohnt
der zweite Versuch.

**Auf einem Draft läuft er an** — #55 ist der Beleg. Dass umgekehrt die
automatischen Auslöser den ready-Zustand *brauchen*, stand hier lange
unwidersprochen daneben; seit dem 29.8. ist es fraglich (Abschnitt 4.3).

**Auf einem gemergten PR läuft er an** — #45 war seit 70 Minuten gemergt, #51
seit knapp 14 Stunden; beide bekamen ihren Review. Geprüft wird dann allerdings
der **Merge-Commit**, nicht der Branch-Stand: Der Aufruf auf dem gemergten #59
am 29.8. um 07:07:24 lieferte um 07:09:27 einen Review von `789e901`.

**Ein Lauf kann einen Merge überleben.** Auf #60 startete am 29.8. um 07:11:27
ein Lauf, um 07:11:53 wurde gemergt, und um 07:12:44 stand er auf «Completed».
Was zwei Fassungen lang als eigener Grund dastand — der Merge töte einen
laufenden Job — ist damit als allgemeine Regel widerlegt.

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

Danach vier Fehlschläge, alle mit derselben Meldung:

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

**Der Beginn ist auf 1 h 45 min 18 s eingegrenzt** — zwischen dem letzten
Erfolg um 07:27:07 und dem ersten Fehlschlag um 09:12:25. Das ist die engste
Eingrenzung in dieser Sammlung; beim Ausfall vom 21./22.8. war schon das
entsprechende Fenster 67 Minuten breit, und das Ende blieb ganz offen.

**Zur Dauer gibt sie so wenig her wie die erste.** Zwischen erstem und letztem
Fehlschlag liegen 58 min 57 s, dichter abgetastet als im August — acht Punkte
statt zwei, und die acht Auslöser sind voneinander unabhängig. Dichter heisst
trotzdem nicht lückenlos: Zwischen zwei Fehlschlägen kann sich das Fenster
geöffnet und durch den nächsten Auslöser wieder geschlossen haben. Was nach
10:11:22 geschah, steht hier nicht — bis zum Ende der Sitzung ging kein Lauf
mehr durch.

**Das Dashboard blieb zu.** `chatgpt.com/codex/cloud/settings/usage` beantwortet
einen Abruf ohne ChatGPT-Anmeldung mit HTTP 403. Welches Limit griff — rollendes
Fünf-Stunden-Fenster oder Wochenlimit —, ist deshalb auch für diese Episode
offen. Die Frage lässt sich ohne Anmeldung nicht am Dashboard klären, wohl aber
am Verhalten des Bots: Er sagt selbst, dass er nicht kann.

**Eine Sperre bremst die Auslöser nicht.** Zwei der vier Fehlschläge stammen von
Merges, die während der Sperre stattfanden. Warum diese beiden PRs gerade da
gemergt wurden, ist von aussen nicht zu sehen und steht deshalb nicht hier.
Festzuhalten ist nur, dass eine Sperre weitere Versuche nicht verhindert. Ob ein
abgewiesener Versuch selbst etwas kostet, ist nicht bekannt.

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

Zeigt das Dashboard freies Kontingent, während Reviews weiter scheitern, ist
das ein bekannter Fehler bei mehreren verbundenen Konten — dann den
GitHub-Connector in den Codex-Einstellungen trennen und neu verbinden.

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
42 aus Abschnitt 3 zählt Reviews.

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

---

## 9. Fassungen, die nicht hielten

Der Abschnitt über die schwankenden Antworten (4.3) stand vor seinem Merge
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

- **«Der Merge tötet einen laufenden Job»** — widerlegt durch #60 (siehe 5).
- **«Die 👀 ist die einzige je beobachtete Reaktion»** — widerlegt durch #59
  und #60 (siehe 1).

### Fassungen zur stillen Draft-Eröffnung (4.3)

Am 29.8. in vier Review-Runden binnen sechzehn Minuten abgeräumt, jede von der
nächsten. Dieselbe Krankheit wie oben: aus Stille auf Ursachen schliessen.

1. **«Der Vergleich steht bei durchgehend gesperrtem Kontingent.»** Für die
   Eröffnung um 10:03:12 war der Kontingentzustand nie beobachtet, und gerade
   die Stille kann eine Sperre nicht bestätigen.
2. **«Beide Kontingentzustände hätten etwas Sichtbares erzeugt, der Schluss
   gilt also unabhängig davon.»** Die Fallunterscheidung übersieht den dritten
   Ausgang — ein Trigger, der angenommen wird und unsichtbar scheitert — und
   setzt voraus, dass jeder Lauf einen Status-Kommentar hinterlässt. Beides
   unbelegt, und den dritten Ausgang hält Abschnitt 5 für #51 längst fest.
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
