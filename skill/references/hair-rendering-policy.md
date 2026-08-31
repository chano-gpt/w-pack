# Hair Rendering Policy

Treat visible human hair as a dedicated rendering grammar, not as generic texture or a place to add decorative micro-detail.

## Authority order

Resolve hair behavior in this order:

1. Explicit user instruction about hairstyle or hair texture.
2. Directly bound CHARACTER or STYLE reference hair grammar.
3. Source-derived STYLE DNA or CHARACTER profile when the reference is inspectable but not visually bound.
4. `CLEAN_MASS` fallback when no usable hair grammar exists.

A reference may intentionally contain messy, frizzy, wet, windblown, braided, curly, or strand-heavy hair. Match that grammar when it is actually authoritative; do not sanitize it into the fallback.

## Default `CLEAN_MASS` grammar

Build hair from macro to micro:

1. Lock the overall hairstyle silhouette, parting, fringe/bang shape, volume, length, and gravity flow.
2. Divide the mass into a small number of coherent locks or ribbons that follow the hairstyle.
3. Add internal texture only after the large masses read correctly.
4. Keep micro-strands sparse, subordinate, and physically motivated.

Use a clean continuous outer silhouette. Prefer grouped tapered or grouped blunt ends over independently branching filaments. Keep the hairline integrated with the scalp and fringe rather than spawning isolated roots. Keep face-crossing strands rare unless the brief or source calls for them.

## Anti-signature controls

Suppress the common generic image-model hair signature unless the source explicitly requires it:

- dense flyaway halos around the entire silhouette
- forked or repeatedly split strand tips
- many equally sharp individual filaments
- random wisps crossing the forehead, cheeks, eyes, or mouth
- evenly distributed frizz that ignores gravity and hairstyle flow
- bright thread-like highlights tracing individual strands
- excessive strand separation that destroys the larger lock structure

Do not solve this by making hair plastic, helmet-like, or uniformly smooth. Preserve believable volume, overlap, softness, and local variation at the lock level.

## Highlight grammar

Prefer highlight shapes that belong to locks or clusters: broad ribbons, soft bands, or grouped specular regions consistent with the active style. Individual filament highlights are allowed only when the STYLE_CORE clearly uses them or the user asks for strand-level realism.

## Prompt handoff

When the final image instruction needs an explicit hair clause, use compact positive wording rather than dumping the full anti-signature list. A default clause is:

> Render hair as cohesive grouped locks with a clean continuous silhouette, grouped ends, natural gravity flow, broad lock-level highlights, and only a few subtle physically plausible flyaways.

Adapt that clause to the active STYLE_CORE. For stylized work, reduce micro-strands further. For photographic work, retain natural variation but keep it subordinate to the hairstyle's larger grouped structure.

## Audit and recovery

Audit `hair_rendering_grammar` independently from general texture/surface treatment. Check silhouette noise, strand density, tip behavior, highlight granularity, face-crossing wisps, and agreement with the active source.

Hair-only drift is high-salience. If structure is otherwise acceptable but the generated hair clearly falls back to the generic micro-strand/flyaway signature, allow `style_status=FAIL` even when fewer than three other style fingerprint axes fail.

During `SINGLE_RESTYLE`, preserve hairstyle geometry: identity, length, parting, bang shape, volume, direction, and major lock placement. Change only the rendering grammar: strand density, silhouette noise, tip branching, highlight granularity, and lock grouping.
