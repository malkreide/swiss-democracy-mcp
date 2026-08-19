#!/usr/bin/env bash
#
# SessionStart-Hook: meldet, wie viele Commits der ausgecheckte Stand hinter
# origin/<default-branch> liegt. Schweigt, wenn nichts fehlt.
#
# GRUND: Ein veralteter Klon hat am 3.8.2026 zweimal eine rote CI erzeugt,
# deren Ursache nicht im Diff stand — die fehlenden Commits waren jeweils
# genau die, die das Gate einfuehrten, an dem der Branch scheiterte. Die
# Pruefung kostet eine Sekunde und ersetzt eine Fehlersuche in den falschen
# Dateien.
#
# OBERSTE REGEL: Dieser Hook blockiert die Session nie. Kein `set -e`, kein
# `set -o pipefail`, jeder Pfad endet in `exit 0`. Kein Netz, kein Remote,
# detached HEAD, flatterndes DNS — jeder dieser Faelle geht still durch. Ein
# Hook, der bei Netzproblemen die Arbeit anhaelt, wird nach dem zweiten Mal
# abgeschaltet und schuetzt danach gar nichts.
#
# Details und Stellschrauben: .claude/hooks/README.md

# Sekunden, die ein Netz-Kommando hoechstens dauern darf. Der Sessionstart
# soll nicht an einem haengenden Netz warten; lieber keine Meldung als eine
# spaete.
FETCH_TIMEOUT="${CLAUDE_STALENESS_TIMEOUT:-5}"

# Git darf unter keinen Umstaenden nach Zugangsdaten fragen: ein Prompt auf
# einem Hook ohne TTY blockiert genau so lange wie ein haengendes Netz.
export GIT_TERMINAL_PROMPT=0
export GIT_ASKPASS=/bin/true
export SSH_ASKPASS=/bin/true
export GIT_SSH_COMMAND="${GIT_SSH_COMMAND:-ssh -o BatchMode=yes -o ConnectTimeout=5}"

# Ein Kommando mit harter Zeitgrenze ausfuehren. stdout bleibt beim Aufrufer,
# damit die Ausgabe von `ls-remote` lesbar ist; nur stderr wird verworfen.
# `timeout` ist auf schlanken Images (und auf macOS ohne coreutils) nicht
# garantiert vorhanden, deshalb ein portabler Ersatz: Kommando in den
# Hintergrund, danach pollen und toeten.
run_limited() {
  if command -v timeout >/dev/null 2>&1; then
    timeout "$FETCH_TIMEOUT" "$@" 2>/dev/null
    return $?
  fi

  "$@" 2>/dev/null &
  pid=$!
  waited=0
  while kill -0 "$pid" 2>/dev/null; do
    if [ "$waited" -ge "$FETCH_TIMEOUT" ]; then
      kill -9 "$pid" 2>/dev/null
      wait "$pid" 2>/dev/null
      return 124
    fi
    sleep 1
    waited=$((waited + 1))
  done
  wait "$pid" 2>/dev/null
  return $?
}

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

# Kein Git-Repo -> nichts zu vergleichen.
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

# Kein Remote `origin` -> nichts zu vergleichen.
git remote get-url origin >/dev/null 2>&1 || exit 0

# Detached HEAD: kein Branch, der hinterherhinken koennte. Still durch.
git symbolic-ref --quiet HEAD >/dev/null 2>&1 || exit 0

# Default-Branch ermitteln, NICHT `main` annehmen: mindestens ein Repo im
# Portfolio nutzt `master` (openlex-mcp, swiss-courts-mcp, swisstopo-mcp), und
# genau diese Annahme hat schon einmal einen Branch 15 Commits alt werden
# lassen. Zuerst der lokale Zeiger (kostet kein Netz), sonst der Remote.
default_branch=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)
default_branch="${default_branch#origin/}"

if [ -z "$default_branch" ]; then
  default_branch=$(run_limited git ls-remote --symref origin HEAD |
    sed -n 's|^ref: refs/heads/\([^[:space:]]*\).*|\1|p' | head -n 1)
fi

# Nicht ermittelbar -> lieber schweigen als `main` raten.
[ -n "$default_branch" ] || exit 0

# Ab hier ist Netz im Spiel. Scheitert das fetch (offline, DNS, Auth, Timeout),
# endet der Hook still: eine Zahl aus einem veralteten Remote-Ref waere
# schlechter als keine Zahl.
run_limited git fetch --quiet origin "$default_branch" >/dev/null || exit 0

behind=$(git rev-list --count HEAD..FETCH_HEAD 2>/dev/null)

# Nur Ziffern akzeptieren; alles andere ist ein Fehlerfall und schweigt.
# Bei 0 schweigt der Hook ebenfalls — Ausgabe nur, wenn wirklich etwas fehlt.
case "$behind" in
  '' | *[!0-9]*) exit 0 ;;
  0) exit 0 ;;
esac

commit_wort="Commits"
[ "$behind" = "1" ] && commit_wort="Commit"

printf 'Klon-Aktualitaet: Der ausgecheckte Stand liegt %s %s hinter origin/%s.\n' \
  "$behind" "$commit_wort" "$default_branch"
printf 'Ein veralteter Klon erzeugt eine rote CI, deren Ursache nicht im Diff steht:\n'
printf 'die fehlenden Commits sind oft genau die, die das scheiternde Gate einfuehren.\n'
printf 'Aktualisieren mit: git merge origin/%s   (oder: git rebase origin/%s)\n' \
  "$default_branch" "$default_branch"

exit 0
