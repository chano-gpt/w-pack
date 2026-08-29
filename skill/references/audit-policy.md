# Audit Policy

Review the generated candidate against the compiled request and active authority scopes.

## Required axes

1. Scene compliance — required subject, environment, framing, lighting, and exact text are present.
2. Authority fidelity — each active authority influenced only its permitted properties and important required traits were preserved.
3. Leakage — incidental identity, pose, objects, text, background, or composition from references did not leak into the result without authorization.
4. Structural quality — anatomy, perspective, object relationships, cropping, and scale are coherent enough for the requested use.
5. Freshness — a fresh run does not visibly inherit unrelated artifacts from a previous candidate.

## Verdicts

- `PASS`: no material defect requiring regeneration.
- `HOLD`: usable candidate but one or more material ambiguities should be surfaced to the user before another run.
- `FAIL`: clear violation of the brief or authority boundaries; regenerate only if the user's request still requires an image.

Do not burden the user with a verbose audit when the candidate passes. Surface only defects that materially affect the requested result.
