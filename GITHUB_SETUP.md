# GitHub Setup Guide

Step-by-step instructions to publish IHR BioAtlas on GitHub and
enable automatic GitHub Pages deployment.

---

## Part 1 — Create the Repository

1. Go to **https://github.com/new**

2. Fill in:
   - **Repository name:** `ihr-bioatlas`
   - **Description:** `ML-Driven Probabilistic Biodiversity Mapping — Indian Himalayan Region`
   - **Visibility:** Public *(required for free GitHub Pages)*
   - ✅ **Add a README file:** No *(we have our own)*
   - ✅ **Add .gitignore:** No *(we have our own)*
   - **License:** No *(we have our own)*

3. Click **Create repository**

---

## Part 2 — Push the Package

Open a terminal in the `ihr-bioatlas/` folder:

```bash
# Initialise git
git init
git branch -M main

# Add the GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/ihr-bioatlas.git

# Stage all files
git add .

# First commit
git commit -m "Initial release: IHR BioAtlas v3, 809 specimens, 15 orders"

# Push
git push -u origin main
```

---

## Part 3 — Enable GitHub Pages (auto-deploy)

1. On your repo page, go to **Settings** → **Pages** (left sidebar)

2. Under **Source**, select:
   - **GitHub Actions** *(not "Deploy from a branch")*

3. The workflow at `.github/workflows/deploy.yml` will:
   - Trigger automatically on every push to `main`
   - Find the latest `ihr_bioatlas_v*.html`
   - Publish it as `index.html` at your Pages URL

4. Your app will be live at:
   ```
   https://YOUR_USERNAME.github.io/ihr-bioatlas/
   ```
   *(takes ~2 minutes after first push)*

---

## Part 4 — Updating with New Data

When new sequencing data arrives:

```bash
# 1. Run the updater to produce a new version
python scripts/bioatlas_updater.py ihr_bioatlas_v3.html \
  --csv data/combined_output_2year.csv \
  --pdf data/Merged_2ndyear.pdf \
  --version v4 \
  --out ihr_bioatlas_v4.html

# 2. Commit and push — GitHub Actions will auto-deploy
git add ihr_bioatlas_v4.html CHANGELOG.md README.md
git commit -m "Year 2 update: 1500 specimens, v4"
git push
```

The GitHub Actions workflow will automatically pick up the new version
(it always deploys the highest-versioned `ihr_bioatlas_v*.html`).

---

## Part 5 — Add Repository Topics (optional but recommended)

On your repo page, click the ⚙ gear next to **About** and add topics:
```
biodiversity  dna-barcoding  oxford-nanopore  random-forest
leaflet  india  himalaya  zoology  bioinformatics  bold-systems
```

---

## Part 6 — GitHub Release (optional)

To create a formal versioned release:

1. Go to **Releases** → **Draft a new release**
2. **Tag:** `v3.0`
3. **Title:** `IHR BioAtlas v3 — Year 1 Release`
4. **Description:** copy from CHANGELOG.md
5. **Attach:** `ihr_bioatlas_v3.html` as a release asset
6. Click **Publish release**

This lets collaborators download specific versions.

---

## Credential / Authentication Notes

GitHub now uses **Personal Access Tokens (PAT)** instead of passwords.

If `git push` asks for a password:
1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Generate a new token with `repo` scope
3. Use the token as your password when prompted

Or use [GitHub CLI](https://cli.github.com/):
```bash
gh auth login
gh repo create ihr-bioatlas --public --source=. --push
```
