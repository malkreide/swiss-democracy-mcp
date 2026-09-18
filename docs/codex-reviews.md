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

Eine dritte Gruppe steht daneben und gehört nicht zu den beiden: «Vier
Fassungen, die kein Review getroffen hat». Sie erklärten nicht zu viel, sie
rechneten falsch — und niemand hat es bemerkt, weil während ihrer Entstehung
kein Lauf mehr durchging.

Eine Gesamtzahl steht hier nicht. Am 29.8. wurde sie in drei aufeinander
folgenden Review-Runden dreimal korrigiert: «sechs» gegen «sieben» an zwei
Stellen, dann eine Überschrift mit «drei» über vier Einträgen, dann «acht»,
das die überlebende Fassung mitzählte. Jede Korrektur erzeugte die nächste.

---

## 1. Die sechs Formen, in denen sich ein Lauf zeigt

| Form | Wo | Bedeutet |
|---|---|---|
| «💡 Codex Review» | Review-**Objekt** (`get_reviews`) | Lauf mit Befund |
| «Codex Review: Didn't find any major issues.» | Issue-Kommentar **oder** Antwort im Review-Thread | Lauf ohne Befund |
| «You have reached your Codex usage limits for code reviews.» — auch ohne «for code reviews» | Issue-Kommentar **oder** Antwort im Review-Thread | Kontingent weg |
| «To use Codex here, create an environment for this repo.» | Issue-Kommentar | Environment-Meldung |
| Status-Kommentar «🔄 Running» / «✅ Completed» | Issue-Kommentar, **bearbeitet** | Lauf läuft / ist durch |
| gar nichts | — | nichts belegt |

Die ersten fünf Formen verlangen **drei** Abfragen, nicht zwei: `get_reviews`
für das Objekt, `get_comments` für die Issue-Kommentare — und
`get_review_comments` für die Antworten in Review-Threads. Wer eine weglässt,
übersieht einen Teil; genau so ist die Limit-Meldung zuerst durchgerutscht.

**Die dritte kam am 18.9. dazu.** Auf #98 stand die Kontingent-Meldung um
06:40:01 als Antwort in einem Review-Thread, also nur über
`get_review_comments` zu sehen; erst der *nächste* Aufruf bekam sie um 06:41:11
als Issue-Kommentar. Die beiden gehören verschiedenen Aufrufen, und der Wortlaut
unterscheidet sich: Die Thread-Fassung nennt «for code reviews», die
Issue-Fassung an dieser Stelle nicht. Wer in einem solchen Fenster nur die zwei
bisherigen Abfragen fährt, sieht gar nichts und hält den Head für ungeprüft aus
unbekanntem Grund — statt zu wissen, dass eine Sperre steht.

**Nicht nur die Ausfallmeldung nimmt diese Form an.** Am 18.9. um 09:58:29 kam
auf #103 die *Befundlos*-Meldung als Thread-Antwort, und `get_comments` kannte
sie nicht. Das trifft härter als der erste Fall: Die Befundlos-Meldung ist einer
der beiden Belege dafür, dass überhaupt geprüft wurde. Wer sie übersieht, hält
einen erfolgreichen Lauf für einen stillen.

Beide Male war der Aufruf selbst eine Thread-Antwort. Ob die Form dem Auslöser
folgt, ist damit nicht belegt, sondern naheliegend — und ob die Environment-
Meldung ebenso kann, ist gar nicht beobachtet.

**Zwei weitere Fälle am selben Tag.** Auf #108 kamen zwei Befundlos-Meldungen
um 11:01:23 und 11:09:16 als Thread-Antworten, und beide Aufrufe waren selbst
Thread-Antworten.

**Die Gegenprobe in der anderen Richtung ist längst gemessen** — in derselben
Sitzung auf #98, die den ersten Fall lieferte: Um 06:40:59 ging dort ein
*Issue-Kommentar* hinaus, und die Kontingent-Meldung kam zwölf Sekunden später
als *Issue-Kommentar*. Damit ist die Vermutung an beiden Formen geprüft statt
nur an einer. Die Tabelle führt jeden Fall, für den Auslöser **und**
Zustellweg festgehalten sind:

| Auslöser (UTC) | Form des Auslösers | Form der Meldung |
|---|---|---|
| #98, 06:39:50 | Thread-Antwort | Thread-Antwort (06:40:01) |
| #98, 06:40:59 | Issue-Kommentar | Issue-Kommentar (06:41:11) |
| #103 | Thread-Antwort | Thread-Antwort (09:58:29) |
| #108, 10:58:56 | Thread-Antwort | Thread-Antwort (11:01:23) |
| #108, 11:06:13 | Thread-Antwort | Thread-Antwort (11:09:16) |
| #111, 13:08:50 | Thread-Antwort | Thread-Antwort (13:10:14) |
| #112, 13:19:45 | Thread-Antwort | Thread-Antwort (13:19:55) |
| #112, ≈13:45:14 | **Umschalten auf ready** | **Issue-Kommentar (13:45:17)** |
| #112, 13:47:01 | Issue-Kommentar | Issue-Kommentar (13:47:10) |
| #113, 13:50:56 | Issue-Kommentar | Issue-Kommentar (13:51:08) |
| #113, ≈13:51:46 | **Umschalten auf ready** | **Issue-Kommentar (13:51:48)** |

**Die beiden Zeilen mit «Umschalten auf ready» sagen etwas, das die übrigen
nicht hergeben.** Das Umschalten ist gar kein Kommentar — es gibt keinen
Thread, in dem geantwortet werden könnte. Beide Male landete die Meldung unter
den Issue-Kommentaren. Damit liest sich die Beobachtung schärfer als «die Form
folgt dem Auslöser»: **Der Issue-Kommentar ist der Normalfall, und die
Thread-Antwort ist das, was ein Aufruf aus einem Thread heraus bekommt.**

**Ob die zweite Messung die erste stützt, ist offen.** Wenn ein Auslöser ohne
Thread gar nichts anderes bekommen *kann*, beschreiben beide Zeilen dieselbe
Mechanik und nicht zwei unabhängige Beobachtungen — dann ist der Satz oben
eine Beschreibung des Zustellwegs und keine Vermutung über ihn. Entschieden
ist das nicht; beide Male war zudem eine Kontingent-Absage der Inhalt, nie ein
Befund oder eine Befundlos-Meldung.

Die Auslösezeiten dieser beiden Zeilen sind die einzigen in der Tabelle, die
nicht aus der Primärquelle stammen: Das Umschalten trägt in der API keinen
Zeitstempel am PR, die ≈-Werte kommen aus den Webhook-Ereignissen. Die
Meldungen daneben sind mit 13:45:17 und 13:51:48 belegt; alle übrigen Zeiten
sind `created_at`-Werte der Kommentare.

Belegt ist die Regel damit immer noch nicht: Alle Zeilen stammen aus diesem
Repo, für die Environment-Meldung ist die Form gar nicht beobachtet, und ein
Fall, der ihr widerspricht — eine Thread-Antwort auf einen Issue-Kommentar oder
umgekehrt —, ist bisher nicht vorgekommen, aber auch nicht gezielt gesucht
worden. Zwei weitere Aufrufe jener Sitzung auf #98 (06:44:08 und 07:32:49,
beide Issue-Kommentare) bekamen ebenfalls die Kontingent-Meldung — wo sie
landete, ist nicht festgehalten.

Für die Praxis ändert das nichts — die dritte Abfrage ist ohnehin zu fahren.
Es verschiebt nur die Erwartung: Wer aus einem Thread heraus anfordert, sucht
die Antwort zuerst dort; wer gar nicht kommentiert hat, sucht sie unter den
Issue-Kommentaren.

### Der Schlusssatz der Befundlos-Meldung wechselt

Beobachtet: «Swish!», «Delightful!», «Keep it up!», «More of your lovely PRs
please.», «Keep them coming!», «Hooray!», «Breezy!» — und am 29.8. stand dort
statt eines Satzes bloss ein 🚀. Stabil ist nur der Satz davor.

### Der Status-Kommentar (seit 29.8.)

Kenntlich am HTML-Marker `<!-- codex-pull-request-review-summary -->`. Codex
legt ihn zu Beginn eines Laufs an und **aktualisiert ihn an Ort und Stelle**
von «🔄 Running» auf «✅ Completed» — kein zweiter Kommentar, sondern ein
`issue_comment.edited`. Wer nur auf neue Kommentare achtet, sieht diesen
Wechsel nicht. **Welcher** Lauf damit endete, ist allerdings eine eigene Frage
— «Der manuelle Aufruf: was belegt ist» hält fest, warum die Zeile das nicht
beantwortet.

Seine Tabelle nennt als Einzige **beides**: einen Commit *und* den Auslöser
(«Manual request», «Draft marked ready»). Die Befundlos-Meldung und das
Review-Objekt nennen nur den Commit — dafür den, den der Lauf geprüft hat. Der
Wert in der Statuszeile muss das nicht sein; der Vorbehalt «Der Commit in der
Statuszeile ist nicht unbedingt der geprüfte» hält den Fall fest.

Vorbehalte:

- Kein Beleg für eine abgeschlossene Prüfung — auf «Running» steht er auch
  dann, wenn nie ein Ergebnis folgt.
- Kein Protokoll, sondern **eine einzige Zeile mit dem letzten Lauf**. Ein
  neuer Auslöser überschreibt den vorigen spurlos: Am 29.8. verdrängte auf #61
  der ready-Lauf um 07:19:51 den manuellen von 07:18:38; dessen Ausgang steht
  seither nirgends mehr. Wer zwei Läufe auseinanderhalten will, braucht ihre
  Ergebnis-Kommentare — die bleiben einzeln stehen.
- **«✅ Completed» belegt kein zugestelltes Ergebnis.** Auf #60, #79, #88, #89
  und #93 stand die Zeile auf «Completed», ohne dass ein Review-Objekt oder
  eine Befundlos-Meldung ankam; sie stehen unter «Der manuelle Aufruf: was
  belegt ist». #92 kommt hinzu und steht unter «Der Lauf läuft noch, der Merge
  geht durch» — dort, weil es dabei um den Merge-Zeitpunkt geht und nicht
  darum, was ein Aufruf hergibt. Ob diese Läufe nichts fanden oder ihr Ergebnis
  nach dem Merge nicht mehr zugestellt wurde, ist von aussen nicht zu
  unterscheiden. Wer aus «Completed» auf «nichts gefunden» schliesst, erfindet
  ein Urteil.
- **Der Commit in der Statuszeile ist nicht unbedingt der geprüfte.** Am 18.9.
  auf dem gemergten #93 nannte die Zeile `639fce5`, den Branch-Stand, während
  das Review-Objekt `7755c900` trägt, den Merge-Commit.

  Dass beide zum **selben** Lauf gehören, hängt an zwei Angaben: Die Zeile
  trug zu diesem Zeitpunkt «Manual request» und «Completed 05:28:49», der
  ready-Lauf davor dagegen «Draft marked ready» und «Completed 05:19:50»; das
  Review-Objekt trägt 05:28:46, drei Sekunden vor der Zeile. Ohne den
  Auslöser-Namen wäre die Zuordnung nicht zu halten — die Zeile wird an Ort
  und Stelle überschrieben und führt immer nur den letzten Lauf. Ein
  Codex-Review auf #94 hat den Vergleich denn auch zunächst zwei
  verschiedenen Läufen zugeordnet.

  Der Name ist dabei notwendig und nicht hinreichend: Er trennt den manuellen
  Lauf vom ready-Lauf, aber nicht zwei manuelle voneinander. Auf #95 trugen
  beide «Manual request» — was das für die Zuordnung heisst, steht unter «Der
  manuelle Aufruf: was belegt ist».

  **Am 18.9. gab die Commit-Spalte gar nichts mehr her.** Auf #108 sassen zwei
  Läufe auf demselben `e3141f6`, und die Zeile trug sie nacheinander:

  | Zeit (UTC) | Status | Commit | Auslöser |
  |---|---|---|---|
  | 10:59:08 | 🔄 Running | `e3141f6` | Manual request |
  | 11:01:25 | ✅ Completed | `e3141f6` | Manual request |
  | 11:01:49 | 🔄 Running | `e3141f6` | **Draft marked ready** |
  | 11:04:56 | ✅ Completed | `e3141f6` | Draft marked ready |

  Im Fall auf dem gemergten #93 trennte der Auslöser-Name zwei Läufe, deren
  Commits sich ohnehin unterschieden. Hier ist er das Einzige, was sie trennt.

  Zur Sackgasse von #79 und #87 wurde es trotzdem nicht — und der Unterschied
  liegt nicht am Commit: Auf #87 sassen beide Läufe ebenfalls auf einem und
  demselben, und dort blieb die Zuordnung offen. Er liegt daran, dass hier
  **jeder Lauf sein eigenes Ergebnis zustellte**: eine Befundlos-Meldung um
  11:01:23, ein Review-Objekt um 11:04:52. Für den manuellen Lauf auf #87 ist
  überhaupt kein Ausgang festgehalten, weder ein Ergebnis noch ein
  «Completed» — deshalb liess sich der dortige Befund keinem der beiden
  zuordnen.

  **Was daraus nicht folgt: dass die beiden Läufe auf #87 gleichzeitig
  liefen.** Dass der manuelle beim Start des ready-Laufs noch lief, ist nicht
  belegt; er kann ebenso geendet haben, ohne dass seine «Completed»-Fassung
  konserviert wurde — die Zeile wird überschrieben, und «Completed ohne
  zugestelltes Ergebnis» ist in dieser Aufzählung für mehrere PRs belegt.
  Belegt ist dort allein, dass sich eine Trennung nicht zeigen lässt.

  Der Fall führt damit nur vor, was der Abschnitt ohnehin schliesst: Die
  Zuordnung hängt an den Ergebnissen, nicht an der Statuszeile.

  Wer wissen muss, was geprüft wurde, liest deshalb das Ergebnis, nicht die
  Statuszeile.

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

**Am 18.9. auf #108 derselbe Ablauf noch einmal**, an einer Regeldatei:

| Zeit | Commit | Auslöser | Urteil |
|---|---|---|---|
| 11:01:23 | `e3141f6` | `@codex review` | befundlos |
| 11:04:52 | `e3141f6` | Draft → ready | **P2, zutreffend** |

Derselbe Ausgang: Der Befund kam aus dem Lauf, den niemand mit Absicht
angestossen hat. Mit dem Fall auf #85 unter «Zum Verfahren für Doku-PRs» sind
das drei Paare, in denen ein Lauf einen Commit befundlos nannte und ein
zweiter auf **demselben** Commit einen zutreffenden Befund lieferte. Die
Abstände waren 15 Sekunden, 287 und 209 — drei Messwerte, mehr nicht. Ob der
Abstand etwas ausmacht, ist daran nicht zu prüfen: Alle drei gingen gleich
aus, ein Gegenfall fehlt.

**Neu ist der dritte Fall in einem Punkt: Gemergt wurde erst die behobene
Fassung.** In den beiden früheren lag der Befund rechtzeitig vor und wurde
überfahren — auf #59 um 07:04:53, 81 Sekunden vor dem Merge; auf #85 um
18:42:49, 15 Sekunden davor. Beide brauchten einen Folge-PR. Am 18.9. war der
Lauf abgewartet, die Behebung ging in denselben PR, und gemergt wurde dieser
dann auch: `16fdd89` über den Merge-Commit `2c60fb6`. Der fehlerhafte Stand
kam gar nicht erst nach `main`.

Der Unterschied liegt damit nicht am Prüfer, sondern am Umgang mit seinem
Ergebnis. Es ist derselbe Befund wie unter «Der Review ist da, der Merge geht
trotzdem durch», von der anderen Seite gelesen: Dort kostet die Eile den
Befund, hier hat das Abwarten ihn eingebracht.

---

## 4. Wege, den Prüfer zu verlieren

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

**Am 18.9. auf #110 dasselbe.** Der Lauf lieferte um 12:54:18 vier P2-Befunde
zu `e257321`; gemergt wurde um 12:56:22, **124 Sekunden später**, auf
demselben Commit. Die Behebung war um 12:58:00 committet — 98 Sekunden nach
dem Merge — und brauchte den Nachzügler #111. Der Absatz darüber gilt hier
genauso: Belegt ist der Zustand beim Merge, nicht, ob jemand hingesehen hat.

**Neu ist, was derselbe Tag danebenlegt.** Elf Minuten nach dem Merge von #110
wiederholte sich die Lage auf #111 — dieselbe Datei, derselbe Prüfer, wieder
ein Befund vor dem Merge — und ging anders aus:

| | Befund | Merge | Fenster | Behebung committet |
|---|---|---|---|---|
| #110 | 12:54:18 | 12:56:22 | 124 s | 12:58:00, also 222 s nach dem Befund |
| #111 | 13:07:19 | 13:09:14 | 115 s | 13:08:20, also 61 s nach dem Befund |

Die Fenster sind fast gleich lang; verschieden ist, was die Behebung brauchte.
**Woran das lag, ist nicht gemessen** — naheliegend ist der Prüfaufwand (vier
Befunde gegen zwei, und beim zweiten Mal war die Stelle schon bearbeitet),
belegt ist es nicht.

Was die zwei Zeilen trotzdem hergeben: **Bei fast gleich langem Fenster war
die Behebung einmal rechtzeitig fertig und einmal nicht** — 61 gegen 222
Sekunden, also mehr als das Dreifache. Der Abstand zwischen Befund und Merge
sagt für sich genommen nichts darüber, ob eine Behebung hineinpasst; das hängt
daran, wie lange sie dauert, und diese Dauer schwankte hier stark. Woran sie
hing, ist nicht gemessen.

Für die Praxis folgt daraus genau eines, und es ist negativ: **Auf «schnell
reagieren» lässt sich nicht bauen, weil die benötigte Zeit vorher nicht
bekannt ist.** Ein Ersatz für «das Ergebnis abwarten» ist es damit nicht.

Was sie **nicht** hergeben: eine Dauer des Fensters. Zwei Werte sind keine
Spanne, und beide hängen daran, wann jemand auf «Merge» drückt — das ist keine
Eigenschaft des Prüfers, sondern eine des Vorgehens.

**Eine Beobachtung fällt dabei ab, ohne Empfehlung.** Meldet ein Push auf einen
Branch, den es vorher gab, `* [new branch]`, dann fehlte der Ziel-Ref im
Augenblick des Pushes — er ist zwischendurch gelöscht worden. Mehr sagt die
Zeile nicht: Ein Merge mit automatischer Branch-Löschung erzeugt sie, eine
Löschung von Hand ebenso, andere Automatisierung auch. Auf #110 war sie die
erste Spur davon, dass der PR längst zu war und die Behebung an einem Branch
ohne offenen PR hing — bemerkt wurde es aber erst, als der PR-Zustand
abgefragt wurde. **Wer aus der Zeile auf einen Merge schliesst, rät; wer sie
zum Anlass nimmt nachzusehen, verliert nichts.**

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

**Ein dritter Draft am 18.9. — und diesmal trennt der Wortlaut.** #115 wurde
als Draft eröffnet; um 13:58:10 stand eine Kontingent-Meldung da, neun Sekunden
vor dem ersten `@codex review` (IDs `5731051064` vor `5731052982`, dieselbe
monotone Ordnung wie auf #64). Um 13:58:31 kam die Antwort auf diesen Aufruf.
Die beiden lauten **verschieden**:

| Zeit (UTC) | Auslöser | Wortlaut |
|---|---|---|
| 13:58:10 | Eröffnung als Draft | «You have reached your Codex usage limits.» |
| 13:58:31 | `@codex review` | «…usage limits **for code reviews**.» |

Derselbe PR, dasselbe Konto, 21 Sekunden auseinander. Wie sich die kurze und
die lange Fassung über jenen Nachmittag verteilen, führt die Tabelle unter
«Die Nachmittagssperre desselben Tages»; sie ist die Quelle, hier steht nur
der Einzelfall.

**Was das hergibt:** Die Absage nach der Eröffnung war ihrem eigenen Wortlaut
nach *keine* Absage eines Code-Reviews. Die Eröffnung erreicht damit einen
anderen Pfad als das Umschalten — der erste Anhaltspunkt dafür in dieser
Sammlung, und er stammt aus dem Text der Meldung, nicht aus einer Zeitreihe.

**Was es nicht hergibt**, und das bleibt die offene Frage dieses Abschnitts:
dass eine Eröffnung einen *Lauf* auslöst. Sie löst etwas aus, das bei
erschöpftem Kontingent eine Meldung erzeugt; was daraus bei freiem Kontingent
würde, ist weiterhin ungemessen — und genau das verlangt der Absatz oben.

**Sechs Minuten später dasselbe, und ohne die Schwäche des ersten Falls.** #117
wurde um 14:08 als Draft eröffnet; um 14:08:10 stand die Meldung da, wieder
**ohne** «for code reviews». Auf #115 folgte neun Sekunden später ein Aufruf,
und die Zuordnung hing an der Reihenfolge der Kommentar-IDs. Auf #117 gab es
keinen Aufruf: **Die Meldung war der einzige Kommentar auf dem PR.** Ein
konkurrierender Auslöser existiert hier nicht.

Damit sind es zwei Eröffnungen mit der kurzen Fassung. Der dritte Fall der
kurzen Fassung gehört nicht hierher — er hing an einem Kommentar, der die
Zeichenfolge zitierte, und steht bei der Nachmittagssperre.

Die Zuordnung der Meldung zur Eröffnung bleibt trotzdem ein Schluss aus der
Reihenfolge, nicht aus einem Feld: Die Meldung nennt ihren Auslöser nicht, und
die Statuszeile, die als Einzige eine Auslöser-Spalte führt, entsteht bei einer
Absage gar nicht. Auf #117 ist der Schluss nur deshalb stärker, weil kein
anderer Kandidat im Zeitraum liegt.

Drei der vier beobachteten Eröffnungen haben eine Meldung erzeugt (#64, #115,
#117), eine nicht (#65). Auch das ist keine Regel — und die drei liegen alle in
Sperrzeiten, bei freiem Kontingent ist keine einzige gemessen.

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

**Ein zweiter Fall am 18.9., sauberer als der erste.** Auf #98 ging um 06:40:59
ein Kommentar hinaus, der die Zeichenfolge nur in Backticks führte, in einem
Satz *über* das Auslösen. Zwölf Sekunden später stand die Kontingent-Meldung da.
Kein Push, kein Zustandswechsel, kein anderer Kandidat im Text — das ist der
Unterschied zum ersten Fall, wo ein Push siebzig Sekunden vorher lag. Der
Backtick schützt also nicht.

**Und trotzdem bleibt es «vermutlich».** Was fehlt, ist die Gegenprobe: In
dieser Sitzung trug *jeder* Kommentar an den Connector entweder einen echten
Aufruf oder ein Zitat davon. Ein Kommentar ohne beides wurde nie abgesetzt, und
damit ist nie gemessen worden, ob der Connector auf einen beliebigen Kommentar
schweigt. Zwei Fälle mit demselben blinden Fleck sind nicht mehr als ein Fall
mit zwei Zeitstempeln. Für die Praxis genügt es — die Zeichenfolge gehört nicht
in einen Kommentar, auch nicht zitiert —, als Beleg genügt es nicht.

### 4.4 Der Lauf läuft noch, der Merge geht durch

Am 18.9. auf #92, alles auf demselben Commit `494a61f`:

| Zeit (UTC) | Ereignis |
|---|---|
| 04:08:40 | Befundlos-Meldung des **manuellen** Laufs |
| vor 04:09:03 | Draft → ready |
| 04:09:03 | ready-Lauf startet («Draft marked ready») |
| 04:09:20 | **gemergt** |
| 04:10:15 | ready-Lauf steht auf «Completed» — **ohne zugestelltes Ergebnis** |

Zwischen Start und Merge lagen **17 Sekunden**. Kein Review-Objekt, keine
zweite Befundlos-Meldung: `get_reviews` leer, unter den Kommentaren nichts
Neues.

**Der Ausgang dieses Laufs ist unbekannt, nicht «befundlos».** Ob er nichts
fand oder ob sein Ergebnis nach dem Schliessen nicht mehr zugestellt wurde, ist
von aussen nicht zu unterscheiden — die Fälle #60, #79, #88 und #89 unter «Der
manuelle Aufruf: was belegt ist» halten genau diese Grenze fest, und #80 zeigt,
dass ein Ergebnis einen Merge durchaus überholen kann. #92 ist ein weiterer
Fall dieser Reihe und kein neuer Befund. Eine frühere Fassung dieses Abschnitts
trug «endet, ohne Befund» in die Tabelle und schloss daraus, es sei «gut
ausgegangen» — beides war ein erfundenes Urteil.

Der Platz hier statt dort ist trotzdem gewollt: Die Belege gehören zu dem, was
ein Aufruf hergibt, die Lehre zu den Wegen, den Prüfer zu verlieren. 4.1 misst
allein den Abstand zwischen Umschalten und Merge und nennt keinen
Startzeitpunkt — ob dort ein Lauf schon lief, ist nicht belegt, und der
Abschnitt sagt selbst, dass er das Warum nicht hergibt. In 4.2 lag der Befund
vor und wurde übergangen. Hier ist der Start dagegen belegt: Der Status stand
beim Merge auf «🔄 Running», und das Urteil dieses Laufs ist bis heute nicht zu
haben.

**Was den gemergten Stand trägt, ist der andere Lauf.** Derselbe Commit hatte
40 Sekunden vor dem Merge eine zugestellte Befundlos-Meldung des manuellen
Laufs. Ungeprüft ging er also nicht nach `main` — geprüft ist er durch den
Lauf, den jemand abgewartet hat, nicht durch den, der lief.

**Was der Fall nicht hergibt:** ob der Mergende vom laufenden Review wusste.
Von aussen ist der Zustand messbar, nicht die Aufmerksamkeit — dieselbe Grenze
wie in 4.2. Ebenso wenig ist belegt, welcher der beiden Läufe die 👍 am PR
gesetzt hat: Die Reaktionen wurden erst **nach** dem zweiten Lauf gelesen, und
die Sammlung führt sie ohnehin als Nicht-Beleg.

**Ein zweiter Fall am selben Tag, diesmal ohne Rückhalt.** Auf #101, alles auf
Commit `718689d`:

| Zeit (UTC) | Ereignis |
|---|---|
| 10:01:43 | **manueller** Lauf startet |
| 10:02:32 | Draft → ready |
| 10:02:38 | **gemergt** |
| 10:03:56 | Statuszeile auf «Completed», für den **ready**-Lauf |

Zwischen Start und Merge lagen **55 Sekunden**, bei einem Vorlauf, der auf
demselben PR kurz zuvor 2 min 48 s betragen hatte. Danach alle drei Abfragen:
kein Review-Objekt zu diesem Commit, keine Befundlos-Meldung, nichts in den
Review-Threads. **Zugestellt wurde also nichts** — was die beiden Läufe getan
haben, sagt das nicht. Einen zuschreibbaren Abschluss hat nur der ready-Lauf;
der manuelle war aus der Statuszeile verdrängt, bevor sein Ende dort zu sehen
war, und sein Ausgang bleibt offen.

**Der Unterschied zu #92 ist der Rückhalt.** Dort trug eine zugestellte
Befundlos-Meldung desselben Commits den gemergten Stand, und der Abschnitt
oben hält fest: «Ungeprüft ging er also nicht nach `main`.» Hier gibt es keine
solche Meldung. Der vorige Commit `de3df06` hatte einen Befund, `718689d` ist
dessen Korrektur — und für die Korrektur ist nichts zugestellt worden. Die
Reihe hat damit ihren ersten Fall, in dem der gemergte Stand ohne Ergebnis
blieb.

Wer nur auf die Statuszeile sieht, hält ihn trotzdem für geprüft: Sie stand
auf «✅ Completed».

**Der Handgriff daraus ist nicht «schneller sein».** Auf #76 fielen Befund und
Merge in dieselbe gemessene Sekunde; auf eine Reaktionszeit ist nicht zu bauen.

**Er ist aber auch nicht «einer reicht».** Die erste Fassung dieses Abschnitts
schloss, ein abgewarteter Lauf mache den zweiten, der beim Merge noch läuft, zu
«einer Zugabe und keinem Risiko». Das widerspricht «Ein Ergebnis sagt etwas
über den Lauf, nicht über den Text»: Dort urteilten drei Läufe über denselben
Defekt zweimal befundlos und einmal zutreffend P2 — gefunden hat ihn der Lauf,
den niemand mit Absicht angestossen hat. Ein befundloser Erstlauf sagt über den
Ausgang des Zweitlaufs nichts.

Es bleiben zwei Haltungen, und die Wahl gehört benannt:

- **Jeden angestossenen Lauf abwarten.** Dann ist der gemergte Stand so weit
  geprüft, wie diese Werkzeuge es hergeben.
- **Den offenen Ausgang wissentlich in Kauf nehmen.** Dann aber nicht darauf
  warten, dass er noch eintrifft — auf einem geschlossenen PR kann er
  ausbleiben. Wer es wissen muss, ruft den Review auf dem gemergten PR neu auf;
  er läuft dort an und prüft dann den Merge-Commit.

Was nicht geht, ist das Zweite zu tun und das Erste zu behaupten.

Die Fassungen dieses Abschnitts, die an Codex-Reviews auf #93 gescheitert sind
— dem PR, der ihn einführt —, stehen in dessen Commit-Historie: der Fehlschluss
«kein Risiko», das erfundene Urteil «ohne Befund», die unbelegte Abgrenzung zu
4.1. Eine Zahl steht hier nicht: Sie war schon einmal falsch, weil die dritte
beim Zählen noch nicht geschrieben war.

---

## 5. Der manuelle Aufruf: was belegt ist

Geliefert hat er in dieser Spanne:

| PR | Vorlauf |
|---|---|
| #55 (Draft!) | 2 min 14 s |
| #45 | 2 min 31 s |
| #51 | 2 min 57 s |
| #53 | 3 min 1 s |
| #93 (gemergt!) | 3 min 25 s |
| #95, erster Aufruf | 2 min 34 s |
| #95, zweiter Aufruf (gemergt!) | 2 min 16 s |
| #109, erster Aufruf (Draft!) | 1 min 49 s |
| #109, zweiter Aufruf (gemergt!) | 1 min 22 s |

**Die Spanne ist keine Zusage.** Sie reicht von 1 min 22 s bis 3 min 25 s; wer
bei drei Minuten aufhört nachzusehen, verpasst den längsten gemessenen Lauf.
Eine frühere Fassung nannte die Werte «erstaunlich gleichmässig» und CLAUDE.md
sprach von «zwei bis drei Minuten» — beides stammte aus der Zeit, als die
Tabelle vier Zeilen hatte.

**Am 18.9.2026 ist sie nach unten gewandert.** Beide Läufe auf #109 blieben
unter dem bisherigen Kleinstwert von 2 min 14 s, der eine auf einem Draft, der
andere auf dem gemergten PR. CLAUDE.md nannte zu diesem Zeitpunkt «zwischen
2 min 14 s und 3 min 25 s» — die zweite dortige Fassung, die eine Messung
überholt hat, nach «zwei bis drei Minuten» die erste. Deshalb steht dort
jetzt keine Spanne mehr, sondern der Verweis hierher: Die Tabelle ist die
Quelle, und eine Kopie in einer Regeldatei ist mit jedem Eintrag erneut fällig.

**Eine verlässliche Endmarke gibt es nicht.** Die Uhr taugt nicht dafür, und
die Statuszeile auch nicht. Eine frühere Fassung hat sie dafür ausgegeben,
«solange kein weiterer Auslöser dazwischenkommt» — die Bedingung greift zu
kurz, weil sie nur nach vorn schaut. Die Zeile springt zwar von «🔄 Running»
auf «✅ Completed», führt dabei aber immer nur den letzten Lauf, den der
Connector geschrieben hat, und das muss nicht der eigene sein: nicht, wenn ein
späterer ihn überschreibt — auf #94 verdrängte der ready-Lauf um 05:51:36 die
manuelle Runde von 05:50:54, bevor für diese überhaupt ein «Completed»
feststand, und ihr Ausgang ist seither offen —, und nicht, wenn ein früherer
noch dasteht. Ein «✅ Completed» unter dem eigenen Auslöser-Namen kann deshalb
einem fremden Lauf gehören.

**Der Auslöser-Name schliesst aus, er weist nicht zu.** Steht dort ein anderer
Name als der eigene, gehört die Zeile einem anderen Lauf und sagt über den
eigenen nichts. **Welchem, sagt sie nicht.** Es kann ein späterer sein, der die
eigene Zeile überschrieben hat — auf #79 hat ein ready-Lauf den manuellen so
verdrängt. Es kann ebenso gut ein früherer sein, der noch dasteht, weil der
eigene Lauf noch gar nicht angefangen hat: Auf #98 lagen zwischen dem Aufruf um
06:27:19 und dem Start um 06:27:33 vierzehn Sekunden. Wer aus dem fremden Namen
«meiner ist überholt» liest, hat sich eine Reihenfolge erfunden, die die Zeile
nicht hergibt.

Steht dort derselbe Name, ist damit nichts gewonnen: Zwei manuelle Aufrufe
hintereinander tragen beide «Manual request», und der zweite überschreibt den
ersten, ohne dass die Prüfung auf den Namen anschlägt. Auf #95 lief der erste
am 18.9. um 05:59:23, der zweite — nach dem Merge — um 06:15:06;
die Zeile führte um 06:17:25 «✅ Completed» unter «Manual request» und meinte
den zweiten.

Die Commit-Spalte trennt die beiden erst recht nicht: Sie stand zu diesem
Zeitpunkt auf `af463f8`, dem Branch-Stand — also ausgerechnet auf dem Commit,
den der **erste** Lauf geprüft hatte, während der zweite den Merge-Commit
`1879444` prüfte. Wer die Zeile dem eigenen Lauf zuschreiben wollte, hätte
beide Spalten für sich gehabt und trotzdem den falschen Lauf vor sich.

Zuzuweisen wäre die Zeile nur, wenn auszuschliessen wäre, dass sie einem
anderen Lauf gehört — einem späteren, der sie überschrieben hat, oder einem
früheren, der noch steht. Ein sichtbarer Auslöser lässt sich aus den
Kommentaren lesen; ein unsichtbar angestossener Lauf grundsätzlich nicht —
daran ist auf #93 das Entscheidungsverfahren gescheitert. Die Zeile taugt
deshalb zum Ausschliessen und nicht zum Zuweisen — dieselbe Bedingung, die die
Arbeitsanweisung in `CLAUDE.md` nennt.

**Was bleibt, ist das zugestellte Ergebnis.** Es trägt den geprüften Commit und
steht als eigener Eintrag, den kein späterer Lauf überschreibt. Bleibt es aus,
ist das kein Urteil, sondern ein offener Ausgang — der Vorbehalt «✅ Completed
belegt kein zugestelltes Ergebnis» hält genau das fest. Wer wartet, wartet
folglich auf das Ergebnis und nicht auf die Zeile.

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

**Auch aus einer Antwort in einem Review-Thread läuft er an**, nicht nur aus
einem gewöhnlichen Kommentar. Auf #98 ging der Aufruf am 18.9. um 06:31:40 als
Antwort unter einem Codex-Befund hinaus; elf Sekunden später stand der Lauf auf
«Running». Wer einen Befund beantwortet und im selben Zug neu anfordern will,
braucht dafür also keinen zweiten Kommentar — und wer bloss antworten will,
muss die Zeichenfolge meiden.

Belegt ist das mit **einem** Lauf. Ein zweiter Aufruf derselben Form, um
06:39:50, traf schon die Kontingent-Sperre; er zeigt, dass die Form einen
Versuch anstösst, aber keinen zweiten Startzeitpunkt.

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

**Und gleich noch einmal auf #89,** dem PR, der den #88-Fall eintrug. Sein
ready-Auslöser um 05:11:16 startete einen Lauf, gemergt wurde 05:11:19, und um
05:12:27 stand er auf «Completed» — 68 Sekunden nach dem Merge. Wieder kam
nichts an: `get_reviews` leer, und die einzige Befundlos-Meldung trägt 04:55:50
und gehört zum manuellen Aufruf davor. Auch hier stand kein zweiter Lauf
daneben.

Die Laufzeit ist diesmal **nicht** zu haben: Die Statuszeile zeigt nur noch
«Completed», ihre «Running»-Fassung ist überschrieben, und kein Ereignis hat
sie festgehalten. Belegt sind Auslöser und Ende, nicht der Start — dass für
#88 eine Dauer dasteht und hier keine, liegt nicht an den Läufen, sondern
daran, welche Fassung der Zeile zufällig konserviert wurde.

**Und noch einmal auf #93**, dem PR, der diesen Abschnitt erweitert. Am 18.9.
wurde um 05:18:38 gemergt, um 05:18:41 startete der ready-Lauf — drei Sekunden
**nach** dem Merge — und um 05:19:50 stand er auf «Completed». Angekommen ist
nichts: kein Review-Objekt zu `639fce5`, und die einzige Befundlos-Meldung
trägt 05:04:32 und gehört zum manuellen Lauf davor. Dieselbe Prüfung wie bei
#88 und #89.

**Der Rückgriff hat dort funktioniert, und das ist der Teil, der neu ist.** Ein
`@codex review` auf dem gemergten #93 um 05:25:21 lieferte um 05:28:46 ein
Review-Objekt mit zwei Befunden — zum **Merge-Commit** `7755c900`, nicht zum
Branch-Stand. Damit ist an einem Fall belegt, dass der Rückgriff nach einem
stillen Lauf tatsächlich ein Urteil beschafft, und zwar über den Stand, der in
`main` liegt. Was er nicht beschafft, ist das Urteil des stillen Laufs: Ob der
ready-Lauf dieselben zwei Befunde gehabt hätte oder gar keine, bleibt offen.

**Zugestellt wird aber durchaus.** Auf #80 wurde um 18:48:36 gemergt, und um
18:48:45 — neun Sekunden danach — erschien ein Review-Objekt mit Befund zum
Head `836568f`. Ein Ergebnis kann den Merge also überholen; dass auf #60 und
#79 keines ankam, liegt nicht daran, dass nach dem Schliessen grundsätzlich
nichts mehr zugestellt würde.

Praktisch heisst das: **Nach einem frühen Merge kann am PR nicht mehr
ablesbar sein, ob geprüft wurde** — verlassen kann man sich weder darauf noch
auf das Gegenteil. Wer es wissen muss, sieht nach, und zwar mit allen drei
Abfragen: `get_reviews` für das Objekt, `get_comments` für die
Issue-Kommentare, `get_review_comments` für alles, was als Antwort in einem
Review-Thread steht. Die dritte gehört hierher, weil ohne sie ein Teil der
Antwort fehlt: Am 18.9. stand auf #98 die Kontingent-Meldung nur dort und auf
#103 die Befundlos-Meldung. Wer bloss die beiden anderen fährt, sieht im einen
Fall die Sperre nicht und im anderen den geglückten Lauf.

**Eine gefundene Ausfallmeldung erklärt aber nur die Vergangenheit.** Sie sagt,
warum *damals* nichts kam, und nichts darüber, ob die Sperre jetzt noch steht —
am 18.9. war sie um 08:42 belegt und um 09:45 weg. Wer aus einer älteren
Meldung schliesst, ein Aufruf lohne sich nicht, lässt den Merge-Commit
ungeprüft aus einem Grund, den er nicht gemessen hat. Gemessen wird der
aktuelle Zustand nur durch einen Aufruf.

Was die drei Abfragen ergeben, trennt drei Lagen:

- **Ein Review-Objekt oder eine Befundlos-Meldung zum Merge-Commit.** Dann
  liegt das gesuchte Ergebnis vor, und der Rückgriff hat keinen Gegenstand.
- **Nur eine Ausfallmeldung.** Sie erklärt das Fehlen und sagt über jetzt
  nichts — also ein neuer Aufruf.
- **Nichts davon.** Ebenfalls ein neuer Aufruf.

In den beiden letzten Fällen ist der Rückgriff derselbe: ein Aufruf von Hand,
der auf dem gemergten PR anläuft und den Merge-Commit prüft.

### Der Vorlauf trennt «angelaufen» nicht von «abgeblockt»

Naheliegend wäre, aus einer schnellen Antwort auf die Sperre zu schliessen und
aus einer ausbleibenden auf einen laufenden Job. Die Messungen vom 18.9. auf
#98 geben das nicht her:

| Aufruf (UTC) | Form | Antwort nach | Was kam |
|---|---|---|---|
| 06:27:19 | Issue-Kommentar | 14 s | Lauf «Running» |
| 06:31:40 | Antwort im Review-Thread | 11 s | Lauf «Running» |
| 06:35:51 | Issue-Kommentar | 12 s | Lauf «Running» |
| 06:39:50 | Antwort im Review-Thread | 11 s | Kontingent-Meldung |
| 06:40:59 | Issue-Kommentar (nur Zitat) | 12 s | Kontingent-Meldung |
| 06:44:08 | Issue-Kommentar | 9 s | Kontingent-Meldung |
| 07:32:49 | Issue-Kommentar | 8 s | Kontingent-Meldung |

Für die Zeilen oben gilt: Die Sperre antwortete in 8 bis 12 Sekunden, ein Start
kam nach 11 bis 14 — die Bereiche überlappen. **Den Text lesen, nicht die Uhr:**
Was nach zwölf Sekunden erscheint, kann beides sein — und ohnehin nicht nur
beides: Die Tabelle führt die zwei Meldungen, die an diesem Vormittag kamen,
nicht die möglichen. Die Environment-Meldung ist eine dritte.

**Bleibt eine Meldung ganz aus, ist das keine vierte.** Dann steht nichts da,
was sich lesen liesse, und ein laufender oder verzögerter Review sieht genauso
aus wie einer, der nie antwortet — es ist derselbe Fall wie «gar nichts» in der
Tabelle der Formen, und er belegt nichts.

Die Versuchung, aus der Wartezeit doch etwas zu machen, ist real: Beim Messen
dieser Tabelle ist aus den schnellen Absagen erst einmal eine Faustregel
geworden («bleibt die Meldung eine Viertelminute aus, läuft es»), und die
Überlappung stand in derselben Tabelle schon da.

**Die Spanne ist auch kein Fenster für andere Tage.** Sie stammt von einem PR
an einem Vormittag. Am 29.8. antworteten zwei Läufe schon nach vier und zehn
Sekunden (siehe «Derselbe PR bekommt auf dieselbe Frage verschiedene
Antworten»); eine Untergrenze von acht Sekunden gibt es also nicht. Wächst die
Tabelle, sind die beiden Spannen daneben fällig.

### Beide Wege können funktionieren

Automatisch hat geliefert (#45 um 08:55:43, ohne jeden vorherigen Kommentar auf
dem PR) und versagt (#53 um 18:43:41); von Hand hat geliefert (#45, #51, #53,
#55, #93, #95 zweimal) und versagt (#53 um 18:51:30). Über den *Einfluss* des
Wegs sagt das nichts: Je ein gemessener Fehlschlag auf beiden Seiten, und auf
beiden Seiten zu wenige Versuche, als dass ein Unterschied sichtbar würde.

Eine Quote stand hier und ist gestrichen. Sie nannte einen Nenner, den die
Aufzählung daneben schon widerlegte, und eine spätere Fassung schrieb dazu, der
Nenner sei gewachsen — ohne die Zahl anzufassen. Genau der Fall aus «Zahlen,
die eine Aufzählung wiederholen»: Die Aufzählung ist die Quelle, und wer die
Kopie bloss kommentiert, hat sie nicht geprüft.

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

### Die Episode vom 18.9.2026

Vier Läufe auf PR #97 lieferten zwischen 06:15 und 06:35 je einen Befund (siehe
«Vier Runden an einem kurzen Test»). Der nächste Aufruf auf demselben PR lief
auf die Sperre, und jeder weitere Versuch lief ebenso auf sie — auch die
anderer PRs und anderer Repos —, bis Stunden später wieder einer durchlief:

| Zeit (UTC) | PR | Auslöser |
|---|---|---|
| 06:37 | #97 | `@codex review` |
| 06:39:50 | #98 | Aufruf als Antwort im Review-Thread |
| 06:40:59 | #98 | Kommentar, der die Zeichenfolge nur *zitiert* |
| 06:44:08 | #98 | `@codex review` auf dem bereits gemergten PR |
| 06:46 | #99 | `@codex review` |
| 06:51 | #99 | Draft → ready |
| 07:04 | #100 | `@codex review` |
| 07:06 | #100 | Draft → ready |
| 07:08:02 | `news-monitor-mcp`#85 | `@codex review` |
| 07:08:11 | `swiss-cultural-heritage-mcp`#86 | `@codex review` |
| 07:32:49 | #98 | `@codex review` auf dem bereits gemergten PR |
| 07:48 | #101 | `@codex review` |
| 08:01:15 | `news-monitor-mcp`#86 | `@codex review` |
| 08:01:17 | `swiss-cultural-heritage-mcp`#87 | `@codex review` |
| 08:21:14 | `news-monitor-mcp`#86 | Draft → ready |
| 08:38:51 | `swiss-cultural-heritage-mcp`#88 | `@codex review` |
| 08:51 | #101 | `@codex review` |

**Eine nackte Nummer meint dieses Repo.** Die Zeilen aus anderen Repos tragen
deshalb ihren Namen — die Nummernkreise überschneiden sich, und ein `#88` gibt
es hier wie dort.

**Dasselbe Konto bekam die Absage in drei Repos.** «Wie das Kontingent
funktioniert» sagt seit dem 29.8., es hänge am Konto und nicht am Repo; die
Zeilen aus zwei weiteren Repos sind dazu die erste Messung ausserhalb dieses
einen. Die Zeilen 07:08:02 und 07:08:11 liegen neun Sekunden auseinander und
gehören zwei verschiedenen Repos; um 07:32 und 07:48 wies dasselbe Konto in
einem dritten ab.

**Eine gleichzeitig stehende Sperre ist das nicht.** Der Absatz zur
Punktmessung weiter unten gilt auch hier, und er gilt auch für neun Sekunden:
Bei einem rollenden Fenster kann sich das Kontingent zwischen zwei Zeilen
geöffnet und durch Aktivität, die von hier aus nicht zu sehen ist, wieder
erschöpft haben. Für das dritte Repo liegen die Messpunkte ohnehin 24 und 40
Minuten daneben.

Belegt ist damit eine Folge von Absagen über Repo-Grenzen hinweg — nicht, dass
die Sperre zu einem Zeitpunkt in allen dreien stand, und nicht, dass ein
Ausweichen in ein anderes Repo nichts brächte. Wer das eine aus dem anderen
folgert, tut dasselbe wie jemand, der aus der Tabelle eine Dauer macht.
(Dieser Absatz stand zuerst umgekehrt da und wurde durch einen Codex-Befund
auf PR #108 zurückgenommen.)

**Neu daran: Die Sperre trifft auch den automatischen Auslöser.** Die Zeilen
mit «Draft → ready» gehören zu Läufen, die niemand von Hand angestossen hat —
dieselbe Meldung, kein Ergebnis. Umschalten ist also kein Weg an einer
stehenden Sperre vorbei. Für die übrigen Auslöser (PR-Eröffnung,
`@codex security review`) ist das nicht gemessen.

Ein Zusammenhang zwischen den gelieferten Läufen und der Sperre ist **nicht
belegt** — was sonst noch auf das Konto ging, ist von hier aus nicht zu sehen.
Belegt ist die Reihenfolge: erst Ergebnisse, dann Fehlschläge.

**Sie ist wieder aufgegangen, und das grenzt den Zeitpunkt ein.** Um 08:51 wies
sie noch ab. Um 09:54:12 lief ein Aufruf auf demselben PR an, und um 09:57:00
stand die Befundlos-Meldung zu Commit `42f7517` da — das erste Ergebnis seit
06:35. Sie fiel also zwischen diesen beiden Zeitpunkten; wo genau, geben die
Messpunkte nicht her, weil dazwischen niemand nachfragte.

Um 09:56:36 lief ein Aufruf in `swiss-cultural-heritage-mcp`#88 an und
lieferte um 09:59:48 zwei Befunde — dasselbe Konto, ein anderes Repo,
zweieinhalb Minuten nach dem Lauf hier. **Am Endpunkt ändert das nichts:** Er
ist durch die letzte Absage um 08:51 und den gelungenen Aufruf um 09:54:12
eingegrenzt, und ein weiterer Erfolg danach kann dieses Intervall nicht
verkleinern. Der Messpunkt belegt allein, dass kurz darauf auch im anderen
Repo ein Lauf gelang.

Eine Dauer folgt daraus nicht, und auch keine Untergrenze dafür. **Die Tabelle
ist eine Punktmessung:** Jede Zeile belegt eine Absage in ihrem Augenblick,
keine Strecke bis zur nächsten. Bei einem rollenden Fenster kann sich das
Kontingent zwischen zwei Zeilen geöffnet und durch Aktivität, die von hier aus
nicht zu sehen ist, wieder erschöpft haben — «Wie das Kontingent funktioniert»
hält das für die Episode vom 29.8. schon fest. Ob über die ganze Reihe dieselbe
Sperre stand, ist damit offen.

Was 08:51 und 09:54 eingrenzen, ist deshalb ein **Endpunkt** und keine Spanne:
der Zeitpunkt, an dem zuletzt eine aufging. Warum dort — abgelaufenes
Fünf-Stunden-Fenster, etwas anderes —, ist von hier aus nicht zu sehen. Wer aus
einer Episode eine Wartezeit ableitet, hat sie erfunden: dieselbe Lage wie beim
GitHub-Rate-Limit in `CLAUDE.md`, nur mit einem Endpunkt mehr.

Die Tabelle ist fortzuschreiben, solange eine Sperre hält — Sätze daneben, die
ihre Zeilen oder ihre Spanne zählen, veralten damit.

**Auch der Rückgriff auf einem gemergten PR fällt darunter.** Die beiden
#98-Aufrufe um 06:44:08 und 07:32:49 galten dem Merge-Commit `2e80539`, dessen
Branch-Stand ungeprüft nach `main` gegangen war. Der Hebel, der sonst genau
diese Lücke schliesst, ist bei stehender Sperre keiner — und der Head bleibt
ungeprüft, bis sie fällt.

**Was die Regel oben verlangt, ist hier nicht geschehen.** «Blockiert es, bleibt
der PR Draft, bis wieder ein Lauf durchgeht» — beide PRs wurden stattdessen
gemergt, #97 um 06:41 und #99 um 06:55, jeder mit einem Head, für den kein
Ergebnis vorlag. Beide Male hat ein Mensch entschieden, und beide Male stand die
Lage vorher als Kommentar auf dem PR. Festgehalten wird es, weil die Regel damit
zum zweiten Mal an ihrer eigenen Anwendung gescheitert ist: Der erste Einsatz
des Verfahrens verfehlte sie beim Umschalten, dieser hier beim Merge.

### Die Nachmittagssperre desselben Tages (18.9.2026)

Der Abschnitt davor, «Die Episode vom 18.9.2026», beschreibt den Vormittag.
Am Nachmittag ging die Sperre ein zweites Mal zu. Dazwischen lag ein offenes
Fenster: Von 12:50 bis 13:18 liefen fünf
Läufe an drei PRs an (12:50:48 auf #110, 13:01:52, 13:04:40 und 13:09:07 auf
#111, 13:15:13 auf #112), und der letzte lieferte um 13:18:22 zwei Befunde.
Der nächste Aufruf lief auf die Sperre:

| Zeit (UTC) | PR | Auslöser | Wortlaut |
|---|---|---|---|
| 13:19:55 | #112 | Aufruf als Antwort im Review-Thread | mit «for code reviews» |
| 13:45:17 | #112 | Draft → ready | mit |
| 13:47:10 | #112 | `@codex review` auf dem bereits gemergten PR | mit |
| 13:51:08 | #113 | `@codex review` | mit |
| 13:51:48 | #113 | Draft → ready | mit |
| 13:52:39 | #114 | `@codex review` | mit |
| 13:53:36 | #114 | Draft → ready | mit |
| 13:55:49 | #114 | Kommentar, der die Zeichenfolge nur zitiert | **ohne** |
| 13:58:10 | #115 | **Eröffnung als Draft** | **ohne** |
| 13:58:31 | #115 | `@codex review` | mit |
| 14:01:51 | #115 | Draft → ready | mit |
| 14:08:10 | #117 | **Eröffnung als Draft** | **ohne** |

**Die Spalte «Wortlaut» trennt drei Zeilen von den übrigen neun.** Keiner der
drei Auslöser ist eine ausdrückliche Review-Anforderung: zweimal die Eröffnung
als Draft, einmal ein Kommentar, der die Zeichenfolge nur zitiert. Was daraus
folgt und was nicht, steht weiter unten bei der kurzen Fassung und unter
«Fassungen zur stillen Draft-Eröffnung».

**Das Zugehen ist auf 282 Sekunden eingegrenzt** — um 13:15:13 lief noch ein
Lauf an, um 13:19:55 kam die Absage. Die Vormittagsepisode gibt das nicht her:
Dort sind die Randzeiten nur minutengenau festgehalten. Wann die Sperre
*fällt*, sagt auch diese Episode nicht; gemessen ist nur, wann sie zuging.

**Eine frühere Fassung nannte hier 93 Sekunden** und stützte sich auf die
Zustellung um 13:18:22. Das war falsch: Eine Zustellung belegt, dass der Lauf
**vorher** anlief, nicht dass das Kontingent im Augenblick der Zustellung noch
offen war. Die obere Grenze muss deshalb am letzten *Start* hängen, nicht am
letzten Ergebnis. Der Fehler stand keine Stunde in `main` und ist nicht durch
einen Review aufgefallen, sondern beim Nachrechnen für den nächsten Nachtrag —
dieselbe Klasse wie die Zeitstempel unten.

**Zwei Läufe hatten unmittelbar zuvor Befunde geliefert, die eingearbeitet
werden mussten.** Das ist dasselbe Muster wie unter «Die Korrekturschleife
verbraucht das Kontingent»: Jede Korrekturrunde kostet einen Lauf, und die
Runden häufen sich dort, wo ein Text viele Befunde trägt.

**Auch hier traf die Sperre den automatischen Auslöser** — auf jedem PR der
Tabelle, der umgeschaltet wurde. Umschalten ist kein Weg an ihr vorbei; die
Vormittagsepisode zeigt es einmal, diese Episode an jedem betroffenen PR.

**Und auch hier wurde gemergt, statt zu warten.** #112 um 13:45:48, #113 um
13:52:23, #114 um 14:01:36 und #115 um 14:01:53, jeder mit einem Head, für den
kein Ergebnis vorlag; auf #115 lag die Absage **zwei Sekunden** vor dem Merge.

Die vier Zeitangaben stammen aus dem Committer-Datum der Merge-Commits.
Frühere Fassungen nannten 13:45:50, 13:52:24 und 14:01:37 und hatten damit die
Ankunftszeiten der Webhook-Meldungen genommen — drei Abweichungen von einer
bis zwei Sekunden, aus zwei unabhängig entstandenen Fassungen. Der Griff zur
Benachrichtigung statt zur Primärquelle ist offenbar der naheliegende, auch
wenn die Regel danebensteht. Wie am Vormittag
hat ein Mensch entschieden, und wie dort stand die Lage vorher als Kommentar
auf dem PR. Was es gekostet hat, ist offen und bleibt es, solange kein Lauf
durchgeht: Nicht ein schlechtes Ergebnis liegt vor, sondern keines.

Bemerkenswert ist der Gegenstand: #113 trägt eine Aussage über das
Zustellverhalten des Prüfers — und ist der Stand, den dieser Prüfer nicht
gelesen hat. Für #115, der diesen Abschnitt einträgt, gilt dasselbe.

**Drei Absagen der Tabelle lauten anders als die übrigen neun.** Die erste
davon auf #114 um 13:55:49:

```
You have reached your Codex usage limits. You can see your limits in the
[Codex usage dashboard](https://chatgpt.com/codex/cloud/settings/usage).
```

Es fehlt das «for code reviews», das die übrigen belegten Absagen tragen. Wer
den notierten Wortlaut als ganzen Satz
vergleicht, erkennt diese Fassung nicht und zählt sie als «gar nichts», also
als den einen Ausgang, aus dem sich nichts schliessen lässt. Der Handgriff ist
deshalb, auf den **Anfang** zu prüfen — «You have reached your Codex usage
limits» —, nicht auf den vollen Satz. Das ist dieselbe Regel wie «Den Text
lesen, nicht die Zahl», eine Ebene tiefer: auch ein bekannter Text kommt in
Fassungen.

**Warum sie anders lautet, ist offen — aber nicht mehr aus einem Fall.** Diese
Zeile stand zuerst als Einzelfall hier, und der Satz daneben sagte, eine
Zuordnung «kurze Fassung ↔ anderer Auslösertyp» wäre aus n = 1 erfunden. Zwei
weitere Fälle kamen binnen zwölf Minuten dazu, aus einer zweiten Sitzung am
selben Repo: #115 um 13:58:10 und #117 um 14:08:10, beide nach einer
**Eröffnung als Draft**, beide ohne den Zusatz.

Damit stehen sich gegenüber: drei kurze Fassungen, deren Auslöser **keine**
ausdrückliche Review-Anforderung war (zweimal Eröffnung, einmal ein Zitat der
Zeichenfolge), und neun lange, deren Auslöser eine war (Aufruf im Thread,
Aufruf als Issue-Kommentar, Umschalten auf ready).

**Eine Erklärung ist das immer noch nicht.** Drei zu neun ist keine Zuordnung,
sondern eine Verteilung; gemessen ist, was die Meldung sagt, nicht warum. Was
sich sagen lässt: Die kurze Fassung ist bisher nie nach einer ausdrücklichen
Anforderung aufgetreten — und ein Gegenfall wäre eine einzige Absage, die das
umkehrt.

**Alle zwölf liegen in Sperrzeiten.** Ob dieselben Auslöser bei freiem
Kontingent überhaupt etwas erzeugen, ist an keiner der Zeilen gemessen.

**Diese Absage war nicht angefordert — der dritte Fall für die Fussangel.**
Der Kommentar von 13:55:41 hielt fest, dass auf #114 kein Ergebnis vorliegt,
und zitierte dabei die Auslöser-Zeichenfolge in einer Tabellenzelle, in
Backticks. Acht Sekunden später kam die Absage. Ein anderer dokumentierter
Auslöser lag nicht vor: Die Codex-Hinweisbox nennt Eröffnung, Umschalten auf
ready und den Kommentaraufruf, und keines davon geschah; das einzige andere
Ereignis in diesen Sekunden war der Abschluss der CI-Prüfsuite um 13:55:45,
der dort nicht als Auslöser geführt wird.

**Die Gegenprobe fehlt weiterhin.** Das Entfernen der Zeichenfolge aus
demselben Kommentar um 13:56:33 brachte keine weitere Absage — aber eine
Bearbeitung ist kein neuer Kommentar, und ob sie überhaupt einen Versuch
auslöst, ist unabhängig vom Inhalt ungemessen. Ein Kommentar ganz ohne die
Zeichenfolge bleibt der offene Fall.

**Der Fall ist unangenehm genau am Ort seiner Regel aufgetreten:** in einem
Kommentar, der vor dem ungeprüften Merge warnte, verfasst von jemandem, der
die Fussangel im selben Atemzug zitierte.

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

Zwei Abfragen, aus demselben Grund, aus dem am einzelnen PR keine der drei
allein genügt:

```
search_pull_requests: user:malkreide commenter:chatgpt-codex-connector[bot] updated:>=<Datum>
```

Findet, wo er als Kommentar *geschrieben* hat — Befundlos-Meldung und die
beiden Ausfallmeldungen, die aber nicht voneinander; dafür ist der Text zu
lesen. Ein Review **mit** Befund ist kein Kommentar und taucht hier nicht auf.

Ob `commenter:` auch eine Antwort in einem Review-Thread erfasst, ist **nicht
gemessen**. Seit dem 18.9. ist bekannt, dass sowohl die Kontingent- als auch
die Befundlos-Meldung diese Form annehmen kann; ein PR, der eine davon *nur*
so trägt, könnte dem Vorfilter entgehen.

Die Richtung des Irrtums ist dabei verschieden. Entgeht eine Ausfallmeldung,
fehlt ein PR, an dem nichts geprüft wurde. Entgeht eine **Befundlos**-Meldung,
fehlt ein PR, der geprüft *ist* — und er sieht in einer Erhebung aus wie einer,
den niemand angesehen hat. Wer sich auf den Vorfilter verlässt, prüft das
besser einmal nach.

**Hier bleibt etwas offen, und es steht hier, statt behoben zu sein.** Die
beiden Richtungen gelten nur, solange die Thread-Antwort die einzige
einschlägige Bot-Aktivität am PR ist. Trägt derselbe PR schon ein
Review-Objekt und bekommt später eine Thread-Meldung, findet ihn
`reviewed-by:` weiterhin — und damit ist nichts verloren: Wer den gefundenen
PR danach mit allen drei Abfragen ansieht, sieht die Thread-Meldung. Die
Suchen sind Vorfilter, nicht die Erhebung. Gar nichts zu sehen bekommt nur,
wer einen PR vor sich hat, den **beide** Vorfilter nicht zurückgeben.

Eine Fassung, die beides sauber trennt, steht hier nicht. Der Befund kam am
18.9. vom Rückgriff auf dem schon gemergten #104, und die Korrekturschleife
war da bei einer Reihe von Befunden derselben Klasse angelangt: eine Regel
geschärft und den zusammenfassenden Satz daneben eine Stufe zu breit gefasst.
Abgebrochen wurde sie nicht, weil der Stand sauber wäre, sondern mit einem
Menschen — so, wie «Zum Verfahren für Doku-PRs» in `CLAUDE.md` es für diese
Lage verlangt. Dieser Absatz ist das, was dort «schreibt hin, was offen
blieb» heisst.

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
damit. Neben den 28 Sekunden vom 28.8., den 81 Sekunden auf #59 und den 124
auf #110 ist das der Fall, in dem Aufpassen nichts mehr ausrichtet — wer sicher
sein will, wartet das Ergebnis ab. Wogegen diese Abstände zu halten sind, ist
erst am 18.9. danebengemessen worden: Wie lange eine geprüfte Behebung
tatsächlich braucht, steht unter «Der Review ist da, der Merge geht trotzdem
durch».

**Umschalten auf ready ist hier die Merge-Entscheidung.** Der ready-Auslöser
startet einen Lauf; sein Ergebnis kam in diesen drei Fällen erst nach dem
Merge:

| PR | ready | Merge | Abstand | Ergebnis des ready-Laufs |
|---|---|---|---|---|
| #83 | 18:13:32 | 18:13:33 | 1 s | 18:14:35, 62 s nach dem Merge |
| #84 | 18:22:00 | 18:22:02 | 2 s | 18:23:40, 98 s danach |
| #86 | 03:41:18 | 03:41:21 | 3 s | 03:42:50, 89 s danach |

Die Ergebniszeiten stammen aus der Statuszeile des jeweiligen Laufs mit
Auslöser «Draft marked ready». **Nicht mit den Vorläufen der manuellen Aufrufe
verrechnen** — sie stehen unter «Der manuelle Aufruf: was belegt ist»: Diese
ready-Läufe brauchten **63 bis 100 Sekunden ab dem Umschalten** — die Zahlen in
der Tabelle sind die Abstände zum Merge und ein bis zwei Sekunden kleiner. Der
Abstand von ein bis drei Sekunden liegt weit darunter — mehr sagt die Tabelle nicht, und für andere
Fälle ist die Reihenfolge damit nicht behauptet. **Die Spanne ist auch kein
Deckel:** Der ready-Lauf auf #88 stand am 31.8. um 04:43:50 auf «Running» und
um 04:46:12 auf «Completed», also 142 Sekunden reine Laufzeit. Das ist aus der
Statuszeile des Laufs gemessen und damit ab seinem Start, während die 63 bis
100 Sekunden ab dem Umschalten laufen — einem Zeitpunkt wenige Sekunden davor.
In beiden Bezugsrahmen liegt der Wert über der Spanne. **Was das kostet,
ist an #83 gemessen:** Dort lag seit 18:05:51 ein P1 offen — die Löschregel
löschte ungemergte Branches, an einem Bare-Repo nachgestellt —, und der Merge
um 18:13:33 nahm ihn mit nach `main`. Behoben erst in #84.

**Die Wertebereiche überlappen inzwischen.** Der manuelle Aufruf auf #109
lieferte am 18.9.2026 nach 82 Sekunden und liegt damit mitten im Bereich der
63 bis 100 Sekunden dieser ready-Läufe; beide Werte laufen vom Auslöser bis
zum zugestellten Ergebnis. Aus einer Dauer ist also nicht zu lesen, welcher
Auslöser dahinterstand. Getrennt zu halten sind die beiden Bezugsrahmen
trotzdem — nur nicht mehr deshalb, weil sie weit auseinanderlägen.

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
  Ein vierter kam am 18.9. auf #108 dazu; er steht unter «Die sechs Formen, in
  denen sich ein Lauf zeigt». Dort scheiterte die Zuordnung **nicht**, obwohl
  die Zeile genauso überschrieben wurde — weil jeder der beiden Läufe sein
  eigenes Ergebnis zustellte. Das ist der Unterschied zu diesem Fall: nicht
  der geteilte Commit, den beide haben, und auch keine belegte Gleichzeitigkeit,
  sondern die fehlenden Ergebnisse.

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

**Am 18.9. ist er befolgt worden, und der Durchgang ist festgehalten.** Auf
#108, ebenfalls einer Regeldatei, nannte ein manueller Lauf `e3141f6` um
11:01:23 befundlos. Statt zu mergen, wurde umgeschaltet und der ausgelöste
Lauf abgewartet; er fand um 11:04:52 einen zutreffenden P2 auf demselben
Commit. Die Behebung ging in denselben PR. Ein früherer Durchgang, in dem der
Handgriff befolgt wurde, ist hier nicht verzeichnet — ob es einen gab, sagt
diese Datei nicht.

Was der Fall **nicht** hergibt: dass der ready-Lauf gründlicher sei. Dreimal
war er der findende, und dreimal ist «Ein Ergebnis sagt etwas über den Lauf,
nicht über den Text» die einfachere Erklärung — die Läufe streuen, und der
ready-Lauf ist bei diesem Verfahren bloss derjenige, der zuletzt kommt. Der
Handgriff verlangt nicht, ihn für besser zu halten, sondern nur, keinen Lauf
ungelesen zu lassen.

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

### Vier Fassungen, die kein Review getroffen hat (18.9.2026)

Alles oben in diesem Abschnitt ist von einem Review abgeräumt worden. Am
Nachmittag des 18.9. lief das Kontingent leer, und die Arbeit ging weiter. Was
danach falsch war, fiel nicht bei einer Kontrolle auf, sondern beim
Weiterarbeiten — jedes Mal, weil der nächste Nachtrag zufällig dieselben Zahlen
noch einmal anfasste.

| # | Was falsch war | Wobei es auffiel |
|---|---|---|
| 1 | «122 Sekunden» zwischen Befund und Merge auf #110 | beim Zusammenstellen des nächsten Nachtrags, **vor** dem Merge |
| 2 | «93 Sekunden» als Eingrenzung des Zugehens | beim Nachrechnen für den nächsten Nachtrag, **nach** dem Merge |
| 3 | dieselbe Zahl stand an **zwei** Stellen; korrigiert war eine | beim Auflösen eines Merge-Konflikts |
| 4 | drei Merge-Zeiten (#112, #113, #114) | beim Zusammenführen zweier Fassungen |

**Zwei Klassen, und beide haben ihre Regel neben sich stehen.**

*Die Benachrichtigung statt der Primärquelle.* Fall 1 und Fall 4 sind zusammen
vier Zeitangaben, genommen aus den Ankunftszeiten der Webhook-Meldungen statt
aus `created_at`, `submitted_at` oder dem Committer-Datum. Die Abweichung
beträgt ein bis vier Sekunden — klein genug, um nicht aufzufallen, gross
genug, um eine Spanne zu verfälschen. **Drei davon stammen aus dieser Sitzung,
eine aus einer anderen**, die unabhängig an derselben Datei arbeitete. Der
Griff zur Benachrichtigung ist offenbar der naheliegende: Sie liegt vor, die
Primärquelle kostet eine Abfrage.

*Die Halbkorrektur.* Fall 3 ist der vierte an diesem Tag, an dem eine
zurückgenommene Aussage an der gemeldeten Stelle verschwand und anderswo
stehen blieb — zweimal im PR-Text, während der Diff bereits korrigiert war,
einmal in einem Querverweis zwölfhundert Zeilen entfernt, einmal in der
Einleitung über der Tabelle, in der die Zahl richtiggestellt worden war. Der
Handgriff dagegen kostet einen Aufruf: **nach jeder Rücknahme den Volltext
nach der zurückgenommenen Aussage durchsuchen, den PR-Text eingeschlossen.**
Er stand nach dem zweiten Fall schon fest und wurde beim dritten und vierten
nicht angewandt.

**Was der Abschnitt nicht hergibt: dass Weiterarbeiten eine Prüfung ersetzt.**
Alle vier fielen zufällig auf, weil der nächste Nachtrag dieselbe Stelle
berührte. Wie viele Fehler derselben Art unberührt blieben, ist unbekannt —
und aus vier Funden folgt keine Fundrate. Belegt ist allein, dass sie den
Punkt überlebt haben, an dem sie hätten auffallen sollen.

**Alle vier betreffen Zahlen** — drei einen falschen Wert, einer einen
richtigen an der falschen Stelle. «Zahlen, die eine Aufzählung wiederholen»
steht seit Wochen in derselben Datei. Die Regel zu kennen, hat nicht gereicht;
ihre Anwendung kostet beim Schreiben eine Abfrage, und genau die wurde jedes
Mal gespart.

---

## 10. Zahlen, die eine Aufzählung wiederholen

Die Handlungsregel steht in `CLAUDE.md`. Hier die Fälle, an denen sie entstand:
am 29.8.2026 an dieser Datei, eine Review-Runde nach der anderen, und **jede
Korrektur erzeugte die nächste.** Der Fall mit dem kommentierten Nenner kam am
18.9. dazu.

| Die Zahl | Warum sie fiel |
|---|---|
| «sechs» im Text gegen «sieben» in der Einleitung | zwei Zählstellen für dasselbe Archiv |
| Überschrift «Drei Fassungen» | beim Beheben war ein vierter Eintrag dazugekommen |
| «Acht Fassungen» | ein Listenpunkt war die überlebende Fassung, keine gescheiterte |
| «vier Fehlschläge» über einer Tabelle mit acht Zeilen | Tabelle gewachsen, Prosa nicht |
| «Zwei Fehlschläge der Tabelle» | Nenner entfernt, Zähler stehen gelassen |
| «die Mehrzahl der Fälle oben» | im Abschnitt, der die Regel aufschrieb |
| «1 Fehlschlag von 5» neben einer längeren Aufzählung | Nenner kommentiert statt geprüft |

**Eine Kopie zu kommentieren ist nicht, sie zu prüfen.** Der Nenner
«1 Fehlschlag von 5» stand unter «Beide Wege können funktionieren» neben einer
Aufzählung, die ihn schon überholt hatte. Die Fassung danach schrieb daneben,
der Nenner sei gewachsen, und liess die Ziffer stehen: Der Satz war damit
richtig *über* die Zahl, und die Zahl blieb falsch. Das ist die bequemste Form
des Fehlers, weil sie wie Sorgfalt aussieht.

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

---

## 11. Vier Runden an einem kurzen Test (18.9.2026)

Die bisherigen Mehrfachrunden dieser Sammlung hingen an Regeltexten — fünf auf
dem Verfahrensabschnitt, neun auf PR #93. Am 18.9. lief dasselbe an etwas
anderem: an `tests/test_ruff_pin_doku.py`, einer einzelnen Testdatei mit einer
einzigen Frage. Vier Runden vor dem Merge, jede mit genau einem P2-Befund,
keiner bestritten.

| Runde | Head | Befund | Wirkung |
|---|---|---|---|
| 1 | `b67f091` | `rglob` über alle `*.md` mit handgeschriebener Ausschlussliste | Falsch-Rot |
| 2 | `814dd53` | Version negativ abgegrenzt (Liste verbotener Folgezeichen) | Falsch-Rot |
| 3 | `87a517f` | `ruff==` wörtlich, ohne PEP 503/508 | **Falsch-Grün** |
| 4 | `d5814c6` | nur der Versions-Präfix gefangen | **Falsch-Grün** |

### Der Gegenstand war die Fehlerklasse, die der Test enthielt

Der PR behob eine Versionszahl, die `CLAUDE.md` aus `pyproject.toml` kopiert
hatte, statt auf die Quelle zu verweisen. Jeder Befund der Tabelle traf
dieselbe Klasse **im Test selbst**: eine Verzeichnisliste, eine Zeichenliste,
eine Annahme über die Schreibweise des Paketnamens, eine über das, was nach
einer Versionsnummer folgen darf. Jedes Mal stand eine handgeschriebene
Aufzählung da, wo eine Quelle hingehört hätte — `.gitignore` für die Dateien,
die Versionssyntax für den Rest.

Wer ein Werkzeug gegen eine Fehlerklasse baut, baut sie mit hoher
Wahrscheinlichkeit hinein. Das ist kein Argument gegen das Werkzeug, aber eines
dafür, es prüfen zu lassen.

### Die Richtung kippte in der Mitte

Die ersten beiden Befunde machten die Suite rot, wo nichts falsch war: eine
erzeugte Datei in `venv/`, ein Satzpunkt hinter der korrekten Version. Das
fällt auf, sobald es eintritt.

Die letzten beiden liessen eine echte Drift durch. `Ruff == <andere Version>`
und `ruff==<Pin>.*` standen in einer getrackten Datei, und das Gate meldete
grün. Ein Gate mit Falsch-Grün ist schlechter als keines: Es beantwortet die
Frage, für die es da ist, mit einem Nein, das niemand nachprüft.

Beide Falsch-Grün-Befunde kamen aus den Runden **nach** den Falsch-Rot-Befunden.
Wer nach zwei sichtbaren Fehlern aufhört, weil «die offensichtlichen jetzt
raus sind», hört genau vor den stillen auf.

### Der teuerste Befund war die Korrektur des vorigen

Runde 2 lehrte, den Satzpunkt nicht mitzufangen: `Install ruff==<Pin>.` darf
nicht als `<Pin>.` gelesen werden. Die Korrektur fing daraufhin gar nichts
mehr hinter der Ziffernfolge — und warf damit die Anforderungssyntax mit weg.
`ruff==<Pin>.*` wurde zu `<Pin>`, stimmte damit überein und ging durch.
Runde 4 war also nicht ein neuer Fehler neben dem alten, sondern der alte, in
die Gegenrichtung überschossen.

Der Punkt ist am Zeichen nicht zu erkennen, nur am folgenden: In
`Install ruff==<Pin>.` schliesst er den Satz, in `ruff==<Pin>.*` gehört er zur
Anforderung. Eine Korrektur, die das nicht trennt, kann nur die eine oder die
andere Seite treffen.

Das ergänzt die Beobachtung aus «Zum Verfahren für Doku-PRs», dass eine
Straffung eine schon entfernte Behauptung zurückholen kann. Hier holte sie
nichts zurück, sondern erzeugte den Spiegelfehler. Der Handgriff ist derselbe:
**Nach einer Korrektur prüfen, was sie auf der anderen Seite kostet** — nicht
nur, ob der gemeldete Fall jetzt stimmt.

### Warum hier Platzhalter stehen

Die Beispiele oben nennen `<Pin>` statt einer Ziffernfolge, und das ist kein
Schönheitsentscheid. Der Test, um den es geht, gleicht jede `ruff==`-Angabe in
den versionierten Markdown-Dateien gegen den Pin ab — auch die in dieser Datei.
Mit ausgeschriebenen Versionen fiel er beim Schreiben dieses Abschnitts:
`docs/codex-reviews.md` nannte vier abweichende Angaben, und jede war ein Zitat
eines Fehlerfalls, keine Anweisung.

**Zitat und Anweisung kann der Test nicht trennen**, und eine Ausnahme dafür
wäre genau die Lücke, durch die eine echte Drift wieder durchginge. Die Kosten
trägt deshalb die Doku, nicht das Gate.

Ein Platzhalter ist hier ohnehin das Richtige: Ein Beispiel mit ausgeschriebener
Version wechselt beim nächsten Pin-Wechsel seine Bedeutung — `<Pin>.*` sieht
dem gepinnten Stand immer ähnlich, `0.16.5.*` nur so lange, wie dieser gilt.

### Jeder Lauf sah eine Schicht

Kein Lauf nannte zwei Befunde, und kein späterer wiederholte einen früheren.
Runde 1 sah die Dateiliste und nicht das Muster daneben; Runde 2 sah die
Zeichenklasse und nicht die Gross-/Kleinschreibung im selben Ausdruck. Der
Gegenstand war klein genug, dass alles gleichzeitig sichtbar war — gefunden
wurde es trotzdem nacheinander.

Daraus folgt nichts über eine Reihenfolge, die man erwarten dürfte. Es folgt
nur, dass ein Lauf mit Befund den Gegenstand so wenig erschöpft wie ein Lauf
ohne: **Nach einem behobenen Befund ist der nächste Lauf keine Formalie.**

### Was die Läufe nicht fanden

Zwei Mängel kamen beim Nachmessen der gemeldeten Befunde ans Licht, nicht aus
einem Review:

- Der Namensabgrenzung wegen las das Muster `xruff==0.16.3` und
  `my-ruff==0.16.3` als ruff — ein fremdes Paket wäre zur Drift erklärt worden.
  Aufgefallen beim Prüfen der Schreibweisen aus Runde 3.
- Die Positivkontrolle verlangte `X.Y.Z`, während der Pin-Leser daneben einen
  Vorabversions-Pin wie `0.16.5rc1` zulässt. Ein solcher Pin hätte die Suite
  falsch-rot gemacht — dieselbe Fehlerrichtung wie der Befund aus Runde 2, an
  einer Stelle, die keiner der Läufe nannte.

Der Review liefert damit den Anstoss und nicht die Vollständigkeit. Wer einen
Befund bloss abarbeitet, statt seine Umgebung nachzumessen, lässt den Teil
liegen, den ein Lauf nicht gesehen hat.

### Das Ende war kein befundloser Lauf

Das Verfahren für Doku-PRs verlangt, bis ein Lauf auf dem aktuellen Head nichts
mehr findet. So weit kam es nicht: Nach Runde 4 lief die Anforderung auf die
Kontingentsperre (siehe «Die Episode vom 18.9.2026»). Der Stand, der gemergt
wurde, trug damit kein Ergebnis — weder ein gutes noch ein schlechtes.

Die Befunde sagen nichts darüber, ob ein weiterer gekommen wäre. Sie sagen
etwas anderes: dass an diesem Gegenstand Runde um Runde etwas gefunden wurde
und keine leer ausging.

**Einer kam dann doch**, und zwar aus einem anderen Repo, in das die Datei am
selben Vormittag portiert wurde: «Ein Befund an der Kopie deckt das Original
auf» hält ihn fest. Dort steht auch, wie viele dieser Runden ihn überhaupt
sehen konnten — die naheliegende Lesart, alle vier hätten ihn übersehen, ist
falsch.

---

## 12. Ein Befund an der Kopie deckt das Original auf (18.9.2026)

Der Abschnitt davor endet mit dem Satz, der Review liefere den Anstoss und
nicht die Vollständigkeit — nachgewiesen an zwei Mängeln, die erst beim
Nachmessen auffielen. Dieser Abschnitt setzt ihn fort: Auch das Nachmessen war
nicht vollständig, und der fehlende Teil kam aus einem anderen Repo zurück.

### Der Gegenstand

`tests/test_ruff_pin_doku.py` ist am Vormittag des 18.9. nach
`swiss-cultural-heritage-mcp` portiert worden, wo `CLAUDE.md` dieselbe Drift
trug: eine ältere Version im Fliesstext, eine neuere im Pin. Die Datei ging
unverändert mit, bis auf den Modul-Docstring.

**Die alte Zahl steht hier bewusst ohne ihren Paketnamen.** Der Test prüft
jede versionierte Markdown-Datei, dieses Dokument eingeschlossen — wer einen
Drift-Fall mit der vollen Angabe aufschreibt, macht die Suite rot. Beim
Schreiben dieses Abschnitts ist genau das passiert, und die Meldung nannte
Datei und Zeile. `CLAUDE.md` löst es seit dem Vormittag genauso: Die Ziffern
stehen dort ohne das `ruff==` davor. Eine Nebenwirkung, kein Mangel — aber
eine, die man einmal erlebt haben muss.

Auf dem PR dort kam ein Lauf mit zwei Befunden. Der eine (P3) galt dem Muster
`_IN_DOKU`:

> The boundary check still matches a different valid distribution whose name
> ends in `.ruff`: for example, `my.ruff==0.1.0` is parsed as a Ruff pin
> because `.` is not excluded by the lookbehind.

Nachgemessen, vor jeder Änderung:

```
my.ruff==0.1.0     -> ['0.1.0']
foo.bar.ruff==2.0  -> ['2.0']
```

PEP 508 erlaubt den Punkt im Paketnamen, PEP 503 normalisiert `.`, `-` und `_`
auf dasselbe Zeichen. Eine versionierte Markdown-Datei, die ein fremdes Paket
`my.ruff` nennt, hätte die CI rot gemacht — ein Falsch-Rot an einer Stelle, an
der die dokumentierte ruff-Version stimmt.

Dass der Fix greift, belegt dieser Abschnitt selbst: Die beiden Zeilen oben
stehen in einer Datei, die der Test liest, und lösen ihn nicht aus.

### Warum das hier steht

Der Befund galt **beiden** Repos. Die Kopie und das Original trugen denselben
Lookbehind; gemessen wurde er in beiden, behoben in beiden.

Bemerkenswert ist, wann er kam — und hier ist genau zu zählen, welche Läufe
den Fehler überhaupt sehen konnten. Den Lookbehind gab es vorher nicht: Er
entstand mit `d5814c6` als Behebung des Befunds aus Runde 3, der die Datei
erstmals PEP 503/508 lesen liess. **Unter den vier Runden war er damit genau
einmal Gegenstand eines Laufs** — Runde 4 prüfte diesen Head und fand etwas
anderes (nur der Versions-Präfix wurde gefangen). Übersehen hat ihn also genau
ein Lauf, und zwar vor der Portierung; der Lauf danach, von dem dieser
Abschnitt handelt, fand ihn.

Danach überstand er das Nachmessen, bei dem `xruff` und `my-ruff` auffielen —
dieselbe Abgrenzung, dieselbe Zeile, der Punkt blieb liegen — und die
Portierung. Aufgefallen ist er im nächsten Lauf, der die Datei sah, und der
lief in einem anderen Repo.

Diese Zählung hat zwei Runden gebraucht. Die erste Fassung sprach von «vier
Läufen» und überzeichnete die Evidenz, auf der der Abschnitt beruht. Die
Korrektur sagte «genau einmal» — und war ebenfalls falsch, weil der Lauf, von
dem dieser Abschnitt handelt, denselben Fehler ja sah und fand. Beide Male kam
der Einwand aus einem Codex-Lauf auf PR #108, der zweite an der Korrektur des
ersten.

Das ist der Fall «Zahlen, die eine Aufzählung wiederholen», an einem Text über
Codex-Befunde — und daneben der Fall «Der teuerste Befund war die Korrektur des
vorigen», den «Vier Runden an einem kurzen Test» für dieselbe Datei schon
festhält. Eine Zahl beim Kürzen richtigzustellen, heisst nicht, sie richtig
gestellt zu haben.

**Der Mechanismus ist billig und hier zum ersten Mal beobachtet:** Wer eine
Datei portiert und am Ziel einen Review anfordert, bekommt einen weiteren Blick
auf das Original — ohne dort etwas anzufassen. Was der Lauf am Ziel findet, ist
an der Quelle nachzumessen, bevor man es für ein Problem der Kopie hält.

Was der Fall **nicht** hergibt: dass der fünfte Lauf ihn wegen der Portierung
fand. Ein fünfter Lauf am Original hätte ihn vielleicht genauso gefunden —
«Ein Ergebnis sagt etwas über den Lauf, nicht über den Text» gilt auch hier.
Der Beleg dafür ist ein **anderer, früherer** Fall: die 42 Läufe vom 23.8. in
Abschnitt 3, die über einen anderen Text gegenteilig urteilten. Diese Datei
ist da nicht durchgegangen — es gab sie noch nicht, sie entstand erst am
18.9. mit `b67f091`. Der Streubereich, den jener Fall misst, reicht aber
mühelos aus, um den Unterschied zwischen «übersehen» und «gefunden» auch ohne
die Portierung zu erklären. Belegt ist die Reihenfolge, nicht die Ursache.

### Der zweite Befund (P2) traf nur die Kopie

Er galt einer Zusicherung, die es am Original nicht gibt: Der Docstring-Test
des Kulturerbe-Repos prüfte nur, dass jede angebundene Quelle in der
Aufzählung steht, nicht die Rückrichtung. Eine entfernte Integration hätte
ihre Zeile im Docstring behalten, und kein Test hätte es gesehen.

Er steht hier, weil er die Grenze des Mechanismus zeigt: Ein Lauf an der Kopie
prüft die Kopie. Dass er dabei auch das Original trifft, ist der Glücksfall
und nicht die Regel — er hängt daran, wie viel von der Datei unverändert
mitgegangen ist.

### Was die Befunde kosteten

Beide kamen **um 09:59:48**. Der PR wurde **um 10:01:54** gemergt, 126 Sekunden
später, auf dem ungefixten Head. Die Behebung brauchte damit einen zweiten PR
im Kulturerbe-Repo und einen dritten hier — dieselbe Klasse wie die Fälle in
«Zu schnell mergen», nur mit der Besonderheit, dass ein Befund zwei Repos
betraf und beide nachzuziehen waren.

Die beiden Nachzügler wurden ihrerseits gemergt, während ihre Läufe noch
liefen; beide endeten auf «Completed» ohne zugestelltes Ergebnis.

