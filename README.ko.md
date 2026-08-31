# W-Pack

### ChatGPT용 Project-source-first 이미지 생성 하네스

[English](./README.md) · **한국어** · [日本語](./README.ja.md) · [简体中文](./README.zh-CN.md) · [繁體中文](./README.zh-TW.md)

W-Pack v0.4는 ChatGPT Web/Projects 환경에서 Z-Pack의 핵심 원리인 **bounded authority, fresh generation, fail-closed reference control, style fidelity**를 채팅 방식에 맞게 적용합니다.

## v0.4 핵심 변경

- Project `DEFAULT` 소스를 매 요청마다 자동 사용합니다.
- 하나의 STYLE 소스를 내부적으로 `STYLE_CORE`로 사용합니다.
- STYLE_CORE의 화풍, 표현 매체, 실사도, 윤곽선, 형태 추상화, 명암/색/질감 문법을 강하게 유지합니다.
- 첫 생성은 항상 1회 FRESH로 시작합니다.
- **구조는 성공했지만 스타일만 실패한 경우에만** 1회의 style-only restyle을 수행할 수 있습니다.
- restyle을 연속 반복하지 않으며 자동 3차 생성도 하지 않습니다.
- 채팅 첨부 이미지는 기본 소스가 아니라 임시 override/add-on입니다.

## 기본 흐름

```text
Project DEFAULT 소스
        ↓
     FRESH 생성
        ↓
  구조 / 스타일 감사
     /          \
  통과        스타일 실패
   ↓              ↓
 종료       SINGLE RESTYLE
                  ↓
              최종 감사 후 종료
```

2단계는 기본값이 아닙니다. 첫 이미지의 인물, 포즈, 구도, 장면은 잘 나왔지만 화풍이 STYLE_CORE에서 크게 벗어난 경우에만 사용합니다.

## STYLE_CORE

STYLE_CORE는 전체 이미지의 visual grammar를 담당합니다.

- visual medium / rendering domain
- 실사도와 stylization level
- 윤곽선과 edge 처리
- 형태와 얼굴 특징의 추상화 방식
- 명암과 value 구조
- 색 사용 방식
- 질감과 표면 표현
- 배경 단순화/렌더링 방식

`85mm`, `망원`, `Canon`, `low angle`, `depth of field` 같은 표현은 렌즈/구도/광학적 특성으로 처리합니다. STYLE_CORE가 비실사 화풍이면 이런 표현만으로 실사 사진으로 바꾸지 않습니다.

## 1회 스타일 복구

FRESH 결과에서:

- 구조 PASS
- 스타일 FAIL
- STYLE_CORE 1개 존재

조건이 모두 맞을 때만 복구합니다.

복구 단계에는 두 이미지 역할만 사용합니다.

1. 방금 생성한 이미지 = `STRUCTURE_EDIT_TARGET` — 내용·구조만 담당
2. STYLE_CORE = 유일한 스타일 authority

인물 정체성, 포즈, 구도, 카메라, 공간 관계, 물체 수/접촉, 장면 조건, 텍스트는 보존하고 렌더링 스타일만 변경합니다.

구조 자체가 실패한 이미지는 restyle로 고치지 않습니다. 다음 재시도는 다시 FRESH부터 시작해야 합니다.

## 설치 및 Project 설정

1. `skill.zip`을 ChatGPT Skills에 업로드합니다.
2. Project에 반복 사용할 소스 이미지를 넣습니다.
3. `project/PROJECT_INSTRUCTIONS.md`를 Project instructions에 적용합니다.
4. `project/AUTHORITY_MANIFEST.example.json`을 기준으로 `DEFAULT` profile을 정의합니다.
5. 일반적으로 `DEFAULT`에는 STYLE 하나를 두어 STYLE_CORE로 사용합니다.

이후에는 매 프롬프트마다 "소스 참고해서"라고 쓰지 않아도 됩니다.

## 검증

```bash
python3 skill/scripts/self_test.py
```

정상 결과:

```text
W-Pack self-test: PASS
```

현재 버전: `WPACK_v0.4.0-chat-native`
