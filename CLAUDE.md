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
  «More of your lovely PRs please.», «Keep them coming!», «Hooray!»,
  «Breezy!»), und am 29.8. stand dort statt eines Satzes bloss ein 🚀; stabil
  ist nur der Satz davor. Zur 👍, die der Infokasten verspricht, siehe weiter
  unten — es gibt sie, verlassen kann man sich nicht auf sie. Der Kasten
  bleibt trotzdem eine schlechte Quelle, jetzt aus einem handfesteren Grund:
  Am 29.8. trugen zwei Kommentare desselben Bots auf demselben PR zwei
  verschiedene Fassungen davon, eine mit `@codex security review` und der
  👀/👍-Beschreibung, die andere ohne beides.
- **Der PR ist ein Draft** — dann laufen die *automatischen* Auslöser nicht an.
  Ein ausdrücklicher Aufruf schon: Am 28.8. lieferte er auf dem Draft #55 nach
  2 min 14 s einen Review. Ein kommentarloser Draft ist also kein Beleg, aber
  auch keine Sackgasse.
- **Das Kontingent ist weg** — dann schreibt er die Meldung oben.
- **Für das Repo fehlt eine Environment** — dann schreibt er:

  ```
  To use Codex here, create an environment for this repo.
  ```
- **Die Environment-Meldung kommt, obwohl geprüft werden kann** — derselbe PR
  bekam am 28.8. innerhalb von acht Minuten Meldung, Review und wieder
  Meldung (weiter unten). Ob der Auslöser darüber entscheidet oder die
  Prüfung schwankt, ist offen; praktisch heisst es, dass der nächste Aufruf
  durchlaufen kann.

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

Seit dem 29.8. gibt es eine sechste Form, und die ist nützlich: Codex legt zu
Beginn eines Laufs einen Status-Kommentar an, kenntlich am HTML-Marker
`<!-- codex-pull-request-review-summary -->`, und **aktualisiert ihn an Ort und
Stelle** von «🔄 Running» auf «✅ Completed». Kein zweiter Kommentar, sondern
ein `issue_comment.edited` — wer nur auf neue Kommentare achtet, sieht das Ende
des Laufs nicht. Seine Tabelle nennt als Einzige **beides**: den geprüften
Commit und den Auslöser («Manual request», «Draft marked ready»). Wer
auseinanderhalten will, welcher Lauf welchen Stand gesehen hat, liest ihn; die
Befundlos-Meldung und das Review-Objekt nennen nur den Commit.

Er ist allerdings kein Beleg für eine abgeschlossene Prüfung: Auf «Running»
steht er auch dann, wenn nie ein Ergebnis folgt.

Der Kommentarzähler allein reicht ohnehin nicht: `comments: 1` kann die
Befundlos-, die Kontingent-, die Environment-Meldung **oder** der
Status-Kommentar eines noch laufenden Reviews sein — vier Bedeutungen unter
derselben Zahl, darunter zwei gegensätzliche und eine, die noch gar nichts
sagt. Den Text lesen, nicht die Zahl. Und einen unbekannten Text wörtlich
zitieren, statt ihn in eine der bekannten Schubladen zu zwingen: Dieser
Abschnitt musste erst von drei auf vier und dann auf fünf Gründe wachsen, die
Formen von vier auf sechs, und die 👍-Reaktion stand hier zwei Fassungen lang
als Tatsache, eine als widerlegt — ehe sie am 29.8. wieder auftauchte.

Und ein befundloser Lauf ist kein Freispruch. Am 23.8. lief derselbe Text durch
42 Reviews: 36 meldeten denselben P2-Befund, 6 die Befundlos-Meldung — gleiche
Eingabe, gegenteiliges Urteil, alles in denselben neun Minuten. Ein sauberer
Lauf sagt damit etwas über den Lauf, nicht über den Text. Wer sein Häkchen
daran hängt, hängt es an einen Münzwurf.

Am 29.8. dasselbe noch einmal, aber an einem einzelnen benannten Fehler statt
an einer Verteilung — und deshalb schärfer, weil die richtige Antwort bekannt
ist. In diesem Abschnitt fehlte der `reviewed-by:`-Abfrage das
`updated:`-Fenster, das die `commenter:`-Abfrage daneben trägt, während der
Text dazu aufforderte, beide Ergebnisse zusammenzunehmen. Drei Läufe auf
denselben Defekt, neun Minuten:

| Zeit | Commit | Auslöser | Urteil |
|---|---|---|---|
| 07:00:06 | `37b8753` | `@codex review` | befundlos |
| 07:04:53 | `37b8753` | Draft → ready | **P2, zutreffend** |
| 07:09:27 | `789e901`, enthält denselben Defekt | `@codex review` | befundlos |

Zwei Freisprüche und ein Treffer für ein und denselben Fehler. Gefunden hat ihn
nur der Lauf, den niemand mit Absicht angestossen hat — er kam automatisch beim
Umschalten auf ready.

Portfolio-weit nachsehen — mit **zwei** Abfragen, aus demselben Grund, aus dem
am einzelnen PR `get_reviews` und `get_comments` beide nötig sind:

```
search_pull_requests: user:malkreide commenter:chatgpt-codex-connector[bot] updated:>=<Datum>
```

Findet, wo er *kommentiert* hat, also die Befundlos-Meldung und die beiden
Ausfallmeldungen — die aber nicht voneinander; dafür ist der Text zu lesen. Ein
Review **mit** Befund ist kein Kommentar und taucht hier gar nicht auf.

```
search_pull_requests: user:malkreide type:pr reviewed-by:chatgpt-codex-connector[bot] updated:>=<Datum>
```

Findet die Review-**Objekte**, also genau die Läufe mit Befund. Hier fehlt
umgekehrt jeder befundlose Review, weil der ein gewöhnlicher Kommentar ist.

Keine der beiden allein beantwortet «wurde geprüft?». Belegt ist eine Prüfung
durch ein Objekt **oder** eine Befundlos-Meldung, und jede Abfrage sieht nur
eine der beiden Sorten: Wer sich auf `commenter:` verlässt, übersieht die Repos
mit Befund; wer sich auf `reviewed-by:` verlässt, hält die befundlos geprüften
für ungeprüft.

Dasselbe `updated:`-Fenster gehört an **beide**, sonst sind ihre Ergebnisse
nicht zusammenzurechnen: Ohne Fenster liefert `reviewed-by:` jeden je geprüften
PR, und ein Repo mit einem Review vom Juni sähe im August-Fenster geprüft aus,
obwohl darin nichts lief.

Auch mit Fenster bleiben es Vorfilter. `updated:` datiert den **PR**, nicht die
Prüfung — ein im Juni geprüfter PR, den im August irgendein Kommentar berührt,
fällt weiterhin hinein. Ob die Prüfung selbst im Fenster liegt, entscheidet
allein der Zeitstempel am Review bzw. am Kommentar.

Und beide zusammen reichen nur so weit, wie es PR-Aktivität gab. Repos ohne
tauchen in keiner von beiden auf — das ist kein Beleg, dass dort geprüft wurde.

Gemessen am 23.8.2026 über die 41 Server-Repos: **25 mit mindestens einem
echten Review, 16 nur mit Absagen.** Zwei Vorbehalte, ohne die die Zahlen mehr
behaupten, als sie tragen. «Belegt» heisst hier «damals» — ein Review vom 16.8.
sagt über den heutigen Stand nichts. Und aus der Abfrage fällt nur die 25; die
16 verlangt, dass jemand in diesen Repos die Kommentartexte gelesen hat. Wer
sie stattdessen als 41 − 25 ausrechnet, zählt jeden befundlosen Review als
Absage — derselbe Fehlalarm wie oben, nur portfolio-weit.

Nicht mit der anderen Zahl desselben Tages verrechnen: Die 25 zählt Repos, die
42 weiter oben zählt Reviews.

Zweiter Weg, den Prüfer zu verlieren, ganz ohne Kontingentproblem: zu schnell
mergen. Am 21./22.8. lagen zwischen «ready for review» und Merge mehrfach drei
bis fünf Sekunden. Codex wird beim Umschalten von Draft auf ready ausgelöst und
braucht danach Zeit; wer sofort mergt, hat das Häkchen gesetzt und den Review
nicht abgewartet.

Es geht schlimmer, und am 29.8. ging es schlimmer. Auf #59 **war der Review
da**: um 07:04:53 stand der P2-Befund am PR, mit Datei und Zeile. Um 07:06:14
wurde gemergt — 81 Sekunden später, mit dem befundbehafteten Commit als Head.
Die Behebung war zu diesem Zeitpunkt noch nicht geschrieben; ihr Commit trägt
07:06:28. Der Defekt stand damit in `main`, und es brauchte den Nachzügler #60.

Der Unterschied zum Fall darüber ist der Punkt: Dort ging der Prüfer verloren,
hier hat er geliefert und niemand hat hingesehen. Ein grüner Haken sagt nichts
darüber, ob jemand den Befund gelesen hat — deshalb steht die Checkliste im
PR-Template auf «beantwortet oder behoben», nicht auf «Review gelaufen». Zwei
Minuten zwischen Befund und Merge sind zu wenig, um beides zu tun.

Dritter Weg, und der unangenehmste: Derselbe PR bekommt auf dieselbe Frage
verschiedene Antworten. Am 28.8.2026 auf PR #53, alles innerhalb von acht
Minuten:

| Zeit | Auslöser | Antwort |
|---|---|---|
| 18:43:41 | Draft → ready (18:43:37) | «To use Codex here, create an environment» |
| 18:46:52 | `@codex review` (18:43:51) | vollständiger Review, drei P2-Befunde |
| 18:51:30 | Kommentar (18:51:20) bzw. Push | «To use Codex here, create an environment» |

Fehlschlag, Erfolg, Fehlschlag — derselbe PR, dasselbe Repo, dasselbe Konto.
**Warum, ist offen**, und zwei Erklärungen sind mit diesen drei Zeilen
verträglich:

- **Der Auslöser entscheidet.** Der automatische Weg verlangt die Environment,
  der ausdrückliche Aufruf umgeht sie. Dann fehlt die Environment durchgehend,
  und nichts schwankt.
- **Die Prüfung selbst ist unstet.** Dann sagt der Weg nichts, und derselbe
  Aufruf kann mal so und mal anders ausgehen.

Die dritte Zeile könnte zwischen beiden entscheiden — aber genau bei ihr ist
der Auslöser nicht eindeutig (siehe unten). Was es bräuchte, ist ein Erfolg
**und** ein Fehlschlag auf demselben zweifelsfrei bestimmten Auslöser.

Am 29.8. kam eine Beobachtung dazu, die nahe herankommt. PR #60 wurde um
07:09:06 als **Draft** eröffnet, um 07:09:10 ging genau ein `@codex review`
hinaus, und darauf kamen zwei Antworten:

| Zeit | Antwort |
|---|---|
| 07:09:17 | «To use Codex here, create an environment for this repo» |
| 07:09:24 | Lauf startet, Auslöser laut Status-Kommentar «Manual request» |

Sieben bzw. vierzehn Sekunden nach demselben Aufruf, Fehlschlag und Erfolg.
**Zweifelsfrei ist es trotzdem nicht**, und zwar aus einem Grund, der in diesem
Abschnitt selbst steht: Dass ein Draft die automatischen Auslöser nicht anlaufen
lässt, ist eine Behauptung dieses Dokuments, keine hier gemessene Grösse. Gilt
sie nicht, kann die Environment-Meldung von der Eröffnung vier Sekunden zuvor
stammen, und es waren wieder zwei Auslöser.

Entscheiden liesse sich das mit einem Draft-PR **ohne** jeden Aufruf: Kommt dort
eine Environment-Meldung, stammt sie von der Eröffnung und diese Beobachtung
zerfällt. Bleibt es still, trägt sie. Wer den Abschnitt fortschreibt, hat hier
einen Versuch, der drei Minuten kostet.

Belastbar ist deshalb nur, was ohne die Ursache auskommt:

- **Auf eine Environment-Meldung kann Minuten später ein vollständiger Review
  folgen** (18:43:41 → 18:46:52, derselbe PR), **und auf den Review wieder die
  Meldung** (→ 18:51:30).
- Mehr als die Abfolge steht dort nicht. Ob sich in den drei bzw. fünf Minuten
  dazwischen etwas an den Voraussetzungen geändert hat, weiss niemand — wäre
  die Environment um 18:45 angelegt worden, hätte die erste Meldung den
  damaligen Zustand korrekt beschrieben. Die Beobachtung trägt, ihre Deutung
  nicht.
- **Erneut aufrufen ist billig.** Ein ausdrücklicher Aufruf kostet einen
  Kommentar und zwei bis drei Minuten; nach einer Environment-Meldung lohnt er
  sich — unabhängig davon, warum sie kam.

Dieser Absatz stand vor seinem Merge dreimal falsch da, und jede Fassung
scheiterte an derselben Sache: Sie erklärte mehr, als sie gemessen hatte.

1. «Der Auslöser feuert nicht, Zeit und Environment sind ausgeschlossen.» —
   Der Zeit-Ausschluss verglich einen manuellen Lauf mit einem automatischen
   vierzehn Stunden früher; der Environment-Ausschluss stützte sich auf einen
   Lauf, dem sieben Minuten später die Environment-Meldung folgte.
2. «Der manuelle Weg trägt, wo der automatische scheitert.» — Vier Minuten
   später kam die Meldung auf einen Aufruf, der manuell ausgesehen hat.
3. «Die Prüfung ist unstet, der Weg ist nicht die Variable.» — Beides war zu
   viel. Aus «beide Wege haben schon geliefert und schon versagt» folgt nur,
   dass keiner von beiden immer funktioniert; über den Einfluss des Wegs sagt
   es nichts. Bei 1 Fehlschlag von 2 gegen 1 von 4 wäre ein Unterschied mit
   diesen Zahlen ohnehin nicht zu sehen — und der eine «manuelle» Fehlschlag
   ist nicht einmal zweifelsfrei manuell.

Die vierte Fassung nennt deshalb keine Ursache mehr, sondern die Beobachtung
und das, was sie entscheiden würde. Wer den Abschnitt fortschreibt: Eine
Erklärung gehört erst hinein, wenn ein Erfolg und ein Fehlschlag auf demselben
eindeutigen Auslöser vorliegen.

Was beide Wege betrifft, ist belegt und mehr nicht: **Beide können
funktionieren.** Automatisch hat geliefert (#45 um 08:55:43, ohne jeden
vorherigen Kommentar auf dem PR), von Hand ebenfalls (#45, #51, #53).

**Vermutlich eine Fussangel:** Die dritte Zeile oben kam zehn Sekunden nach
einem Kommentar, der `@codex review` in einer Tabelle bloss *zitierte*, und
siebzig Sekunden nach einem Push. Der Abstand spricht für den Kommentar — die
beiden anderen Läufe antworteten nach vier und zehn Sekunden —, aber
auseinanderhalten lässt es sich mit einer Beobachtung nicht. Wer beim
Beantworten eines Reviews aus ihm zitiert, sollte damit rechnen, einen neuen
Lauf auszulösen.

Zu PR #51 (ready 04:35:22, gemergt 04:44:00, nichts in 8 min 38 s; manuell um
18:33:48 → Befundlos-Meldung um 18:36:45) bleibt nach alledem nur die nackte
Beobachtung. Warum dort nichts kam, ist offen, und zwei Dinge machen es
unentscheidbar: Ein manueller Lauf mit knapp drei Minuten begrenzt nicht, wie
lange der automatische Weg vierzehn Stunden früher gebraucht hätte, und
«nichts kam an» ist von aussen nicht von «nichts wurde ausgelöst» zu trennen.

Was hier zwei Fassungen lang als dritter Grund stand — der Merge beende den PR
und töte einen laufenden Job —, ist als allgemeine Regel widerlegt. Auf #60
startete am 29.8. um 07:11:27 ein Lauf, um 07:11:53 wurde gemergt, und um
07:12:44 stand er auf «Completed», gefolgt von der 👍. Ein Lauf kann einen
Merge also überleben. Ob er es immer tut, ist damit nicht gesagt; für #51
taugt er jedenfalls nicht mehr als Erklärung.

Der Vorgänger #50 (ready 04:26:01, gemergt 04:26:04) gehört dagegen in die
Schublade darüber: drei Sekunden erklären ihn vollständig.

Und #45 gegen #46 taugt weniger, als es aussieht. Beide tragen denselben
Sekundenstempel bei der Eröffnung (08:53:57), #45 bekam um 08:55:43 seinen
automatischen Review, #46 bis zum Merge fünf Stunden später gar nichts. Daraus
«der Auslöser fällt pro PR aus» zu folgern geht nicht: Für #46 ist nicht
belegt, dass er zum fraglichen Zeitpunkt überhaupt ready war.

Praktisch zählt zweierlei:

**`@codex review` von Hand ist der Weg, den man selbst in der Hand hat.**
Dreimal geliefert und dabei erstaunlich gleichmässig — #45 in 2 min 31 s, #51
in 2 min 57 s, #53 in 3 min 1 s. Einmal gescheitert, siehe oben. Nach einem
Fehlschlag lohnt der zweite Versuch.

Wer den Aufruf absetzt, wartet diese drei Minuten ab. Codex quittiert ihn
vorher mit einer 👀-Reaktion **auf dem auslösenden Kommentar** — das ist die
Empfangsbestätigung, nicht das Ergebnis. Wer nach einer Minute nachsieht und
nichts findet, hält einen laufenden Review für einen ausgefallenen; genau das
ist beim Schreiben dieses Absatzes passiert. Und sie bleibt nicht liegen: Auf
#53 stand die 👀 auf dem auslösenden Kommentar, solange der Lauf lief, und war
weg, nachdem der Review stand. Als nachträglicher Nachweis, dass je einer lief,
taugt sie damit auch nicht.

Die 👍, die der Infokasten verspricht, **gibt es** — nur nicht verlässlich. Am
29.8. trugen #59 und #60 nach ihrem befundlosen Lauf je `reactions: {"+1": 1}`
auf dem PR, und die 👀 war dort wieder verschwunden. In sechs Repos am 23.8.
und auf #51 am 28.8. kam sie dagegen nicht (`reactions.total_count: 0`). Zwei
Fassungen dieses Abschnitts führten sie als Tatsache, eine erklärte sie für
widerlegt; beides ging über die Beobachtungen hinaus.

Und selbst wo sie steht, belegt sie weniger, als sie verspricht: Auf #59 steht
die 👍 an einem PR, der eineinhalb Stunden zuvor einen zutreffenden P2-Befund
bekommen hatte. Sie folgt einem Lauf, nicht dem PR. Wer einen Beleg braucht,
liest die Kommentartexte — die Reaktion taugt dafür in keiner Richtung.

Die 👀 sitzt an anderer Stelle und bedeutet etwas anderes: gesehen, nicht
geprüft.

**Er wirkt auch auf einem bereits gemergten PR.** #45 war beim manuellen
Aufruf seit 70 Minuten gemergt, #51 seit knapp 14 Stunden — beide bekamen
ihren Review. Ein zu früh gemergter PR ist also nicht verloren; der Review
lässt sich nachholen, solange jemand merkt, dass er fehlt.

Geprüft wird dann allerdings der **Merge-Commit**, nicht der Branch-Stand: Der
Aufruf auf dem gemergten #59 am 29.8. um 07:07:24 lieferte um 07:09:27 einen
Review von `789e901`. Für die Frage «ist das, was jetzt in `main` steht, in
Ordnung?» ist das genau richtig; wer dagegen einen inzwischen gepushten
Folge-Commit geprüft haben will, bekommt ihn hier nicht.

Und der Umkehrschluss, der hier am teuersten ist: **Bleibt es nach dem
automatischen Auslöser still, sagt das nichts über die Ursache** — nicht
Kontingent, nicht Environment, nicht «der Auslöser ist ausgefallen», und schon
gar nicht «der Text ist sauber». Belegt ist allein, dass am PR kein Review
angekommen ist. Die Abhilfe ist dieselbe: `@codex review` absetzen, drei
Minuten warten, und bei einer Environment-Meldung noch einmal.

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

### Verfahren für Doku-PRs

Als Draft öffnen, den Review von Hand anfordern, Befunde einarbeiten — und
**nach jeder Korrekturrunde erneut anfordern**, auf dem neuen Head. Auf ready
geht es, wenn ein Lauf auf dem aktuellen Head nichts mehr findet.

Das ist ein Abbruchkriterium, kein Gütesiegel. Ein befundloser Lauf sagt nach
dem Absatz oben etwas über den Lauf — derselbe Text kann in der nächsten Runde
wieder einen Befund tragen, und irgendwo muss die Schleife enden. Sie endet
also aus praktischen Gründen, nicht weil der Stand bewiesen sauber wäre. Was
sie liefert, ist ein Ergebnis für jede Fassung, die gemergt wird, und das ist
der ganze Unterschied zu keinem.

Die Schleife ergänzt die Reihenfolge, sie ersetzt sie nicht. Wer nach dem
Einarbeiten umschaltet, statt erneut anzufordern, hat genau den Stand
ungeprüft, den er mergt: Der Review lief auf der Fassung davor, im
Draft-Zustand läuft kein automatischer nach, und nach dem Umschalten bleiben
erfahrungsgemäss Sekunden. Von den Fassungen dieses Abschnitts sind am 28.8.
zwei ungeprüft in `main` gelandet — **beide waren die Korrektur einer geprüften
Fassung.**

**Der ausdrückliche Aufruf läuft auch auf einem Draft an** (#55, 2 min 14 s).
Auf ready umzuschalten ist dafür nicht nötig — nur die automatischen Auslöser
brauchen es. Das ist der Grund, warum die Reihenfolge überhaupt möglich ist.

**Was der Draft leistet, ist genau eine Sache: Vor dem Merge muss jemand erst
umschalten.** Mehr nicht. Am 28.8. lagen bei vier PRs zwischen «ready» und
Merge drei bis vier Sekunden, bei rund drei Minuten Vorlauf — aber diese
Messung beginnt erst nach dem Umschalten und sagt deshalb nichts darüber, ob
ein als Draft gestarteter PR seltener zu früh zugeht. Warum es so schnell ging,
ist ebenfalls nicht gemessen: Nachlässigkeit, Bedienführung oder etwas Drittes
sind von aussen nicht zu unterscheiden.

**Der erste Einsatz hat den Fehler nicht verhindert.** PR #57, der dieses
Verfahren einträgt, wurde nach dem manuellen Aufruf zu früh auf ready gesetzt
und 2 min 30 s später gemergt — vor seinem Review. Das gehört hierher: Wer das
Verfahren übernimmt, soll wissen, dass es beim ersten Mal nicht eingehalten
wurde und woran es lag — am Umschalten, nicht am Aufruf.

Warum sich das trotzdem lohnt, hat mit den Befunden nichts zu tun. Von den
Fassungen dieses Abschnitts trugen die geprüften Läufe drei, zwei und einen
P2-Befund — daraus folgt aber nichts über die Qualität der ungeprüften. Der
Abschnitt oben hält selbst fest, dass derselbe Text in 42 Läufen Befunde **und**
sechs befundlose Ergebnisse erzeugte; ein Ergebnis sagt etwas über den Lauf.
Der Grund ist schlichter und stärker: **Bei einer ungeprüften Fassung liegt
überhaupt kein Ergebnis vor.** Nicht ein schlechtes, sondern keines.

Der Reihenfolge wegen: Der Review gehört vor den Merge, weil ein Befund danach
einen zweiten PR braucht. Am 28.8. kam einer 28 Sekunden vor dem Merge — die
Behebung landete deshalb in einem Nachzügler.

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
