<p align="center">
  <img src="./assets/w-pack-hero.webp" alt="W-Pack — generación de imágenes con referencias controladas para ChatGPT" width="100%" />
</p>

<div align="center">

# W-Pack

### Generación de imágenes con referencias delimitadas para ChatGPT

**Usa imágenes de referencia de forma natural sin dejar que controlen todo.**

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · [简体中文](./README.zh-CN.md) · [繁體中文](./README.zh-TW.md) · **Español** · [Português (Brasil)](./README.pt-BR.md) · [Français](./README.fr.md) · [Deutsch](./README.de.md)

</div>

---

W-Pack es una capa chat-native para controlar cómo influyen las imágenes de referencia durante la generación y edición de imágenes en **ChatGPT Web, ChatGPT Projects y ChatGPT Skills**.

En una solicitud con varias referencias, una imagen de estilo puede introducir por accidente una identidad, una composición, un fondo o un objeto. W-Pack asigna a cada referencia una autoridad concreta: `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION` o `ITEM`.

```text
Usa la primera imagen solo como estilo.
Mantén intacta a la persona de la segunda imagen.
Usa la composición de la tercera imagen.
En esta imagen, conserva el rostro y la composición y cambia solo la ropa.
```

No hace falta escribir JSON ni IDs de manifest manualmente.

## Funciones principales

- **Control por lenguaje natural** — interpreta instrucciones como “usa este estilo”, “mantén esta persona”, “usa esta pose” o “usa esta composición”.
- **Inline references** — las imágenes adjuntas en la conversación actual no necesitan manifest.
- **Seis roles de autoridad** — `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION`, `ITEM`.
- **FRESH / EDIT** — separa la generación nueva de la edición de una imagen existente.
- **Project source profiles** — permite activar conjuntos de referencias reutilizables con instrucciones cortas.
- **Validación determinista** — detecta conflictos, duplicados y solicitudes de edición inválidas.

## Inicio rápido

1. Instala o sube [`skill/`](./skill) como ChatGPT Skill.
2. Adjunta una o más imágenes.
3. Indica en lenguaje natural qué debe controlar cada una.

```text
@W-Pack

Primera imagen: solo estilo.
Mantén la persona de la segunda imagen.
Usa la composición de la tercera.

Fondo: interior al atardecer con luz natural suave.
Relación de aspecto: 4:5 vertical.
Genera una imagen nueva.
```

No necesitas API Key, CLI local ni una API de imagen independiente.

## Authority model

| Role | Controla | No controla por defecto |
| --- | --- | --- |
| `STYLE` | color, textura, iluminación, renderizado, tratamiento gráfico | identidad, pose, composición exacta, identidad de objetos |
| `CHARACTER` | identidad, rostro, cabello, apariencia estable | fondo, iluminación, layout, objetos no relacionados |
| `POSE` | disposición corporal, gesto, postura, orientación | identidad, vestuario, entorno, estilo |
| `COMPOSITION` | encuadre, crop, ángulo, colocación, espacio negativo | identidad, vestuario, identidad de objetos, estilo global |
| `PROPORTION` | escala corporal/objetos y dimensiones relativas | identidad, pose detallada, estilo |
| `ITEM` | identidad, silueta y estructura de un objeto | identidad del personaje, entorno, estilo global |

> **Que algo sea visible no significa que esté autorizado.**

Un elemento incidental de una referencia no debe afectar al resultado salvo que su Authority lo permita.

## FRESH y EDIT

### `FRESH`
Para una imagen nueva o una regeneración basada en referencias aprobadas. No reutiliza silenciosamente resultados anteriores.

### `EDIT`
Para modificar una imagen existente manteniendo propiedades concretas. Internamente puede clasificarse como `MODIFY`, `RESTYLE` o `RECOMPOSE`.

## ChatGPT Project

Si reutilizas las mismas referencias, guárdalas en un ChatGPT Project y aplica [`project/PROJECT_INSTRUCTIONS.md`](./project/PROJECT_INSTRUCTIONS.md).

Una imagen no se activa automáticamente por estar dentro del Project. W-Pack selecciona solo el conjunto mínimo necesario para cada solicitud.

## Flujo

```text
Solicitud natural
  -> resolver FRESH / EDIT
  -> resolver referencias y Authority roles
  -> aplicar Source Profile opcional
  -> validar ámbitos y conflictos
  -> compilar scene / composition / lighting / text / preserve / avoid
  -> generar con ChatGPT
  -> auditoría silenciosa
```

Se admiten como máximo 5 referencias por generación.

## Validación

```bash
python3 skill/scripts/self_test.py
```

Resultado esperado:

```text
W-Pack self-test: PASS
```

## Estado actual

La versión actual es `WPACK_v0.3.0-chat-native`, centrada en inline references, resolución natural de Authority, `COMPOSITION`, FRESH/EDIT, Project Source Profiles y validación determinista.
