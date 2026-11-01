# Site pro — Nicolas Férey

Site statique MkDocs Material. Le contenu est dans `docs/*.md`, la navigation dans `mkdocs.yml`.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/mkdocs serve      # aperçu sur http://127.0.0.1:8000
.venv/bin/mkdocs build      # génère le dossier site/
```

Publication : sur GitHub, le workflow `.github/workflows/deploy.yml` publie sur
GitHub Pages à chaque push sur `main`. Pour un autre serveur, copier `site/`.

Les éléments à compléter sont marqués `TODO` (`grep -rn TODO docs mkdocs.yml`).
