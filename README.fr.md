# W-Pack

### Contrôle de références pour la génération d’images dans ChatGPT

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · **Français**

W-Pack v0.5.1 sépare l’**autorité** d’une référence (ce qu’elle peut contrôler) de son **transport** (si l’image a réellement été transmise au modèle de génération).

## v0.5.1

- La présence d’un fichier dans Project ne signifie plus automatiquement `VISUAL_BOUND`.
- STYLE est résolu en un `STYLE_CORE` et jusqu’à deux `STYLE_SUPPORT` bornés.
- Si le binding visuel direct n’est pas vérifiable, STYLE DNA peut être utilisé via `style_signature` et `anti_drift_signature`.
- Les cheveux deviennent un axe de style indépendant : `hair_rendering_grammar`.
- Le fallback `CLEAN_MASS` réduit les halos de mèches volantes, les pointes répétitivement fourchues, les mèches aléatoires devant le visage et les reflets filiformes par cheveu lorsque la source ne les demande pas.
- Un seul `SINGLE_RESTYLE` est autorisé lorsque la structure passe mais que le style échoue.

## Recovery

La récupération automatique exige exactement un STYLE_CORE, qui doit être `VISUAL_BOUND` ou disposer d’un STYLE DNA exploitable.

```text
STRUCTURE_EDIT_TARGET + STYLE_CORE + optional one relevant STYLE_SUPPORT
```

Pas de restyle récursif ni de troisième génération automatique.

Détails : [`QUICKSTART.md`](./QUICKSTART.md) / [English README](./README.md)

Version actuelle : **`WPACK_v0.5.1-chat-native`**
