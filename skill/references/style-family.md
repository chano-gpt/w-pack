# Style Family

Resolve STYLE references as one global core plus bounded support adapters. Do not average several equal styles.

## STYLE_CORE

Use exactly one `STYLE_CORE` when style authority exists. It controls the global visual grammar:

- visual medium and rendering language
- degree of realism
- shape abstraction
- contour and edge grammar
- value and shading structure
- color behavior
- texture and surface treatment
- background rendering
- hair rendering grammar when visible

The following are core-only axes and must never be delegated to STYLE_SUPPORT: `visual_medium`, `degree_of_realism`, and `shape_abstraction`.

## STYLE_SUPPORT

Allow zero to two `STYLE_SUPPORT` references. Each support must declare bounded `support_domains` and may influence only those domains.

Typical support domains include color behavior, value structure, surface treatment, background rendering, edge treatment, or hair rendering grammar. A support source never becomes a second global style and never overrides a conflicting STYLE_CORE decision.

Prefer one support in ordinary first-pass use. Use two only when their domains are distinct and the five-reference total limit still holds.

## Manifest roles

For manifest schema v1.1, STYLE authorities may declare:

```json
{
  "role": "STYLE",
  "style_role": "CORE",
  "style_signature": ["..."],
  "anti_drift_signature": ["..."]
}
```

A support authority declares `style_role: "SUPPORT"` plus non-empty `support_domains`.

A single legacy STYLE without `style_role` may be inferred as CORE. Multiple active STYLE references must resolve explicitly to exactly one CORE and no more than two SUPPORT sources.

## Inline behavior

By default, any explicit current-chat STYLE replaces the Project style family for that request. Set `combine_style_sources=true` only when the user explicitly wants styles combined. In combine mode, inline STYLE references must be role-bounded so the resulting family still has exactly one CORE.

## STYLE DNA

When direct visual binding is unavailable but the source is inspectable, derive high-specificity STYLE DNA rather than using broad labels. Capture:

- medium and mark-making
- edge width, taper, hardness, and hierarchy
- face, eye, and hair abstraction
- shape language
- shadow geometry and value bands
- highlight geometry
- palette relationships
- texture and material treatment
- background simplification and depth cues
- degree of realism
- anti-drift traits

For visible hair, include silhouette cleanliness, lock grouping, strand density, tip behavior, face-crossing wisps, and highlight granularity. Read `hair-rendering-policy.md` for the default fallback and audit rules.

## Recovery support selection

During `SINGLE_RESTYLE`, always use STYLE_CORE. Add at most one STYLE_SUPPORT, and only when its declared support domains intersect the audit `failure_axes`. Do not include unrelated support references merely because they were present in the first pass.
