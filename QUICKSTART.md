# Quick start

W-Pack is designed for ChatGPT web, ChatGPT Projects, and ChatGPT Skills. No local CLI, API key, Codex OAuth, or GPU is required.

## 1. Install the Skill

Upload the packaged `skill.zip` to ChatGPT Skills.

## 2. Configure persistent Project sources

For the intended W-Pack workflow:

1. Add reusable reference images to the ChatGPT Project.
2. Copy `project/PROJECT_INSTRUCTIONS.md` into the Project instructions.
3. Define reusable authorities in `project/AUTHORITY_MANIFEST.example.json`.
4. Put the normal source set in `source_profiles.DEFAULT` and set `default_source_profile` to `DEFAULT`.

The DEFAULT Project source set is then active automatically for every W-Pack image request. You do not need to attach the same images again or repeat "use the sources".

## 3. Use chat attachments only when needed

A current-chat image is optional. Use it when you want a temporary override or addition, for example a one-off pose or composition.

If an explicit inline reference uses the same role as a default Project authority, it overrides that role for the current request while the rest of the DEFAULT Project sources remain active.

## Style behavior

When DEFAULT includes a STYLE authority, W-Pack preserves its visual medium and degree of realism. Camera or lens terminology changes perspective or optical behavior and does not turn a stylized source into a photograph unless the user explicitly requests photorealism.
