# Z-Pack

Z-Pack is a public starter harness for compiling image-generation requests from approved local authorities.

This distribution contains code and contracts only. It deliberately contains **no** style references, characters, poses, proportions, item references, generated images, benchmark data, presentation material, or private validation records.

## Before use

Add only images you own or have explicit permission to use. Local authority folders are ignored by Git:

- `private-assets/characters/`, `items/`, `poses/`, and `proportions/`
- `pack/styles/default/sources/`
- all inboxes, output, presentation folders, and credentials

Run `zpack doctor` to validate the empty starter or your local authority manifest. Generated candidates and audit data belong in the sibling `../zpack-workspace`, never in this repository.

## Public-release boundary

Do not commit authority images, generated results, private evaluations, presentation decks, API keys, or tokens. Review the staged set before every push:

```bash
git status --short
git diff --cached --name-only
zpack doctor
```

This repository does not grant a license for third-party images, names, or styles. Add a project license before accepting outside contributions or redistributing the code.
