# W-Pack

### ChatGPT용 참조 제어 이미지 생성 하네스

[English](./README.md) · **한국어** · [日本語](./README.ja.md) · [简体中文](./README.zh-CN.md) · [繁體中文](./README.zh-TW.md)

W-Pack v0.5.1은 ChatGPT Web/Projects에서 반복 사용하는 이미지 소스를 **권한(authority)**, **실제 전달 상태(transport)**, **스타일 복구(recovery)**로 분리해 제어합니다.

## v0.5.1 핵심 변경

- Project에 파일이 있다는 이유만으로 이미지 모델에 시각 참조가 전달됐다고 가정하지 않습니다.
- STYLE은 `STYLE_CORE` 1개 + `STYLE_SUPPORT` 최대 2개 구조로 처리합니다.
- 직접 시각 바인딩이 불확실하면 `style_signature` / `anti_drift_signature` 기반 STYLE DNA를 사용할 수 있습니다.
- 머리카락을 별도의 `hair_rendering_grammar` 스타일 축으로 감사합니다.
- 별도 소스 지시가 없으면 `CLEAN_MASS`를 사용해 과도한 잔머리, 반복적으로 갈라지는 끝, 얼굴을 가로지르는 무작위 가닥, 실처럼 번쩍이는 가닥별 하이라이트를 억제합니다.
- 구조는 성공했지만 스타일만 실패한 경우에만 1회의 `SINGLE_RESTYLE`을 허용합니다.

## 기본 흐름

```text
Project / current-chat 참조
          ↓
      bounded role
          ↓
   transport 상태 확인
          ↓
 STYLE_CORE + SUPPORT 해석
          ↓
       FRESH 생성
          ↓
   구조 / 스타일 감사
          ↓
 필요할 때 SINGLE_RESTYLE 1회
```

## STYLE family

`STYLE_CORE`는 전체 이미지의 visual grammar를 담당합니다.

- visual medium / rendering language
- degree of realism
- shape abstraction
- contour / edge grammar
- value / shading structure
- color behavior
- texture / surface treatment
- background rendering
- visible hair rendering grammar

`STYLE_SUPPORT`는 선언된 support domain만 보조합니다. `visual_medium`, `degree_of_realism`, `shape_abstraction`은 CORE 전용 축이며 SUPPORT가 덮어쓸 수 없습니다.

## 머리카락 렌더링

기본 `CLEAN_MASS` 순서:

```text
전체 실루엣
  → 큰 머리 덩어리/락
  → 내부 질감
  → 최소한의 미세 가닥
```

깨끗한 외곽 실루엣, 묶여 있는 끝선, 중력에 맞는 흐름, lock 단위 하이라이트를 우선합니다. 다만 소스가 의도적으로 곱슬, 부스스함, 젖은 머리, 바람에 날리는 머리, strand-heavy 표현을 사용하면 소스가 우선합니다.

## Reference transport

W-Pack은 Project source 선택과 실제 이미지 모델 전달을 별개로 봅니다.

- `VISUAL_BOUND` — 직접 시각 바인딩 확인
- `VISUAL_INPUT_EXPECTED` — 현재 채팅 이미지 입력 예정, 바인딩 미확인
- `PROJECT_CONTEXT_ONLY` — ChatGPT는 소스를 볼 수 있으나 이미지 모델 직접 전달 미확인
- `TEXT_PROFILE_ONLY` — 텍스트 프로필만 사용 가능
- `UNVERIFIED_PROJECT_SOURCE` — Project 소스 전달 상태 미확인
- `UNAVAILABLE` — 사용할 수 있는 참조 없음

텍스트 fallback은 직접 시각 참조와 동일하다고 표현하지 않습니다.

## 1회 스타일 복구

자동 복구 조건:

1. 원래 요청이 `FRESH`
2. 구조 PASS
3. 스타일 FAIL
4. STYLE_CORE가 정확히 1개
5. STYLE_CORE가 `VISUAL_BOUND`이거나 usable STYLE DNA 보유

복구에는 다음만 사용합니다.

```text
STRUCTURE_EDIT_TARGET
+ STYLE_CORE
+ 실패 축과 관련된 STYLE_SUPPORT 최대 1개
```

재귀 restyle과 자동 3차 생성은 금지합니다.

## 설치

1. `skill/` 또는 패키징된 `skill.zip`을 설치합니다.
2. Project에 재사용할 참조 이미지를 넣습니다.
3. `project/PROJECT_INSTRUCTIONS.md`를 Project instructions에 적용합니다.
4. `project/AUTHORITY_MANIFEST.example.json`을 기준으로 DEFAULT profile을 구성합니다.
5. 자연어로 이미지 생성 요청을 합니다.

자세한 설정은 [`QUICKSTART.md`](./QUICKSTART.md)를 참고합니다.

## 검증

```bash
python3 skill/scripts/self_test.py
```

정상 결과:

```text
W-Pack self-test: PASS
```

현재 버전: **`WPACK_v0.5.1-chat-native`**
