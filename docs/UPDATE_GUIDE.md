# IHR BioAtlas — Update Guide

This guide covers how to update the standalone HTML app as new sequencing data
arrives through the project timeline (April 2025 – March 2028).

---

## Prerequisites

Install Python dependencies once:

```bash
pip install pandas PyMuPDF
```

---

## Workflow: Annual / Periodic Update

### Step 1 — Prepare your data files

Ensure you have:
- `combined_output_1year.csv` (or the latest cumulative BOLD export CSV)
- `Merged_1styear.pdf` (or the latest sequencing report PDF with specimen photos)

Place them in the `data/` folder of this repository.

---

### Step 2 — Run the updater

#### Option A: GUI (recommended)

```bash
python scripts/bioatlas_updater.py
```

In the window that opens:

| Field | Value |
|---|---|
| Source HTML | `ihr_bioatlas_v3.html` (or current version) |
| CSV | `data/combined_output_YYYY.csv` |
| PDF | `data/Merged_YYYY.pdf` |
| Output HTML | `ihr_bioatlas_v4.html` (new version name) |
| Version string | `v4` |

Check all boxes under **⑤ What to Update**, then click **▶ Run Update**.

The log panel will show every change made. A backup is created automatically.

#### Option B: CLI

```bash
python scripts/bioatlas_updater.py ihr_bioatlas_v3.html \
  --csv data/combined_output_2year.csv \
  --pdf data/Merged_2ndyear.pdf \
  --version v4 \
  --out ihr_bioatlas_v4.html
```

---

### Step 3 — Verify in browser

Open the new HTML file and confirm:
1. **Header stats** match your CSV row count
2. **Analytics KPI cards** show correct numbers
3. **Distribution Map** shows all new specimen markers
4. **Specimen Data** table has the correct total
5. **Popup images** appear on marker click (if PDF was updated)

Use the **Troubleshoot** tab → **App Status Check** for a live diagnostic.

---

### Step 4 — Commit to GitHub

```bash
# Stage the new HTML
git add ihr_bioatlas_v4.html

# Remove the old version if desired
git rm ihr_bioatlas_v3.html

# Update README version badge if needed
# Edit README.md: change v3 → v4 and specimen count

git add README.md
git commit -m "Year 2 data update: 1200 specimens, 18 orders, v4"
git push origin main
```

---

## Updating Only Metadata (no new data)

To change the app name, icon, version string, or tab labels without new CSV/PDF:

```bash
python scripts/bioatlas_updater.py ihr_bioatlas_v3.html \
  --version v3.1 \
  --name "IHR BIOATLAS" \
  --icon "🦋" \
  --badge "COI-5P · BOLD BIN · RF Classifier · Year 2" \
  --tab "map=🗺 Distribution Map" \
  --tab "analytics=📊 Analytics" \
  --out ihr_bioatlas_v3.1.html
```

---

## CSV Format Requirements

The updater expects the standard BOLD export format. Required columns:

```
Field ID, Sample ID, Process ID, Lat, Lon,
Species, Genus, Family, Order, Subfamily,
State/Province, Region, Exact Site, BIN,
Habitat, Life Stage, Collectors, Collection Date,
Elev, Identification, Match_Status,
Class, Phylum, COI-5P Seq. Length, Image Count
```

If column names change in a future BOLD export, edit the field mapping in
`scripts/bioatlas_updater.py` → `update_from_csv()` function.

---

## PDF Image Extraction

The updater uses PyMuPDF to extract specimen photographs from the sequencing
report PDF. Images are matched to specimen records by **Field ID** 
(format: `FDE_P1_A1`, `FDW_P2_B3`, etc.).

- Only records with a matching Field ID in the PDF will show popup images.
- The `Image Count` column in the CSV indicates expected image availability.
- Image extraction is slow (~30–120 seconds for a large PDF).
- Uncheck **"Update specimen images from PDF"** if you only need to update records.

---

## Version Naming Convention

| Version | Description |
|---|---|
| `v3` | Year 1 data (2025), 809 specimens |
| `v4` | Year 2 data (2026), expected ~1500 specimens |
| `v5` | Year 3 data (2027), final dataset |
| `v3.1` | Minor fix or metadata change to v3 |

---

## Troubleshooting the Updater

**"RECORDS block not found"**
→ The HTML structure changed. Ensure the source HTML contains `const RECORDS = [`

**"PyMuPDF not installed"**
→ Run `pip install PyMuPDF` and retry with PDF update enabled.

**Stats still showing old values**
→ Check that the IDs in the HTML match: `id="kpi-sp"`, `id="kpi-spp"`, etc.
   Run the updater again — it is safe to run multiple times.

**Output file is identical to source**
→ Ensure at least one update option is checked and the CSV/PDF paths are correct.
