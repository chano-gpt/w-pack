# W-Pack

### Generación de imágenes Project-source-first para ChatGPT

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · **Español**

W-Pack v0.4 usa por defecto las referencias persistentes de un Project de ChatGPT y mantiene separadas las autoridades de estilo, personaje, pose, composición, proporción y objeto.

## Novedades de v0.4

- El perfil `DEFAULT` del Project se activa automáticamente.
- Una única referencia STYLE se convierte internamente en `STYLE_CORE`.
- Se protege el medio visual, nivel de realismo, contornos, abstracción, valores/sombras, color, textura y tratamiento del fondo.
- Siempre se empieza con una sola generación FRESH.
- Solo si la estructura es correcta pero falla el estilo se permite un único `SINGLE_RESTYLE`.
- No hay restyle recursivo ni una tercera generación automática.
- Las imágenes adjuntas en el chat son overrides o añadidos temporales.

En la recuperación se usan únicamente el candidato recién generado como `STRUCTURE_EDIT_TARGET` y STYLE_CORE como única autoridad de estilo. Se preservan identidad, pose, composición, cámara, relaciones espaciales, objetos y condiciones de escena; solo cambia el renderizado.

Versión actual: `WPACK_v0.4.0-chat-native`
