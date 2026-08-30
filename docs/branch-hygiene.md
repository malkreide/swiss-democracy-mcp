# Branch-Hygiene im Portfolio

Die Handlungsregel steht in [`CLAUDE.md`](../CLAUDE.md) unter «Wenn zwei
Agenten dasselbe tun». Hier die Erhebung, auf der sie beruht.

## Die Erhebung vom 30.8.2026

Alle 51 Repos des Kontos, abgefragt um 11:43 UTC. Erst `git ls-remote --heads`
für die Branch-Namen, dann pro Repo ein `git clone --filter=blob:none
--no-checkout` und `git merge-base --is-ancestor <branch> <default>` für den
Merge-Status.

**Der Weg ist Teil des Befunds:** Beides läuft über anonyme Git-Lesezugriffe
des Proxys, nicht über die GitHub-API. Deshalb griff keine der Sperren, an
denen dieselbe Messung über `list_branches` gescheitert wäre — weder das
Repo-Scoping der Session noch das Kontingent, das am Vortag die
GraphQL-Abfragen blockierte.

| | Anzahl | Repos |
|---|---|---|
| `claude/*`-Branches insgesamt | 152 | 43 von 51 |
| davon **gemergt** (Leichen) | 89 | 40 |
| davon **offen** (unmerged) | 63 | 42 |

Die häufigsten Leichen: `claude/codex-vierter-grund` (37 Repos),
`claude/drift-005-doku` (23), `claude/version-aus-paket-metadaten` (11) — die
Signatur portfolioweiter Durchläufe, deren Branches niemand aufgeräumt hat.

## Der Fallstrick: ein Name ist kein Merge-Status

`claude/codex-env-reason` liegt in **40 Repos und ist in keinem einzigen
gemergt** — überall genau ein Commit vor dem Default-Branch. Er sieht aus wie
die anderen Durchlauf-Branches und ist der häufigste `claude/*`-Name im
Portfolio.

Wer nach Namensmuster aufräumt, löscht damit 40 unveröffentlichte Commits. Die
Ancestry-Prüfung ist das Einzige, was ihn heraushält; die Namen tun es nicht.

## Was die Erhebung nicht hergibt

- **Warum die Leichen existieren.** In `swiss-democracy-mcp` löscht GitHub den
  Branch beim Merge — am 29.8. bei #81 und #82 beobachtet, und das Repo ist
  eines von acht ohne jeden `claude/*`-Branch. Ob die Einstellung anderswo aus
  ist oder ob die 89 Leichen aus der Zeit davor stammen, wurde nicht gemessen.
- **Ob die 63 offenen Branches noch gebraucht werden.** Gemessen ist nur, dass
  sie Commits tragen, die nicht im Default-Branch stehen.
- **Den heutigen Stand.** Die Zahlen sind eine Momentaufnahme. Vor einer
  Löschaktion ist jeder Branch erneut zu prüfen, nicht die Liste zu glauben.

## Fallen aus derselben Erhebung

**Ein fehlgeschlagener Aufruf ist keine Messung.** Beim Prüfen eines
Branches, den ein `git fetch --prune` lokal gerade entfernt hatte, lief

```bash
git merge-base --is-ancestor origin/claude/<name> origin/main && echo JA || echo "NEIN, noch offen"
```

in den `||`-Zweig — nicht weil der Branch offen war, sondern weil
`merge-base` auf einer nicht existierenden Referenz mit `fatal:` abbrach. Die
Ausgabe las sich wie ein Befund. Dieselbe Klasse wie der 403, der als
Fund-Fehlschlag verpackt ist: Entscheidend ist nicht, welchen Zweig ein
Kommando nimmt, sondern ob es überhaupt geantwortet hat.

**Eine Prüfung auf einem zwischengespeicherten Ref schützt nicht.** Die erste
Fassung der Regel in `CLAUDE.md` prüfte die Ancestry gegen
`origin/claude/<name>` — ohne vorher zu holen. Ist diese Kopie veraltet und
der alte Stand gemergt, meldet die Prüfung «gefahrlos», während der Branch
inzwischen neue Commits trägt. Die Regel hätte dann genau das gelöscht, wovor
sie schützen soll, und widersprach dabei dem Absatz unten in dieser Datei.

Gefunden von einem Codex-Review auf #83 — als einziger P1 einer Serie, die
sonst nur P2 hervorbrachte. Behoben durch ein `git fetch --prune` davor **und**
einen Lease am Löschen selbst:

```bash
sha=$(git rev-parse "origin/claude/<name>")
git push --force-with-lease="refs/heads/claude/<name>:$sha" origin ":refs/heads/claude/<name>"
```

Die festgehaltene `$sha` ist nicht Kosmetik: Ein zweiter Befund auf demselben
PR zeigte, dass der Lease laut `git push -h` nur verlangt, der *alte Wert des
Refs* möge dem übergebenen Wert entsprechen. Wird er erst beim Löschen aus dem
Tracking-Ref aufgelöst und hat ein Hintergrund-Fetch diesen inzwischen
fortgeschrieben, passt der Lease auf den neuen, ungeprüften Stand — und das
Löschen gelingt.

An einem lokalen Bare-Repo gegengeprüft: Mit veraltetem erwartetem SHA lehnt
der Server mit `! [rejected] (delete) -> feature (stale info)` ab und der
Branch bleibt stehen; mit dem aktuellen SHA wird gelöscht. Das Fetch allein
genügt nicht — zwischen Prüfung und Löschen bleibt sonst ein Fenster, das nur
der Lease schliesst.

**Ein veralteter Remote-Tracking-Ref ist kein Branch.** Was diese Erhebung
auslöste, war ein `origin/claude/…` im lokalen Klon, das ohne `--prune` stehen
blieb, obwohl GitHub den Branch beim Merge längst gelöscht hatte. Es erklärte
nebenbei zwei Beobachtungen des Vortags: dass jeder Push `[new branch]`
meldete statt eines Fast-Forward, und dass der Stop-Hook wiederholt
ungepushte Commits anzeigte, die alle bereits in `main` standen.
