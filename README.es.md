# W-Pack

### Control de referencias para generación de imágenes en ChatGPT

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · **Español**

W-Pack v0.5.1 separa la **autoridad** de una referencia (qué puede controlar) de su **transporte** (si la imagen llegó realmente al modelo de generación).

## v0.5.1

- Un archivo dentro de Project ya no implica `VISUAL_BOUND`.
- STYLE se resuelve como un `STYLE_CORE` y hasta dos `STYLE_SUPPORT` acotados.
- Si el enlace visual directo no puede verificarse, se puede usar STYLE DNA mediante `style_signature` y `anti_drift_signature`.
- El cabello se audita como eje independiente `hair_rendering_grammar`.
- El fallback `CLEAN_MASS` reduce halos de pelos sueltos, puntas repetidamente bifurcadas, mechones aleatorios sobre la cara y reflejos finos tipo hilo cuando la fuente no los exige.
- Solo se permite un `SINGLE_RESTYLE` cuando la estructura pasa y el estilo falla.

## Recuperación

La recuperación automática requiere un único STYLE_CORE y que este esté `VISUAL_BOUND` o disponga de STYLE DNA utilizable.

```text
STRUCTURE_EDIT_TARGET + STYLE_CORE + optional one relevant STYLE_SUPPORT
```

No hay restyle recursivo ni una tercera generación automática.

Más información: [`QUICKSTART.md`](./QUICKSTART.md) / [English README](./README.md)

Versión actual: **`WPACK_v0.5.1-chat-native`**
