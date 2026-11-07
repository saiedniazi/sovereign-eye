# Sovereign Eye

Sovereign Eye is the repository for the eye project.

The tree currently holds this introduction and a continuous integration workflow. Application source is not in the repository yet.

## Checks

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs when:

- commits are pushed to `main`
- a pull request targets `main`
- someone starts the workflow from the Actions tab

The workflow fails when an HTML heading in this file is opened at one level and closed at another. Text inside code spans is ignored, so an example can show a broken tag without failing the check.

Run the same check locally:

```bash
python3 scripts/check_readme.py
```
