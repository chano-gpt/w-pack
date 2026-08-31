# W-Pack

### Controle de referências para geração de imagens no ChatGPT

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · **Português (Brasil)**

O W-Pack v0.5.1 separa a **autoridade** de uma referência (o que ela pode controlar) do **transporte** (se a imagem realmente chegou ao modelo de geração).

## v0.5.1

- Um arquivo existente no Project não é tratado automaticamente como `VISUAL_BOUND`.
- STYLE é resolvido como um `STYLE_CORE` e até dois `STYLE_SUPPORT` limitados.
- Quando o vínculo visual direto não pode ser confirmado, STYLE DNA pode ser usado por `style_signature` e `anti_drift_signature`.
- Cabelo passa a ser auditado como o eixo independente `hair_rendering_grammar`.
- O fallback `CLEAN_MASS` reduz halos de fios soltos, pontas repetidamente bifurcadas, fios aleatórios atravessando o rosto e highlights finos por fio quando a fonte não exige esse comportamento.
- Apenas um `SINGLE_RESTYLE` é permitido quando a estrutura passa e o estilo falha.

## Recuperação

A recuperação automática exige exatamente um STYLE_CORE e que ele esteja `VISUAL_BOUND` ou possua STYLE DNA utilizável.

```text
STRUCTURE_EDIT_TARGET + STYLE_CORE + optional one relevant STYLE_SUPPORT
```

Não há restyle recursivo nem terceira geração automática.

Detalhes: [`QUICKSTART.md`](./QUICKSTART.md) / [English README](./README.md)

Versão atual: **`WPACK_v0.5.1-chat-native`**
