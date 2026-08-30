<p align="center">
  <img src="./assets/w-pack-hero.webp" alt="W-Pack — ChatGPT용 참조 제어 이미지 생성" width="100%" />
</p>

<div align="center">

# W-Pack

### ChatGPT를 위한 Reference-bounded 이미지 생성

**참조 이미지는 자연스럽게 활용하고, 영향 범위는 명확하게 제한합니다.**

[English](./README.md) · **한국어** · [日本語](./README.ja.md) · [简体中文](./README.zh-CN.md) · [繁體中文](./README.zh-TW.md) · [Español](./README.es.md) · [Português (Brasil)](./README.pt-BR.md) · [Français](./README.fr.md) · [Deutsch](./README.de.md)

</div>

---

W-Pack은 **ChatGPT Web, ChatGPT Projects, ChatGPT Skills**에서 이미지 생성과 편집 시 참조 이미지의 영향 범위를 제어하는 chat-native 레이어입니다.

일반적인 멀티 레퍼런스 요청에서는 스타일 이미지의 인물, 구도, 배경 같은 요소가 의도치 않게 섞일 수 있습니다. W-Pack은 각 참조 이미지에 `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION`, `ITEM` 중 하나의 권한을 부여해 이런 누출을 줄입니다.

```text
첫 번째 이미지는 느낌만 참고해.
두 번째 이미지의 인물은 그대로 유지해.
세 번째 이미지 구도로 만들어.
이 이미지에서 얼굴과 구도는 유지하고 옷만 바꿔.
```

사용자는 JSON이나 manifest ID를 직접 작성할 필요가 없습니다.

## 핵심 기능

- **자연어 기반 참조 제어** — “이 느낌으로”, “이 사람 그대로”, “이 포즈로”, “이 구도로” 같은 표현을 해석합니다.
- **Inline reference** — 현재 채팅에 첨부한 이미지는 manifest 없이 바로 사용할 수 있습니다.
- **6개 Authority role** — `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION`, `ITEM`.
- **FRESH / EDIT 구분** — 새 이미지 생성과 기존 이미지 수정 요청을 다르게 처리합니다.
- **Project source profile** — 반복적으로 사용하는 참조 세트를 짧은 요청으로 활성화할 수 있습니다.
- **검증 스크립트** — 권한 충돌, 중복 참조, 잘못된 편집 요청 등을 사전에 검사합니다.

## 빠른 시작

1. [`skill/`](./skill) 폴더를 ChatGPT Skill로 설치하거나 업로드합니다.
2. 이미지 하나 이상을 첨부합니다.
3. 각 이미지가 무엇을 담당해야 하는지 자연어로 말합니다.

```text
@W-Pack

첫 번째 이미지는 스타일만 참고.
두 번째 이미지의 인물은 그대로 유지.
세 번째 이미지 구도로 새 이미지 만들어.

배경은 노을진 실내, 부드러운 자연광.
4:5 세로 비율.
```

API Key, 로컬 CLI, 별도 이미지 API는 필요하지 않습니다.

## Authority model

| Role | 제어하는 요소 | 기본적으로 제어하지 않는 요소 |
| --- | --- | --- |
| `STYLE` | 색감, 질감, 조명 언어, 렌더링, 그래픽 처리 | 인물 정체성, 포즈, 정확한 구도, 제품 정체성 |
| `CHARACTER` | 인물 정체성, 얼굴, 헤어, 안정적인 외형 | 배경, 조명, 레이아웃, 관련 없는 오브젝트 |
| `POSE` | 신체 배치, 제스처, 자세, 방향 | 인물 정체성, 의상, 환경, 스타일 |
| `COMPOSITION` | 프레이밍, 크롭, 카메라 각도, 배치, 여백 | 인물 정체성, 의상, 제품 정체성, 전체 스타일 |
| `PROPORTION` | 신체/오브젝트 비율과 상대적 크기 | 인물 정체성, 세부 포즈, 스타일 |
| `ITEM` | 제품/오브젝트 정체성, 실루엣, 구조 | 인물 정체성, 환경, 전체 스타일 |

핵심 규칙은 하나입니다.

> **보인다고 해서 허용된 것은 아닙니다.**

참조 이미지에 우연히 포함된 요소는 해당 Authority가 허용하지 않는 한 결과물에 영향을 주지 않아야 합니다.

## FRESH와 EDIT

### `FRESH`
새 이미지를 만들거나 참조를 기반으로 다시 생성할 때 사용합니다. 이전 생성물은 자동으로 재사용되지 않습니다.

### `EDIT`
기존 이미지의 일부를 수정·유지·재스타일·재구성할 때 사용합니다. 내부적으로 `MODIFY`, `RESTYLE`, `RECOMPOSE`로 분류될 수 있지만 사용자가 직접 지정할 필요는 없습니다.

## ChatGPT Project 사용

반복해서 사용하는 참조 이미지가 있다면 ChatGPT Project에 저장하고 [`project/PROJECT_INSTRUCTIONS.md`](./project/PROJECT_INSTRUCTIONS.md)를 Project instructions에 적용할 수 있습니다.

Project 파일은 존재한다고 자동 사용되지 않습니다. W-Pack은 현재 요청에 필요한 최소 참조만 선택합니다.

## 동작 흐름

```text
자연어 요청
  -> FRESH / EDIT 판별
  -> 참조 이미지와 Authority role 해석
  -> 선택적 Source Profile 적용
  -> 충돌 및 범위 검증
  -> scene / composition / lighting / text / preserve / avoid 컴파일
  -> ChatGPT 이미지 생성
  -> 결과 감사(audit)
```

한 번의 생성에 최대 5개의 참조 이미지를 사용하며, 가능한 최소 개수를 우선합니다.

## 검증

```bash
python3 skill/scripts/self_test.py
```

정상 결과:

```text
W-Pack self-test: PASS
```

## 현재 상태

현재 버전은 `WPACK_v0.3.0-chat-native`입니다. Inline reference, 자연어 Authority 해석, `COMPOSITION`, FRESH/EDIT, Project Source Profile, deterministic validation에 초점을 맞춘 ChatGPT Web용 마일스톤입니다.
