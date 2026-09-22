# Rebranding & Customization

Cornerstone is engineered specifically to be forked and transformed into your own desktop application with minimal friction.

---

## ⚡ Single-Command Rebranding

Once you have forked or cloned this template, rebrand it into your own project using the built-in `init` command:

```bash
stone init "My Application" -d "A powerful desktop tool for productivity."
# or with just:
just init "My Application" -d "A powerful desktop tool for productivity."
```

### Advanced Options

```bash
# Register custom shorthand CLI aliases
stone init "My Application" --alias stone -a myapp

# Strip demo/sample components and reset to minimal skeletons
stone init "My Application" --clean-examples

# Re-initialize a fresh Git repository with a single clean initial commit
stone init "My Application" --fresh-git

# Choose CI provider (github, gitlab, or both)
stone init "My Application" --ci github

# Launch the interactive rebranding wizard
stone init -i
```

---

## 🔧 What `stone init` Does

1. **Config Rewrites:** Updates `name`, `version` (reset to `0.1.0`), `description`, and `[project.scripts]` in `pyproject.toml` and `package.json`.
2. **Runtime Identity:** Sets `[tool.app] display-name` in `pyproject.toml`, which acts as the single source of truth for window titles, app bundles, and CLI banners.
3. **Template Archival:** Preserves the original Cornerstone template documentation and bridge references in `.cornerstone/` for upstream reference.
4. **Clean Readme:** Generates a fresh, project-specific root `README.md`.

---

## 🎨 Further Customization Checklist

After running `stone init`:
- [ ] **Application Icon:** Replace icons in `public/` and `app/`.
- [ ] **License:** Choose and add your `LICENSE` file.
- [ ] **Git Remote:** Update repository URLs to point to your new project repository.
