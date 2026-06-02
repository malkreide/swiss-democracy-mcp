## Finding: ARCH-002

**Severity:** medium
**Status:** Open
**Check:** ARCH-002  |  **Result:** partial
**Server:** swiss-democracy-mcp

### Observed Behavior
Beschreibungen sind prosaisch und ausführlich, enthalten aber keine maschinell trennscharfen Use-Case-Tags.

### Evidence
- Tool-Descriptions sind ausführlich (>100 Zeichen Median), mit Args/Returns
- Differenzierung ähnlicher Tools (search vs detail vs cantonal) klar

### Gaps
- Keine strukturierten `<use_case>`/`<important_notes>`/`<example>`-Tags (0 Treffer in src/)

### Expected Behavior
≥80% der Tools mit `<use_case>`-Tag plus Caveats in `<important_notes>`.

### Remediation
Pro Tool die Description um `<use_case>`/`<important_notes>`-Tags ergänzen (siehe ARCH-002 Pass-Pattern).

### Effort
S — pro Tool 5–10 Min.

