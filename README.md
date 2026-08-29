<p align="center">
  <img src="assets/zpack-logo.png" alt="Z-Pack — Image Gen Hybrid Harness" width="760">
</p>

<p align="center">
  A disciplined image-generation harness for turning a scene brief and your approved local authorities into a reproducible, reviewable generation request.
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> · <a href="#how-it-works">How it works</a> · <a href="#showcase">Showcase</a> · <a href="#public-release-boundary">Public-release boundary</a>
</p>

## Build images with a clear authority chain

Z-Pack separates what you want to create from the visual authorities allowed to influence it. It compiles scene intent, character or item constraints, proportion requirements, and a selected style authority into a bounded request—then keeps the generated candidate and review evidence outside the repository.

The result is a practical workflow for image projects that need more than a one-off prompt: explicit inputs, SHA-bound local references, controlled retries, and a final human verdict.

## How it works

1. **Bring your own rights-cleared authorities.** Add only images you own or may use. Z-Pack never ships proprietary style, character, pose, or item references.
2. **Compile a bounded request.** Select the approved authorities and describe the scene, framing, physical constraints, and lighting.
3. **Generate fresh.** Normal retries begin from approved authorities again; previous candidates are not silently reused as style inputs.
4. **Review and verify.** Keep candidates, evidence, and audits in the external workspace, then make the final visual decision deliberately.

## Showcase

<p align="center">
  <img src="assets/showcase-samurai-portrait.png" alt="Showcase: cinematic samurai portrait" width="31%">
  <img src="assets/showcase-samurai-action.png" alt="Showcase: full-body samurai action scene" width="31%">
  <img src="assets/showcase-fantasy-rider.png" alt="Showcase: epic fantasy rider scene" width="31%">
</p>

<p align="center"><sub>Project-owner supplied showcase outputs. They are included for presentation only—not as style, identity, pose, proportion, or item authorities.</sub></p>

## Quick start

```bash
python3 -m pip install -e .
zpack doctor
zpack init
```

The public starter validates with zero authorities. Before compiling a request, add only rights-cleared local assets and complete your own review process. See [QUICKSTART.md](QUICKSTART.md) for the command flow.

## Public-release boundary

This repository intentionally excludes authority images, generated run data, private evaluations, benchmark and test artifacts, presentation decks, credentials, and tokens. Local authority folders are ignored by Git:

- `private-assets/characters/`, `items/`, `poses/`, and `proportions/`
- `pack/styles/default/sources/`
- inboxes, output, and local presentation folders

Before every push, review what is staged:

```bash
git status --short
git diff --cached --name-only
zpack doctor
```

The included showcase images do not grant a license to third-party images, names, or styles. Add a project license before accepting outside contributions or redistributing the code.
