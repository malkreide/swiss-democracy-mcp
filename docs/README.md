# Documentation index

Two kinds of documents live here. They have different audiences, and mixing
them up wastes the reader's time.

## Product documentation (English)

For people who run, deploy or contribute to the server. Linked from the
READMEs and from `SECURITY.md`.

| File | Contents |
|---|---|
| [`roadmap.md`](roadmap.md) | Phased architecture; the server is Phase 1 (audit OPS-003) |
| [`security.md`](security.md) | Transport, binding, egress allow-list, CORS |
| [`secret-management.md`](secret-management.md) | How the optional SRGSSR credentials are handled |

`assets/` holds images used by the READMEs.

## Working notes (German)

For whoever maintains this repository — human or agent. Not part of the
product documentation; the rules themselves live in
[`CLAUDE.md`](../CLAUDE.md) at the repository root, and these files carry the
evidence behind them.

| File | Contents |
|---|---|
| [`codex-reviews.md`](codex-reviews.md) | What was observed about the Codex review bot: the forms a run takes, why it stays silent, and the claims that turned out to be wrong |

They are in German because `CLAUDE.md` is, and because they are read together
with it.
