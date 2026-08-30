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

## Zwei Fallen aus derselben Erhebung

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

**Ein veralteter Remote-Tracking-Ref ist kein Branch.** Was diese Erhebung
auslöste, war ein `origin/claude/…` im lokalen Klon, das ohne `--prune` stehen
blieb, obwohl GitHub den Branch beim Merge längst gelöscht hatte. Es erklärte
nebenbei zwei Beobachtungen des Vortags: dass jeder Push `[new branch]`
meldete statt eines Fast-Forward, und dass der Stop-Hook wiederholt
ungepushte Commits anzeigte, die alle bereits in `main` standen.
