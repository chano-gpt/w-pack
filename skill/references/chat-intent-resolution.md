# Chat Intent Resolution

Use conversational language as the primary interface. Do not force users to write authority IDs, JSON, or mode names when their intent is already clear.

## Mode resolution

Choose `FRESH` for requests such as:

- make/create/generate a new image
- remake this concept from the references
- make another version without preserving a previous generated candidate
- 새로 만들어 / 새 이미지로 / 다시 생성

Choose `EDIT` when the user points to an existing target and asks to preserve or alter it, including:

- 여기서 ~만 바꿔
- 이 이미지에서 ~ 수정
- 얼굴은 그대로
- 배경만 바꿔
- 이 후보를 유지하면서
- restyle/refine/continue this image

Within `EDIT`, use `MODIFY`, `RESTYLE`, or `RECOMPOSE` internally only when it helps preserve the right properties. Never require the user to name the subtype.

## Authority cue mapping

Map explicit language to authority roles:

| User intent | Authority |
| --- | --- |
| 이 느낌으로 / 이 스타일로 / 색감 참고 | STYLE |
| 이 사람 그대로 / 얼굴 유지 / 같은 캐릭터 | CHARACTER |
| 이 포즈로 / 자세 참고 | POSE |
| 이 구도로 / 이 배치처럼 / 프레이밍 참고 | COMPOSITION |
| 이 비율로 / 크기 관계 참고 | PROPORTION |
| 이 옷 그대로 / 이 제품 참고 / 소품 유지 | ITEM |

Equivalent language in other languages should be treated the same way.

## Ambiguous reference language

If the user says only "참고해서", "이거 참고", "소스 참고해서", or equivalent:

1. Use an explicitly configured Project source profile if the phrase clearly requests Project sources.
2. If there is one current-chat image and surrounding language makes the intended influence clear, assign only that influence.
3. If multiple images exist and the intended roles cannot be separated without guessing, ask one concise question only if the ambiguity materially changes the output.
4. Never infer unrestricted influence from the entire reference image.

## Inline references

A current-conversation image can be used without a manifest. Create an ephemeral internal authority ID such as `INLINE_STYLE_01` or `INLINE_COMPOSITION_01` and set `source` to `INLINE_AUTHORITY`.

Do not claim an inline reference exists unless a usable image is actually present in the conversation.

## Editing precedence

When a user says both "그대로" and asks for a change, preserve the named properties and change only the requested properties. Example:

"얼굴은 그대로 하고 옷만 바꿔" means:

- target mode: EDIT / MODIFY
- preserve: identity, facial features, hair unless contradicted
- change: wardrobe
- do not silently alter background, framing, or style
