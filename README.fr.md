# W-Pack

### Génération d'images Project-source-first pour ChatGPT

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · **Français**

W-Pack v0.4 utilise par défaut les références persistantes d'un Project ChatGPT et sépare les autorités de style, personnage, pose, composition, proportion et objet.

## Nouveautés v0.4

- Le profil Project `DEFAULT` est activé automatiquement.
- Une référence STYLE unique devient `STYLE_CORE` en interne.
- Le médium visuel, le niveau de réalisme, les contours, l'abstraction, les valeurs/ombres, les couleurs, les textures et le traitement de l'arrière-plan sont protégés.
- Le flux commence toujours par une seule génération FRESH.
- Un unique `SINGLE_RESTYLE` n'est autorisé que si la structure est correcte mais que le style échoue.
- Aucun restyle récursif et aucune troisième génération automatique.
- Les images jointes dans le chat restent des overrides ou ajouts temporaires.

La récupération utilise uniquement le candidat fraîchement généré comme `STRUCTURE_EDIT_TARGET` et STYLE_CORE comme seule autorité de style. L'identité, la pose, la composition, la caméra, les relations spatiales, les objets et les conditions de scène sont préservés ; seul le rendu change.

Version actuelle : `WPACK_v0.4.0-chat-native`
