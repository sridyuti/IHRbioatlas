# 🏔 IHR BioAtlas

**ML-Driven Probabilistic Biodiversity Mapping — Indian Himalayan Region**

[![ZSI](https://img.shields.io/badge/Institution-Zoological%20Survey%20of%20India-gold)](https://zsi.gov.in)
[![Project](https://img.shields.io/badge/NMHS%20Project-2023--24%2FLG11%2F182-blue)](https://nmhs.org.in)
[![ONT](https://img.shields.io/badge/Sequencing-Oxford%20Nanopore-orange)](https://nanoporetech.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Specimens](https://img.shields.io/badge/Specimens-809-brightgreen)]()
[![Orders](https://img.shields.io/badge/Orders-15-purple)]()

---

## Overview

IHR BioAtlas is a **standalone single-file interactive web application** for visualising and exploring faunal biodiversity data collected across the Indian Himalayan Region (IHR) using Oxford Nanopore Technology (ONT) MinION sequencing and COI-5P DNA barcoding.

The platform integrates:
- **Oxford Nanopore MinION** field sequencing
- **COI-5P DNA barcoding** with BOLD BIN assignment
- **Random Forest classifier** for genus-level occurrence probability mapping
- **Leaflet.js** interactive map with dots / heatmap / marker-cluster modes
- **Chart.js** analytics dashboards
- **Standalone HTML deployment** — no server, no install, one file

> **Project:** Oxford Nanopore Sequencing-Based Faunal Diversity Mapping in the Indian Himalayan Region
> **Funded by:** National Mission for Himalayan Studies (NMHS), Project No. 2023-24/LG11/182
> **Duration:** April 2025 – March 2028

---

## 🗺 Live Demo

Open `ihr_bioatlas_v3.html` directly in any modern browser — no internet connection required after first load (external fonts/tiles load from CDN).

---

## 📊 Dataset Summary (Year 1 — 2025)

| Metric | Count |
|---|---|
| Specimens barcoded | **809** |
| Species identified | **208** |
| Genera | **237** |
| Families | **110** |
| Orders | **15** |
| BINs assigned (BOLD) | **451** |
| Specimens with images | **689** |
| Sampling states | Himachal Pradesh, West Bengal, Arunachal Pradesh, Meghalaya, Nagaland |
| Key field sites | GHNP (Great Himalayan National Park), SNP (Singalila National Park) |

**Top Orders by specimen count:**

| Order | Specimens |
|---|---|
| Lepidoptera | 244 |
| Diptera | 234 |
| Hymenoptera | 162 |
| Araneae | 46 |
| Hemiptera | 40 |
| Orthoptera | 27 |

---

## 🗂 Repository Structure

```
ihr-bioatlas/
│
├── ihr_bioatlas_v3.html          ← Main standalone web application
│
├── scripts/
│   └── bioatlas_updater.py       ← Update tool (GUI + CLI)
│
├── data/
│   ├── README.txt                ← Data file placement instructions
│   └── (place CSV & PDF here)    ← Not committed — see Data Files section
│
├── docs/
│   ├── UPDATE_GUIDE.md           ← Step-by-step update instructions
│   └── FIELD_REFERENCE.md        ← CSV column reference
│
├── assets/
│   └── screenshot.png            ← App screenshot (optional)
│
├── .gitignore
├── LICENSE
└── README.md                     ← This file
```

---

## 🚀 Quick Start

### View the app
```bash
# Just open the HTML file in your browser
# Windows
start ihr_bioatlas_v3.html

# macOS
open ihr_bioatlas_v3.html

# Linux
xdg-open ihr_bioatlas_v3.html
```

### Update with new data (GUI)
```bash
pip install pandas PyMuPDF
python scripts/bioatlas_updater.py
```
A dark-themed GUI will open. Browse to your files and click **Run Update**.

### Update with new data (CLI)
```bash
python scripts/bioatlas_updater.py ihr_bioatlas_v3.html \
  --csv data/combined_output_1year.csv \
  --pdf data/Merged_1styear.pdf \
  --version v4 \
  --out ihr_bioatlas_v4.html
```

---

## 🔧 The Updater Script

`scripts/bioatlas_updater.py` handles all data and metadata updates to the HTML app.

### Requirements
```bash
pip install pandas PyMuPDF
```
(`PyMuPDF` is only needed when updating specimen images from PDF.)

### GUI Controls

| Section | What you can change |
|---|---|
| ① File Paths | Source HTML, CSV, PDF, output HTML path |
| ② Version | Version string shown in title (v3, v3.1, v2026-04…) |
| ③ App Identity | App name, brand emoji/icon, subtitles, header badge text |
| ④ Tab Labels | All 6 navigation tab labels (with emoji) |
| ⑤ Options | Toggle: CSV update / PDF images / metadata / auto-backup |

### CLI Options

```
positional:
  html                  Source HTML file path

optional:
  --csv FILE            CSV with specimen records
  --pdf FILE            PDF with specimen images (slow: 30–120s)
  --out FILE            Output path (default: overwrite source)
  --version STR         Version string, e.g. v3
  --name STR            App name
  --icon STR            Brand emblem emoji or text
  --subtitle STR        Brand subtitle line
  --loading-sub STR     Loading screen subtitle
  --badge STR           Header badge text
  --tab data_p=Label    Override a tab label (repeatable)
  --no-backup           Skip auto-backup
```

### What gets updated from CSV

- All **809+ specimen records** (`RECORDS` JSON block) — lat/lon, taxonomy, BIN, collector, date, etc.
- **ORDER_STATS** block — specimens/genera/species/families per order
- **Header stat cards** — Specimens, Species, Genera, Families, Orders, With Images
- **Analytics KPI cards** — same counters
- **All text references** — "N records", "Master specimen data (N rows)", etc.

### What gets updated from PDF

Specimen photographs are extracted from the PDF (matched by Field ID) and embedded as base64 images in the `IMAGE_DATA` block — enabling offline popup images.

### Auto-backup

Before overwriting the source file, a timestamped backup is automatically created:
```
ihr_bioatlas_v3_backup_20251015_143022.html
```

---

## 📋 Data Files

The primary data files are **not committed** to this repository (large binary/sensitive data). Place them in the `data/` folder:

| File | Description |
|---|---|
| `combined_output_1year.csv` | Master specimen dataset from BOLD export |
| `Merged_1styear.pdf` | Sequencing report with specimen photographs |

### CSV Column Reference

See `docs/FIELD_REFERENCE.md` for the full column mapping. Key columns used by the updater:

`Field ID`, `Sample ID`, `Process ID`, `Lat`, `Lon`, `Species`, `Genus`, `Family`, `Order`, `Subfamily`, `State/Province`, `Region`, `Exact Site`, `BIN`, `Habitat`, `Life Stage`, `Collectors`, `Collection Date`, `Elev`, `Identification`, `Match_Status`, `Class`, `Phylum`, `COI-5P Seq. Length`, `Image Count`

---

## 🧬 Methods Summary

1. **Field collection** across Western (Himachal Pradesh), Central (West Bengal), and Eastern (Arunachal Pradesh) IHR sectors
2. **DNA extraction** and **Oxford Nanopore MinION** sequencing with UMI-tagged multiplexing
3. **COI-5P barcode** generation (target: 658 bp)
4. **BOLD matching** for BIN assignment and species identification
5. **Random Forest classifier** (`n_estimators=100`) trained on lat/lon for genus-level occurrence probability
6. **Spatial visualization** via Leaflet.js with dots / heatmap / cluster modes
7. **Standalone HTML** packaging — entire platform in one file

---

## 👥 Authors

**Subhajit Das** · Avas Pakrashi · Dibyajoyti Ghosh · Dola Roy · Jayita Sengupta · Dhriti Banerjee · **Atanu Naskar** *(Corresponding Author)*

Zoological Survey of India, M-Block, New Alipore, Kolkata – 700053, West Bengal, India

---

## 🏛 Funding

This work was supported by the **National Mission for Himalayan Studies (NMHS)**, Ministry of Environment, Forest and Climate Change, Government of India — Project No. **2023-24/LG11/182**.

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## 🔗 Key Databases & Systems

- [BOLD Systems](https://boldsystems.org) — Barcode of Life Data System
- [NCBI](https://ncbi.nlm.nih.gov) — National Center for Biotechnology Information
- [GBIF](https://gbif.org) — Global Biodiversity Information Facility
- [Oxford Nanopore Technologies](https://nanoporetech.com)
