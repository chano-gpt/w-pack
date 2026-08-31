# Audit Policy

Review the generated candidate against the compiled request and active authority scopes.

## Required axes

1. Scene compliance: required subject, environment, framing, lighting, and exact text are present.
2. Project-source fidelity: active default Project authorities visibly influence the properties they control.
3. Style-medium fidelity: when STYLE is active, the output preserves the reference medium, stylization level, rendering language, and degree of realism unless the user explicitly requested a medium change.
4. Leakage: incidental identity, pose, objects, text, background, or composition from references did not leak outside authorized roles.
5. Structural quality: anatomy, perspective, object relationships, cropping, and scale are coherent enough for the requested use.
6. Freshness: a fresh run does not inherit unrelated artifacts from a previous candidate.

Treat unintended conversion of a stylized STYLE reference into generic photorealism as a material failure.

Do not burden the user with a verbose audit when the candidate passes. Surface only defects that materially affect the requested result.
