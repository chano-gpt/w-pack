<p align="center">
  <img src="./assets/w-pack-hero.webp" alt="W-Pack — geração de imagens com referências controladas para ChatGPT" width="100%" />
</p>

<div align="center">

# W-Pack

### Geração de imagens com referências delimitadas para ChatGPT

**Use imagens de referência naturalmente, sem deixar que elas controlem tudo.**

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · [简体中文](./README.zh-CN.md) · [繁體中文](./README.zh-TW.md) · [Español](./README.es.md) · **Português (Brasil)** · [Français](./README.fr.md) · [Deutsch](./README.de.md)

</div>

---

W-Pack é uma camada chat-native para controlar como imagens de referência influenciam a geração e edição de imagens em **ChatGPT Web, ChatGPT Projects e ChatGPT Skills**.

Em pedidos com várias referências, uma imagem de estilo pode acabar transferindo identidade, composição, fundo ou objetos sem intenção. O W-Pack atribui a cada referência uma autoridade específica: `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION` ou `ITEM`.

```text
Use a primeira imagem apenas como referência de estilo.
Mantenha a pessoa da segunda imagem igual.
Use a composição da terceira imagem.
Nesta imagem, preserve o rosto e a composição e altere apenas a roupa.
```

Não é necessário escrever JSON nem IDs de manifest manualmente.

## Principais recursos

- **Controle por linguagem natural** — interpreta instruções como “use este estilo”, “mantenha esta pessoa”, “use esta pose” e “use esta composição”.
- **Inline references** — imagens anexadas na conversa atual não precisam de manifest.
- **Seis Authority roles** — `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION`, `ITEM`.
- **FRESH / EDIT** — diferencia uma nova geração da edição de uma imagem existente.
- **Project source profiles** — permite reutilizar conjuntos de referências com comandos curtos.
- **Validação determinística** — detecta conflitos, duplicações e pedidos de edição inválidos.

## Início rápido

1. Instale ou envie [`skill/`](./skill) como ChatGPT Skill.
2. Anexe uma ou mais imagens.
3. Diga em linguagem natural o que cada imagem deve controlar.

```text
@W-Pack

Primeira imagem: apenas estilo.
Mantenha a pessoa da segunda imagem.
Use a composição da terceira.

Fundo: interior ao pôr do sol com luz natural suave.
Proporção: 4:5 vertical.
Gere uma imagem nova.
```

Sem API Key, CLI local ou API de imagem separada.

## Authority model

| Role | Controla | Não controla por padrão |
| --- | --- | --- |
| `STYLE` | cor, textura, iluminação, renderização, tratamento gráfico | identidade, pose, composição exata, identidade de objetos |
| `CHARACTER` | identidade, rosto, cabelo, aparência estável | fundo, iluminação, layout, objetos não relacionados |
| `POSE` | disposição corporal, gesto, postura, orientação | identidade, roupa, ambiente, estilo |
| `COMPOSITION` | enquadramento, crop, ângulo, posicionamento, espaço negativo | identidade, roupa, identidade de objetos, estilo global |
| `PROPORTION` | escala corporal/objetos e dimensões relativas | identidade, pose detalhada, estilo |
| `ITEM` | identidade, silhueta e estrutura de um objeto | identidade do personagem, ambiente, estilo global |

> **Estar visível não significa estar autorizado.**

Um elemento incidental de uma referência não deve influenciar o resultado a menos que sua Authority permita.

## FRESH e EDIT

### `FRESH`
Para uma nova imagem ou regeneração baseada em referências aprovadas. Resultados anteriores não são reutilizados silenciosamente.

### `EDIT`
Para modificar uma imagem existente preservando propriedades específicas. Internamente pode ser classificado como `MODIFY`, `RESTYLE` ou `RECOMPOSE`.

## ChatGPT Project

Se você reutiliza as mesmas referências, salve-as em um ChatGPT Project e aplique [`project/PROJECT_INSTRUCTIONS.md`](./project/PROJECT_INSTRUCTIONS.md).

Uma imagem não se torna ativa automaticamente por estar no Project. O W-Pack seleciona apenas o conjunto mínimo necessário para cada solicitação.

## Fluxo

```text
Solicitação em linguagem natural
  -> resolver FRESH / EDIT
  -> resolver referências e Authority roles
  -> aplicar Source Profile opcional
  -> validar escopos e conflitos
  -> compilar scene / composition / lighting / text / preserve / avoid
  -> geração de imagem no ChatGPT
  -> auditoria silenciosa
```

No máximo 5 referências por geração.

## Validação

```bash
python3 skill/scripts/self_test.py
```

Resultado esperado:

```text
W-Pack self-test: PASS
```

## Status atual

A versão atual é `WPACK_v0.3.0-chat-native`, focada em inline references, resolução natural de Authority, `COMPOSITION`, FRESH/EDIT, Project Source Profiles e validação determinística.
