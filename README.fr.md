<p align="center">
  <img src="./assets/w-pack-hero.webp" alt="W-Pack — génération d’images à références contrôlées pour ChatGPT" width="100%" />
</p>

<div align="center">

# W-Pack

### Génération d’images à références délimitées pour ChatGPT

**Utilisez des images de référence naturellement, sans les laisser tout contrôler.**

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · [简体中文](./README.zh-CN.md) · [繁體中文](./README.zh-TW.md) · [Español](./README.es.md) · [Português (Brasil)](./README.pt-BR.md) · **Français** · [Deutsch](./README.de.md)

</div>

---

W-Pack est une couche chat-native qui contrôle l’influence des images de référence lors de la génération et de l’édition d’images dans **ChatGPT Web, ChatGPT Projects et ChatGPT Skills**.

Avec plusieurs références, une image de style peut transférer involontairement une identité, une composition, un arrière-plan ou un objet. W-Pack attribue à chaque référence une autorité précise : `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION` ou `ITEM`.

```text
Utilise la première image uniquement pour le style.
Conserve la personne de la deuxième image.
Utilise la composition de la troisième image.
Dans cette image, conserve le visage et la composition, mais change seulement la tenue.
```

Aucun JSON ni ID de manifest à écrire manuellement.

## Fonctionnalités principales

- **Contrôle par langage naturel** — comprend des instructions comme « utilise ce style », « garde cette personne », « utilise cette pose » ou « utilise cette composition ».
- **Inline references** — les images jointes dans la conversation actuelle n’ont pas besoin de manifest.
- **Six Authority roles** — `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION`, `ITEM`.
- **FRESH / EDIT** — distingue une nouvelle génération de la modification d’une image existante.
- **Project source profiles** — permet de réutiliser des ensembles de références avec des commandes courtes.
- **Validation déterministe** — détecte conflits, doublons et demandes d’édition invalides.

## Démarrage rapide

1. Installez ou importez [`skill/`](./skill) comme ChatGPT Skill.
2. Joignez une ou plusieurs images.
3. Indiquez en langage naturel ce que chaque image doit contrôler.

```text
@W-Pack

Première image : style uniquement.
Conserve la personne de la deuxième image.
Utilise la composition de la troisième.

Arrière-plan : intérieur au coucher du soleil, lumière naturelle douce.
Format : vertical 4:5.
Génère une nouvelle image.
```

Pas de clé API, pas de CLI local, pas d’API d’image séparée.

## Authority model

| Role | Contrôle | Ne contrôle pas par défaut |
| --- | --- | --- |
| `STYLE` | couleur, texture, lumière, rendu, traitement graphique | identité, pose, composition exacte, identité d’objet |
| `CHARACTER` | identité, visage, cheveux, apparence stable | arrière-plan, lumière, layout, objets sans rapport |
| `POSE` | disposition du corps, geste, posture, orientation | identité, vêtements, environnement, style |
| `COMPOSITION` | cadrage, crop, angle, placement, espace négatif | identité, vêtements, identité d’objet, style global |
| `PROPORTION` | échelle corps/objet et dimensions relatives | identité, pose détaillée, style |
| `ITEM` | identité, silhouette et structure d’un objet | identité du personnage, environnement, style global |

> **Visible ne signifie pas autorisé.**

Un élément incident d’une référence ne doit pas influencer le résultat si son Authority ne l’autorise pas.

## FRESH et EDIT

### `FRESH`
Pour une nouvelle image ou une régénération à partir de références approuvées. Les anciens résultats ne sont pas réutilisés silencieusement.

### `EDIT`
Pour modifier une image existante tout en préservant certaines propriétés. Peut être classé en interne comme `MODIFY`, `RESTYLE` ou `RECOMPOSE`.

## ChatGPT Project

Si vous réutilisez les mêmes références, stockez-les dans un ChatGPT Project et appliquez [`project/PROJECT_INSTRUCTIONS.md`](./project/PROJECT_INSTRUCTIONS.md).

Une image n’est jamais activée automatiquement parce qu’elle se trouve dans le Project. W-Pack sélectionne uniquement les références nécessaires à la requête en cours.

## Flux

```text
Requête en langage naturel
  -> résoudre FRESH / EDIT
  -> résoudre les références et Authority roles
  -> appliquer un Source Profile optionnel
  -> valider les portées et conflits
  -> compiler scene / composition / lighting / text / preserve / avoid
  -> génération d’image ChatGPT
  -> audit silencieux
```

Maximum de 5 références par génération.

## Validation

```bash
python3 skill/scripts/self_test.py
```

Résultat attendu :

```text
W-Pack self-test: PASS
```

## État actuel

La version actuelle est `WPACK_v0.3.0-chat-native`, centrée sur les inline references, la résolution naturelle des Authority roles, `COMPOSITION`, FRESH/EDIT, les Project Source Profiles et la validation déterministe.
