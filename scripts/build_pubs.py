"""Génère docs/publications.md et télécharge les PDF en accès ouvert dans docs/publications/.

Sources : HAL (idHAL nicolas-ferey) + publications du CV de l'HDR absentes de HAL.
PDF : fichier principal déposé dans HAL, sinon version en accès ouvert trouvée par Unpaywall.
"""
import json, re, sys, unicodedata, urllib.request, urllib.parse, pathlib, time

HAL_JSON, SITE = sys.argv[1], pathlib.Path(sys.argv[2])
PDF_DIR = SITE / "docs" / "publications"
PDF_DIR.mkdir(parents=True, exist_ok=True)

TYPES = {"ART": "Revue", "COMM": "Conférence", "POSTER": "Poster", "COUV": "Chapitre",
         "UNDEFINED": "Prépublication", "OTHER": "Rapport", "WORKSHOP": "Workshop"}

def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()

docs = json.load(open(HAL_JSON))["response"]["docs"]
pubs, seen = [], set()
for d in docs:
    key = d.get("doiId_s", "").lower() or norm(d["title_s"][0])[:60]
    if key in seen:
        continue
    seen.add(key)
    venue = d.get("journalTitle_s") or d.get("conferenceTitle_s") or d.get("bookTitle_s") or ""
    pubs.append(dict(year=d.get("producedDateY_i"), type=TYPES.get(d["docType_s"], d["docType_s"]),
                     title=d["title_s"][0], authors=d.get("authFullName_s", []), venue=venue,
                     doi=d.get("doiId_s", ""), hal=d["halId_s"], halpdf=d.get("fileMain_s", "")))

# Publications du CV de l'HDR absentes de HAL
EXTRA = [
    (2016, "Conférence", "Towards an AR/VR molecular tangible interface based on a lightweight RGB markerless tracking of a modular physical model",
     ["Xavier Martinez", "Nicolas Férey", "Jean-Marc Vézien", "Patrick Bourdot"], "EuroVR 2016 — Best Paper Award"),
    (2015, "Workshop", "1st IEEE Workshop on Virtual and Augmented Reality for Molecular Science (VARMS)",
     ["Xavier Martinez", "Nicolas Férey", "Jean-Marc Vézien", "Patrick Bourdot"], "IEEE VR 2015"),
    (2015, "Workshop", "From molecular dynamics in virtual reality environments to fundamental questions about human-computer interaction",
     ["Alexandre Kouyoumdjian", "Nicolas Férey", "Patrick Bourdot"], "VARMS@IEEE VR 2015"),
    (2014, "Conférence", "A hardware and software architecture to deal with multimodal and collaborative interactions in multiuser virtual reality environments",
     ["Pierre Martin", "Anthony Tseu", "Nicolas Férey", "David Touraine", "Patrick Bourdot"], "SPIE, The Engineering Reality of Virtual Reality"),
    (2013, "Conférence", "6DoF navigation in virtual worlds: comparison of joystick-based and head-controlled paradigms",
     ["Weiya Chen", "Anthony Plancoulaine", "Nicolas Férey", "David Touraine", "Julien Nelson", "Patrick Bourdot"], "ACM VRST 2013"),
    (2013, "Poster", "Augmented Elastic Network Models combined with SAXS data",
     ["Aurélien-Edouard Molza", "Olivier Delalande", "Emmanuel Giudice", "Nicolas Férey", "Marc Baaden", "Mirjam Czjzek", "Elisabeth Le Rumeur"], "GGMM 2013"),
    (2012, "Conférence", "A haptic paradigm to learn how to drive a non-motorised vehicle manipulated through an articulated mechanism",
     ["Pierre Martin", "Nicolas Férey", "Céline Clavel", "Patrick Bourdot"], "Joint Virtual Reality Conference (JVRC), 81–84"),
]
for y, t, title, authors, venue in EXTRA:
    if norm(title)[:60] not in {norm(p["title"])[:60] for p in pubs}:
        pubs.append(dict(year=y, type=t, title=title, authors=authors, venue=venue, doi="", hal="", halpdf=""))

def fetch(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (site-pro builder)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    if not data.startswith(b"%PDF"):
        raise ValueError("pas un PDF")
    dest.write_bytes(data)

def unpaywall(doi):
    try:
        url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email=site-pro@example.org"
        with urllib.request.urlopen(url, timeout=30) as r:
            loc = json.load(r).get("best_oa_location") or {}
        return loc.get("url_for_pdf") or ""
    except Exception:
        return ""

import subprocess, shutil

import hashlib

def first_page_has_title(path, title):
    # Le titre doit figurer en tête de la première page (et non dans une liste de références)
    try:
        txt = subprocess.run(["pdftotext", "-l", "1", str(path), "-"], capture_output=True,
                             text=True, timeout=30).stdout
    except Exception:
        return False
    head = re.sub(r"\s+", " ", norm(txt))[:700]
    words = norm(title).split()[:8]
    return " ".join(words) in head

BLACKLIST = ["CSI 2024/CV.pdf", "2168_GTC2010.pdf", "Flyer-PIRATE.pdf"]  # faux positifs vérifiés
used = {}  # empreinte du fichier source -> titre ; un même fichier ne peut servir qu'une fois

NO_LOCAL = ["Interactive Molecular Dynamics", "Sémantisation du contenu et du contexte"]  # titres trop génériques

def local_pdf(title):
    if title == NO_LOCAL[0] or title.startswith(NO_LOCAL[1]):
        return ""
    frag = " ".join(title.split()[:5]).replace('"', "")
    q = f'kMDItemContentType == "com.adobe.pdf" && kMDItemTextContent == "{frag}*"cd'
    out = subprocess.run(["mdfind", q], capture_output=True, text=True, timeout=60).stdout.split("\n")
    for f in out:
        if not f or any(b in f for b in BLACKLIST) or "/SitePro/" in f or "/Library/" in f or not first_page_has_title(f, title):
            continue
        h = hashlib.sha1(pathlib.Path(f).read_bytes()).hexdigest()
        if h in used and used[h] != title:
            continue
        used[h] = title
        return f
    return ""

report = []
for p in pubs:
    slug = re.sub(r"[^a-z0-9]+", "-", norm(p["title"]))[:50].strip("-")
    dest = PDF_DIR / f"{p['year']}-{slug}.pdf"
    p["pdf"] = p["pdfsrc"] = ""
    if not dest.exists():
        oa = unpaywall(p["doi"]) if p["doi"] else ""
        # HAL est protégé contre les robots : on ne prend que les dépôts hors HAL
        if oa and "hal." not in oa and "archives-ouvertes" not in oa:
            try:
                fetch(oa, dest)
                p["pdfsrc"] = "accès ouvert"
            except Exception as e:
                report.append(f"échec {oa} : {e}")
        if not dest.exists():
            loc = local_pdf(p["title"])
            if loc:
                shutil.copy(loc, dest)
                p["pdfsrc"] = f"local : {loc}"
    if dest.exists() and first_page_has_title(dest, p["title"]):
        p["pdf"] = f"publications/{dest.name}"
    elif dest.exists():
        report.append(f"titre non retrouvé dans {dest.name}, fichier écarté")
        dest.unlink()
    elif p["halpdf"]:
        p["pdf"] = f"https://hal.science/{p['hal']}/document"
        p["pdfsrc"] = "HAL (lien)"
    report.append(f"SRC\t{p['pdfsrc']}") if p["pdfsrc"].startswith("local") else None
    report.append(f"{p['year']} {p['pdfsrc'] or ('PDF' if p['pdf'] else '---'):14.14} {p['title'][:60]}")

pubs.sort(key=lambda p: (-(p["year"] or 0), p["type"], p["title"]))

# Thèses co-encadrées, mises en valeur l'année de leur soutenance
THESES = [
    (2021, "Mengchen Wang", "20 décembre 2021", "Modèle distribué et asynchrone pour la simulation interactive en mécanique des fluides : vers une plateforme de jeu sérieux pour l'aide à la prise de décision",
     "co-direction P. Bourdot et F. Magoulès ; co-encadrement 50 %", "tel-03609841", "2021UPASG113"),
    (2018, "Alexandre Kouyoumdjian", "10 décembre 2018", "Sélection de cibles en mouvement : contexte, modèles, et paradigmes d'aide à la sélection",
     "direction P. Bourdot ; co-encadrement 50 %", "tel-02163235", "2018SACLS606"),
    (2017, "Xavier Martinez", "10 octobre 2017", "Tracking sans marqueur de modèles physiques modulaires et articulés : vers une interface tangible pour la manipulation de simulations moléculaires",
     "direction P. Bourdot ; co-encadrement 25 %", "tel-01633497", "2017SACLS231"),
    (2015, "Mikael Trellet", "18 décembre 2015", "Exploration et analyse immersives de données moléculaires guidées par la tâche et la modélisation sémantique des contenus",
     "co-direction P. Bourdot et M. Baaden ; co-encadrement 50 %", "tel-01269634", "2015SACLS262"),
    (2015, "Weiya Chen", "15 décembre 2015", "Collaboration in Multi-user Immersive Virtual Environment",
     "direction P. Bourdot ; co-encadrement 25 %", "tel-01340364", "2015SACLS248"),
]

def thesis_block(t):
    _, who, date, title, role, hal, tf = t
    return [f'!!! success "Thèse soutenue · {who} · {date}"',
            f"    **{title}**. Université Paris-Saclay ({role}). "
            f"[:material-file-pdf-box: PDF](https://hal.science/{hal}/document) · "
            f"[HAL](https://hal.science/{hal}) · [theses.fr](https://theses.fr/{tf})", ""]

def fmt_authors(names):
    out = []
    for n in names:
        b = n.replace("Ferey", "Férey")
        out.append(f"**{b}**" if "Férey" in b and b.startswith("N") else b)
    return ", ".join(out)

lines = ["# Publications", "",
         f"Liste complète ({len(pubs)} références et {len(THESES)} thèses co-encadrées), de la plus récente à la plus ancienne. "
         "Les PDF sont les versions déposées en accès ouvert (HAL ou dépôt de l'éditeur).", "",
         "!!! tip \"Voir aussi\"",
         "    [HAL](https://cv.hal.science/nicolas-ferey) · "
         "[Google Scholar](https://scholar.google.com/citations?user=lXethhQAAAAJ)", ""]
year = None
for p in pubs:
    if p["year"] != year:
        year = p["year"]
        lines += ["", f"## {year}", ""]
        for t in THESES:
            if t[0] == year:
                lines += thesis_block(t)
    links = []
    if p["pdf"]:
        links.append(f"[:material-file-pdf-box: PDF]({p['pdf']})")
    if p["doi"]:
        links.append(f"[DOI](https://doi.org/{p['doi']})")
    if p["hal"]:
        links.append(f"[HAL](https://hal.science/{p['hal']})")
    if not p["pdf"]:
        links.append("*PDF non disponible*")
    venue = f" *{p['venue']}*." if p["venue"] else ""
    lines.append(f"- <span class=\"pubtype\">{p['type']}</span> {fmt_authors(p['authors'])}. "
                 f"**{p['title'].rstrip('.')}**.{venue} {' · '.join(links)}")
(SITE / "docs" / "publications.md").write_text("\n".join(lines) + "\n")
print("\n".join(report))
print(f"\n{len(pubs)} références, {sum(1 for p in pubs if p['pdf'])} avec PDF")
