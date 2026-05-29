#!/usr/bin/env python3
"""
IHR BioAtlas HTML Updater
=========================
Updates the standalone IHR BioAtlas HTML file from:
  - A new CSV  (specimen records + stats)
  - A new PDF  (specimen photograph images)
  - App metadata (version, name, icon/emoji, tab labels, subtitle, badge)

Requirements:
    pip install pandas PyMuPDF
"""

import os
import sys
import json
import re
import base64
import shutil
import pandas as pd
from pathlib import Path
from datetime import datetime

# ─── Try GUI import; fall back to CLI ────────────────────────────────────────
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    HAS_TK = True
except ImportError:
    HAS_TK = False

try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

# ─── Core update logic ────────────────────────────────────────────────────────

def load_html(html_path: str) -> str:
    with open(html_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def save_html(html_path: str, content: str):
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)


def bump_version(content: str, new_version: str) -> str:
    """Update version string everywhere in the HTML."""
    # Title tag
    content = re.sub(
        r'(<title>.*?BioAtlas\s*)v[\d\.]+',
        lambda m: m.group(1) + new_version,
        content
    )
    # Any other visible vN references in the header badge area
    content = re.sub(
        r'(BioAtlas\s*)v[\d\.]+',
        lambda m: m.group(1) + new_version,
        content
    )
    return content


def update_app_name(content: str, new_name: str) -> str:
    """Update the brand name shown in the header and loading screen."""
    # Loading screen logo
    content = re.sub(
        r'(<div class="ld-logo">)([^<]+)(</div>)',
        lambda m: m.group(1) + new_name.upper() + m.group(3),
        content
    )
    # Header brand name
    content = re.sub(
        r'(<div class="brand-name">)([^<]+)(</div>)',
        lambda m: m.group(1) + new_name.upper() + m.group(3),
        content
    )
    # Page <title> (replace first word-group before "—")
    content = re.sub(
        r'(<title>)[^—<]+(—)',
        lambda m: m.group(1) + new_name + " " + m.group(2),
        content
    )
    return content


def update_subtitle(content: str, new_subtitle: str) -> str:
    """Update the brand subtitle line under the app name."""
    content = re.sub(
        r'(<div class="brand-sub">)([^<]+)(</div>)',
        lambda m: m.group(1) + new_subtitle + m.group(3),
        content
    )
    return content


def update_loading_sub(content: str, new_sub: str) -> str:
    """Update the loading screen subtitle."""
    content = re.sub(
        r'(<div class="ld-sub">)([^<]+)(</div>)',
        lambda m: m.group(1) + new_sub + m.group(3),
        content
    )
    return content


def update_icon(content: str, new_icon: str) -> str:
    """Replace the brand emblem emoji/text."""
    content = re.sub(
        r'(<div class="brand-emblem">)([^<]+)(</div>)',
        lambda m: m.group(1) + new_icon + m.group(3),
        content
    )
    return content


def update_badge(content: str, new_badge: str) -> str:
    """Update the header-badge text (e.g. 'COI-5P · BOLD BIN · RF Classifier')."""
    content = re.sub(
        r'(<div class="header-badge">)([^<]+)(</div>)',
        lambda m: m.group(1) + new_badge + m.group(3),
        content
    )
    return content


def update_tab_labels(content: str, tab_map: dict) -> str:
    """
    tab_map = {
        "map":       "🗺 My Custom Label",
        "analytics": "📊 Analytics",
        ...
    }
    """
    for data_p, new_label in tab_map.items():
        content = re.sub(
            rf'(<div class="tab[^"]*" data-p="{re.escape(data_p)}">)([^<]+)(</div>)',
            lambda m, l=new_label: m.group(1) + l + m.group(3),
            content
        )
    return content


def update_from_csv(content: str, csv_path: str, log=print) -> str:
    """Recompute RECORDS, ORDER_STATS, and all stat counters from a CSV file."""
    log(f"  Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    log(f"  Loaded {len(df)} rows, columns: {df.columns.tolist()}")

    # ── Build RECORDS ──────────────────────────────────────────────────────
    records = []
    for _, row in df.iterrows():
        try:
            lat = float(row["Lat"]) if pd.notna(row.get("Lat")) else None
            lon = float(row["Lon"]) if pd.notna(row.get("Lon")) else None
        except Exception:
            lat = lon = None

        def s(col):
            v = row.get(col)
            return str(v) if pd.notna(v) else ""

        def n(col):
            v = row.get(col)
            try:
                return float(v) if pd.notna(v) else None
            except Exception:
                return None

        records.append({
            "fieldId":      s("Field ID"),
            "sampleId":     s("Sample ID"),
            "processId":    s("Process ID"),
            "lat":          lat,
            "lon":          lon,
            "species":      s("Species"),
            "genus":        s("Genus"),
            "family":       s("Family"),
            "order":        s("Order"),
            "subfamily":    s("Subfamily"),
            "state":        s("State/Province"),
            "region":       s("Region"),
            "locality":     s("Exact Site"),
            "bin":          s("BIN"),
            "habitat":      s("Habitat"),
            "lifeStage":    s("Life Stage"),
            "collector":    s("Collectors"),
            "collDate":     s("Collection Date"),
            "elev":         n("Elev"),
            "identification": s("Identification"),
            "matchStatus":  s("Match_Status"),
            "class":        s("Class"),
            "phylum":       s("Phylum"),
            "seqLength":    s("COI-5P Seq. Length"),
        })

    new_records_str = "const RECORDS = " + json.dumps(records, separators=(",", ":")) + ";"
    idx_s = content.find("const RECORDS = [")
    idx_e = content.find("];", idx_s) + 2
    if idx_s == -1:
        log("  ⚠ RECORDS block not found — skipped.")
    else:
        content = content[:idx_s] + new_records_str + content[idx_e:]
        log(f"  ✓ RECORDS updated: {len(records)} records")

    # ── Compute stats ──────────────────────────────────────────────────────
    total_sp  = len(df)
    total_spp = int(df["Species"].dropna().nunique())
    total_gen = int(df["Genus"].dropna().nunique())
    total_fam = int(df["Family"].dropna().nunique())
    total_ord = int(df["Order"].dropna().nunique())
    img_col   = "Image Count"
    total_img = int((df[img_col] > 0).sum()) if img_col in df.columns else total_sp
    total_bin = int(df["BIN"].dropna().nunique())

    log(f"  Stats → sp:{total_sp} spp:{total_spp} gen:{total_gen} fam:{total_fam} "
        f"ord:{total_ord} img:{total_img} bin:{total_bin}")

    # ── Build ORDER_STATS ─────────────────────────────────────────────────
    order_stats = []
    for order, grp in df.groupby("Order"):
        order_stats.append({
            "order":     order,
            "specimens": len(grp),
            "genera":    int(grp["Genus"].dropna().nunique()),
            "species":   int(grp["Species"].dropna().nunique()),
            "families":  int(grp["Family"].dropna().nunique()),
        })
    order_stats.sort(key=lambda x: -x["specimens"])

    lines = ["const ORDER_STATS = ["]
    for o in order_stats:
        lines.append(
            f'  {{order:"{o["order"]}",specimens:{o["specimens"]},'
            f'genera:{o["genera"]},species:{o["species"]},families:{o["families"]}}},'
        )
    if lines[-1].endswith(","):
        lines[-1] = lines[-1].rstrip(",")
    lines.append("];")
    new_os = "\n".join(lines)

    os_s = content.find("const ORDER_STATS = [")
    os_e = content.find("];", os_s) + 2
    if os_s == -1:
        log("  ⚠ ORDER_STATS block not found — skipped.")
    else:
        content = content[:os_s] + new_os + content[os_e:]
        log(f"  ✓ ORDER_STATS updated: {len(order_stats)} orders")

    # ── Patch all stat display targets ────────────────────────────────────
    patches = {
        # Header stats
        'id="hs-sp">':    (r'id="hs-sp">\d+', f'id="hs-sp">{total_sp}'),
        # Analytics KPI cards (look for id="kpi-*")
        'id="kpi-sp">':   (r'id="kpi-sp">\d+',  f'id="kpi-sp">{total_sp}'),
        'id="kpi-spp">':  (r'id="kpi-spp">\d+', f'id="kpi-spp">{total_spp}'),
        'id="kpi-gen">':  (r'id="kpi-gen">\d+', f'id="kpi-gen">{total_gen}'),
        'id="kpi-fam">':  (r'id="kpi-fam">\d+', f'id="kpi-fam">{total_fam}'),
        'id="kpi-ord">':  (r'id="kpi-ord">\d+', f'id="kpi-ord">{total_ord}'),
    }
    for key, (pattern, repl) in patches.items():
        new_c, n_subs = re.subn(pattern, repl, content)
        if n_subs:
            content = new_c
            log(f"  ✓ Patched {key} → {repl.split('>')[-1]}")

    # Header stat cards (Species, Genera, Families, Orders, With Images)
    # They're plain text numbers inside .h-stat-n divs in sequence
    header_stats = [
        ("Specimens",  total_sp),
        ("Species",    total_spp),
        ("Genera",     total_gen),
        ("Families",   total_fam),
        ("Orders",     total_ord),
        ("With Images", total_img),
    ]
    for label, value in header_stats:
        pattern = rf'(<div class="h-stat-n"[^>]*>)\d+(<\/div><div class="h-stat-l">{re.escape(label)}<\/div>)'
        content, n = re.subn(pattern, lambda m, v=value: m.group(1) + str(v) + m.group(2), content)
        if n:
            log(f"  ✓ Header stat '{label}' → {value}")

    # Text references like "809 records", "809 georeferenced specimen records"
    for old_n in set(re.findall(r'\b(\d{3,4})\b(?= records| georeferenced)', content)):
        if old_n.isdigit():
            content = re.sub(
                rf'\b{old_n}\b( records| georeferenced)',
                f'{total_sp}\\1',
                content
            )
    # "Master specimen data (NNN+ rows)"
    content = re.sub(
        r'Master specimen data \(\d+\+? rows\)',
        f'Master specimen data ({total_sp}+ rows)',
        content
    )
    # Troubleshoot image match text "Only NNN of NNN records have matched"
    content = re.sub(
        r'Only \d+ of \d+ records have matched PDF images',
        f'Only {total_img} of {total_sp} records have matched PDF images',
        content
    )

    log(f"  ✓ CSV update complete")
    return content


def extract_pdf_images(pdf_path: str, log=print) -> dict:
    """
    Extract specimen images from the PDF.
    Returns dict mapping fieldId → base64 JPEG string.
    """
    if not HAS_FITZ:
        log("  ⚠ PyMuPDF not installed — PDF image extraction skipped.")
        log("    Install: pip install PyMuPDF")
        return {}

    log(f"  Reading PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    log(f"  PDF has {len(doc)} pages")

    images = {}
    for page_num, page in enumerate(doc):
        page_text = page.get_text()
        # Extract any Field IDs on this page
        field_ids = re.findall(r'FD[A-Z]_P\d+_[A-Z]\d+', page_text)
        sample_ids = re.findall(r'ON-ZSI\d{3}-\d{2}-[A-Z]\d{2}', page_text)

        # Get images on this page
        img_list = page.get_images(full=True)
        if not img_list:
            continue

        for img_idx, img_info in enumerate(img_list):
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            ext = base_image["ext"]

            # Associate with field IDs found on same page
            for fid in field_ids:
                images[fid] = (ext, img_b64)
                log(f"    Page {page_num+1}: extracted image for {fid}")
            for sid in sample_ids:
                images[sid] = (ext, img_b64)

    doc.close()
    log(f"  ✓ Extracted {len(images)} images from PDF")
    return images


def update_pdf_images_in_html(content: str, images: dict, log=print) -> str:
    """
    Inject base64 images into the IMAGE_DATA const in the HTML.
    Expects a `const IMAGE_DATA = {...};` block.
    """
    if not images:
        return content

    # Convert to format: { "FDE_P1_A1": "data:image/jpeg;base64,..." }
    image_data = {}
    for key, (ext, b64) in images.items():
        mime = "image/jpeg" if ext.lower() in ("jpg", "jpeg") else f"image/{ext.lower()}"
        image_data[key] = f"data:{mime};base64,{b64}"

    new_image_data_str = "const IMAGE_DATA = " + json.dumps(image_data, separators=(",", ":")) + ";"

    idx_s = content.find("const IMAGE_DATA = {")
    if idx_s == -1:
        # Not present — inject it just before RECORDS
        idx_r = content.find("const RECORDS = [")
        if idx_r != -1:
            content = content[:idx_r] + new_image_data_str + "\n" + content[idx_r:]
            log(f"  ✓ IMAGE_DATA injected ({len(image_data)} images)")
        else:
            log("  ⚠ Could not find injection point for IMAGE_DATA")
    else:
        idx_e = content.find("};", idx_s) + 2
        content = content[:idx_s] + new_image_data_str + content[idx_e:]
        log(f"  ✓ IMAGE_DATA updated ({len(image_data)} images)")

    return content


def make_backup(html_path: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = html_path.replace(".html", f"_backup_{ts}.html")
    shutil.copy2(html_path, backup)
    return backup


# ─── GUI ──────────────────────────────────────────────────────────────────────

class BioAtlasUpdaterGUI:
    def __init__(self, root):
        self.root = root
        root.title("IHR BioAtlas HTML Updater")
        root.geometry("780x720")
        root.resizable(True, True)
        root.configure(bg="#1a1a2e")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._apply_styles()
        self._build_ui()

    def _apply_styles(self):
        bg    = "#1a1a2e"
        card  = "#16213e"
        gold  = "#d4a843"
        text  = "#e8e0d0"
        entry = "#0f3460"

        self.style.configure("TFrame",       background=bg)
        self.style.configure("Card.TFrame",  background=card, relief="flat")
        self.style.configure("TLabel",       background=bg,   foreground=text, font=("Segoe UI", 10))
        self.style.configure("Head.TLabel",  background=bg,   foreground=gold, font=("Segoe UI", 11, "bold"))
        self.style.configure("Card.TLabel",  background=card, foreground=text, font=("Segoe UI", 10))
        self.style.configure("TEntry",       fieldbackground=entry, foreground=text, insertcolor=gold)
        self.style.configure("Gold.TButton", background=gold, foreground="#1a1a2e", font=("Segoe UI", 10, "bold"), padding=6)
        self.style.map("Gold.TButton",       background=[("active", "#e8c060")])
        self.style.configure("TButton",      background="#2a2a4e", foreground=text, font=("Segoe UI", 9), padding=4)
        self.style.map("TButton",            background=[("active", "#3a3a6e")])
        self.style.configure("TSeparator",   background="#2a2a4e")

    def _section(self, parent, title):
        f = ttk.Frame(parent, style="Card.TFrame", padding=10)
        f.pack(fill="x", padx=10, pady=4)
        ttk.Label(f, text=title, style="Head.TLabel").pack(anchor="w", pady=(0, 6))
        return f

    def _file_row(self, parent, label, var, filetypes, bg="Card.TFrame"):
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x", pady=2)
        ttk.Label(row, text=label, style="Card.TLabel", width=14).pack(side="left")
        e = ttk.Entry(row, textvariable=var, width=48)
        e.pack(side="left", padx=(0, 6))
        ttk.Button(row, text="Browse…",
                   command=lambda v=var, ft=filetypes: self._browse(v, ft)
                   ).pack(side="left")

    def _browse(self, var, filetypes):
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            var.set(path)

    def _labeled_entry(self, parent, label, var, width=40):
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x", pady=2)
        ttk.Label(row, text=label, style="Card.TLabel", width=18).pack(side="left")
        ttk.Entry(row, textvariable=var, width=width).pack(side="left")

    def _build_ui(self):
        bg = "#1a1a2e"
        # ── Title bar ──────────────────────────────────────────────────────
        title_f = tk.Frame(self.root, bg="#0d1b2a", pady=10)
        title_f.pack(fill="x")
        tk.Label(title_f, text="🏔  IHR BioAtlas HTML Updater",
                 bg="#0d1b2a", fg="#d4a843",
                 font=("Segoe UI", 16, "bold")).pack()
        tk.Label(title_f, text="Zoological Survey of India  ·  Oxford Nanopore × Random Forest",
                 bg="#0d1b2a", fg="#8899aa",
                 font=("Segoe UI", 9)).pack()

        # ── Scrollable area ────────────────────────────────────────────────
        canvas = tk.Canvas(self.root, bg=bg, highlightthickness=0)
        scroll = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        self.scroll_frame = ttk.Frame(canvas, style="TFrame")
        self.scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True, padx=4)
        scroll.pack(side="right", fill="y")

        sf = self.scroll_frame  # shorthand

        # ── Section 1: Files ───────────────────────────────────────────────
        s1 = self._section(sf, "① File Paths")

        self.html_var = tk.StringVar()
        self.csv_var  = tk.StringVar()
        self.pdf_var  = tk.StringVar()
        self.out_var  = tk.StringVar()

        self._file_row(s1, "Source HTML", self.html_var,
                       [("HTML files", "*.html"), ("All", "*.*")])
        self._file_row(s1, "CSV (records)", self.csv_var,
                       [("CSV files", "*.csv"), ("All", "*.*")])
        self._file_row(s1, "PDF (images)", self.pdf_var,
                       [("PDF files", "*.pdf"), ("All", "*.*")])

        row_out = ttk.Frame(s1, style="Card.TFrame")
        row_out.pack(fill="x", pady=2)
        ttk.Label(row_out, text="Output HTML", style="Card.TLabel", width=14).pack(side="left")
        ttk.Entry(row_out, textvariable=self.out_var, width=48).pack(side="left", padx=(0, 6))
        ttk.Button(row_out, text="Browse…",
                   command=lambda: self.out_var.set(
                       filedialog.asksaveasfilename(
                           defaultextension=".html",
                           filetypes=[("HTML files", "*.html")])
                   )).pack(side="left")

        tk.Label(s1, text="Leave Output HTML empty to overwrite source (a backup is made automatically).",
                 bg="#16213e", fg="#778899", font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))

        # ── Section 2: Version ─────────────────────────────────────────────
        s2 = self._section(sf, "② Version")
        self.version_var = tk.StringVar(value="v3")
        self._labeled_entry(s2, "Version string", self.version_var, width=14)
        tk.Label(s2, text='e.g.  v3  v3.1  v2024-10  (replaces existing version tag in title & headings)',
                 bg="#16213e", fg="#778899", font=("Segoe UI", 8)).pack(anchor="w")

        # ── Section 3: App identity ────────────────────────────────────────
        s3 = self._section(sf, "③ App Identity (Name · Icon · Subtitle)")
        self.name_var    = tk.StringVar(value="IHR BIOATLAS")
        self.icon_var    = tk.StringVar(value="🏔")
        self.sub_var     = tk.StringVar(value="Zoological Survey of India · Oxford Nanopore × Random Forest")
        self.loadsub_var = tk.StringVar(value="Indian Himalayan Region · Zoological Survey of India")
        self.badge_var   = tk.StringVar(value="COI-5P · BOLD BIN · RF Classifier")

        self._labeled_entry(s3, "App name",        self.name_var,    width=36)
        self._labeled_entry(s3, "Brand icon/emoji", self.icon_var,   width=8)
        self._labeled_entry(s3, "Brand subtitle",  self.sub_var,     width=56)
        self._labeled_entry(s3, "Loading subtitle", self.loadsub_var, width=56)
        self._labeled_entry(s3, "Header badge",    self.badge_var,   width=46)

        # ── Section 4: Tab labels ──────────────────────────────────────────
        s4 = self._section(sf, "④ Navigation Tab Labels")
        self.tab_vars = {}
        default_tabs = {
            "map":       "🗺 Distribution Map",
            "analytics": "📊 Analytics",
            "ml":        "🤖 ML Prediction",
            "data":      "📋 Specimen Data",
            "about":     "📄 About",
            "ts":        "🔧 Troubleshoot",
        }
        for data_p, default_label in default_tabs.items():
            v = tk.StringVar(value=default_label)
            self.tab_vars[data_p] = v
            row = ttk.Frame(s4, style="Card.TFrame")
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=f"data-p={data_p}", style="Card.TLabel", width=16,
                      font=("Courier", 9)).pack(side="left")
            ttk.Entry(row, textvariable=v, width=36).pack(side="left")

        # ── Section 5: Update options ──────────────────────────────────────
        s5 = self._section(sf, "⑤ What to Update")
        self.do_csv    = tk.BooleanVar(value=True)
        self.do_pdf    = tk.BooleanVar(value=False)
        self.do_meta   = tk.BooleanVar(value=True)
        self.do_backup = tk.BooleanVar(value=True)

        for var, label in [
            (self.do_csv,    "Update records & stats from CSV"),
            (self.do_pdf,    "Update specimen images from PDF  (slow — may take 30–120s)"),
            (self.do_meta,   "Update app name / version / icon / tabs"),
            (self.do_backup, "Create timestamped backup before overwriting"),
        ]:
            cb = tk.Checkbutton(s5, text=label, variable=var,
                                bg="#16213e", fg="#e8e0d0",
                                selectcolor="#0f3460", activebackground="#16213e",
                                font=("Segoe UI", 10))
            cb.pack(anchor="w")

        # ── Run button ─────────────────────────────────────────────────────
        btn_f = ttk.Frame(sf, style="TFrame")
        btn_f.pack(fill="x", padx=10, pady=8)
        ttk.Button(btn_f, text="▶  Run Update",
                   style="Gold.TButton",
                   command=self.run_update).pack(fill="x", ipady=4)

        # ── Log window ────────────────────────────────────────────────────
        log_f = ttk.Frame(sf, style="Card.TFrame", padding=8)
        log_f.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        ttk.Label(log_f, text="Log", style="Head.TLabel").pack(anchor="w")
        self.log_box = scrolledtext.ScrolledText(
            log_f, height=12, bg="#0d1b2a", fg="#a8d8a0",
            font=("Courier New", 9), state="disabled",
            insertbackground="#d4a843")
        self.log_box.pack(fill="both", expand=True)

    def log(self, msg: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        self.root.update_idletasks()

    def run_update(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

        html_path = self.html_var.get().strip()
        csv_path  = self.csv_var.get().strip()
        pdf_path  = self.pdf_var.get().strip()
        out_path  = self.out_var.get().strip() or html_path

        if not html_path:
            messagebox.showerror("Missing", "Please select the source HTML file.")
            return

        self.log(f"{'='*60}")
        self.log(f"BioAtlas Updater  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"{'='*60}")
        self.log(f"Source: {html_path}")
        self.log(f"Output: {out_path}")

        try:
            content = load_html(html_path)
            self.log(f"Loaded HTML ({len(content):,} chars)")

            if self.do_backup.get() and os.path.abspath(out_path) == os.path.abspath(html_path):
                bk = make_backup(html_path)
                self.log(f"Backup created: {os.path.basename(bk)}")

            if self.do_csv.get():
                if not csv_path:
                    self.log("⚠ CSV path empty — skipping CSV update.")
                else:
                    self.log("\n[CSV Update]")
                    content = update_from_csv(content, csv_path, log=self.log)

            if self.do_pdf.get():
                if not pdf_path:
                    self.log("⚠ PDF path empty — skipping PDF update.")
                elif not HAS_FITZ:
                    self.log("⚠ PyMuPDF not installed (pip install PyMuPDF).")
                else:
                    self.log("\n[PDF Image Extraction]")
                    imgs = extract_pdf_images(pdf_path, log=self.log)
                    content = update_pdf_images_in_html(content, imgs, log=self.log)

            if self.do_meta.get():
                self.log("\n[Metadata Update]")
                ver = self.version_var.get().strip()
                if ver:
                    content = bump_version(content, ver)
                    self.log(f"  ✓ Version → {ver}")

                name = self.name_var.get().strip()
                if name:
                    content = update_app_name(content, name)
                    self.log(f"  ✓ Name → {name}")

                icon = self.icon_var.get().strip()
                if icon:
                    content = update_icon(content, icon)
                    self.log(f"  ✓ Icon → {icon}")

                sub = self.sub_var.get().strip()
                if sub:
                    content = update_subtitle(content, sub)
                    self.log(f"  ✓ Subtitle → {sub}")

                loadsub = self.loadsub_var.get().strip()
                if loadsub:
                    content = update_loading_sub(content, loadsub)
                    self.log(f"  ✓ Loading subtitle → {loadsub}")

                badge = self.badge_var.get().strip()
                if badge:
                    content = update_badge(content, badge)
                    self.log(f"  ✓ Badge → {badge}")

                tab_map = {k: v.get().strip() for k, v in self.tab_vars.items() if v.get().strip()}
                if tab_map:
                    content = update_tab_labels(content, tab_map)
                    self.log(f"  ✓ Tab labels updated")

            save_html(out_path, content)
            self.log(f"\n{'='*60}")
            self.log(f"✅ Saved: {out_path}  ({len(content):,} chars)")
            self.log(f"{'='*60}")
            messagebox.showinfo("Done", f"Updated HTML saved:\n{out_path}")

        except Exception as exc:
            self.log(f"\n❌ ERROR: {exc}")
            import traceback
            self.log(traceback.format_exc())
            messagebox.showerror("Error", str(exc))


# ─── CLI fallback ─────────────────────────────────────────────────────────────

def cli_run():
    import argparse
    parser = argparse.ArgumentParser(
        description="IHR BioAtlas HTML Updater (CLI mode)"
    )
    parser.add_argument("html",            help="Source HTML file")
    parser.add_argument("--csv",           help="CSV with specimen records")
    parser.add_argument("--pdf",           help="PDF with specimen images")
    parser.add_argument("--out",           help="Output HTML (default: overwrite source)")
    parser.add_argument("--version",       help="New version string, e.g. v3")
    parser.add_argument("--name",          help="App name")
    parser.add_argument("--icon",          help="Brand emblem emoji/text")
    parser.add_argument("--subtitle",      help="Brand subtitle line")
    parser.add_argument("--loading-sub",   help="Loading screen subtitle")
    parser.add_argument("--badge",         help="Header badge text")
    parser.add_argument("--tab",  action="append", metavar="data_p=Label",
                        help="Override a tab label (repeatable). E.g. --tab map='🗺 Map'")
    parser.add_argument("--no-backup", action="store_true",
                        help="Skip creating a backup")
    args = parser.parse_args()

    out_path = args.out or args.html
    log = print

    content = load_html(args.html)
    log(f"Loaded {args.html} ({len(content):,} chars)")

    if not args.no_backup and os.path.abspath(out_path) == os.path.abspath(args.html):
        bk = make_backup(args.html)
        log(f"Backup: {bk}")

    if args.csv:
        log("\n[CSV Update]")
        content = update_from_csv(content, args.csv, log=log)

    if args.pdf:
        log("\n[PDF Image Extraction]")
        imgs = extract_pdf_images(args.pdf, log=log)
        content = update_pdf_images_in_html(content, imgs, log=log)

    # Metadata
    if args.version:
        content = bump_version(content, args.version)
        log(f"Version → {args.version}")
    if args.name:
        content = update_app_name(content, args.name)
        log(f"Name → {args.name}")
    if args.icon:
        content = update_icon(content, args.icon)
        log(f"Icon → {args.icon}")
    if args.subtitle:
        content = update_subtitle(content, args.subtitle)
        log(f"Subtitle → {args.subtitle}")
    if args.loading_sub:
        content = update_loading_sub(content, args.loading_sub)
        log(f"Loading sub → {args.loading_sub}")
    if args.badge:
        content = update_badge(content, args.badge)
        log(f"Badge → {args.badge}")
    if args.tab:
        tab_map = {}
        for t in args.tab:
            k, _, v = t.partition("=")
            tab_map[k.strip()] = v.strip().strip("'\"")
        content = update_tab_labels(content, tab_map)
        log(f"Tabs → {tab_map}")

    save_html(out_path, content)
    log(f"\n✅ Saved: {out_path}  ({len(content):,} chars)")


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Arguments provided → CLI mode
        cli_run()
    elif HAS_TK:
        root = tk.Tk()
        app = BioAtlasUpdaterGUI(root)
        root.mainloop()
    else:
        print("No arguments given and Tkinter not available.")
        print("Usage: python bioatlas_updater.py <html> [--csv FILE] [--pdf FILE] [--version v4] ...")
        sys.exit(1)
