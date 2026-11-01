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

## Publications

`docs/publications.md` et les PDF de `docs/publications/` sont générés par :

```bash
curl -s "https://api.archives-ouvertes.fr/search/?q=authIdHal_s:nicolas-ferey&rows=500&fl=halId_s,docType_s,title_s,authFullName_s,producedDateY_i,journalTitle_s,conferenceTitle_s,bookTitle_s,doiId_s,fileMain_s&wt=json" > /tmp/hal.json
python3 scripts/build_pubs.py /tmp/hal.json .
```

Sources des PDF : version en accès ouvert hors HAL (Unpaywall), sinon copie locale dont la
première page porte le titre ; à défaut, lien vers le PDF déposé sur HAL.
