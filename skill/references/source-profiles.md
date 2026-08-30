# Source Profiles

Source profiles are optional Project-level shortcuts for recurring reference sets. They exist to support conversational requests such as "소스 참고해서 제작" without forcing the user to repeat authority IDs.

## Behavior

A profile maps a profile name to a bounded set of Project authorities. Example:

```json
{
  "DEFAULT": ["STYLE_CORE_01", "CHARACTER_01", "PROPORTION_01"]
}
```

Use a profile only when it is explicitly configured in the Project and the user's language requests Project/default sources. Do not invent a profile from nearby files or upload order.

## Precedence

1. Explicit per-request user instructions
2. Explicit inline authority assignments
3. Requested source profile
4. Manifest defaults

A profile never grants unrestricted influence. Every referenced authority remains bound to its own role and influence scope.

## Limits

- The final generation request still has a maximum of 5 references.
- Prefer fewer references when the user's request does not need every profile member.
- If a profile reference is missing, do not silently replace it with another Project image.
- Current-chat inline references may be combined with profile references when the total remains within the limit and roles do not conflict.
