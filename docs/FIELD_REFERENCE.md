# CSV Column Reference

Full column reference for the BOLD export CSV used by IHR BioAtlas.

## Columns used by the updater

| CSV Column | JSON field in RECORDS | Description |
|---|---|---|
| `Field ID` | `fieldId` | Unique field specimen identifier (e.g. `FDE_P1_A1`) |
| `Sample ID` | `sampleId` | Sequencing sample ID (e.g. `ON-ZSI001-01-A01`) |
| `Process ID` | `processId` | BOLD process ID (e.g. `ONTOL024-26`) |
| `Lat` | `lat` | Decimal latitude |
| `Lon` | `lon` | Decimal longitude |
| `Species` | `species` | Species epithet |
| `Genus` | `genus` | Genus name |
| `Family` | `family` | Family name |
| `Order` | `order` | Order name |
| `Subfamily` | `subfamily` | Subfamily name |
| `State/Province` | `state` | Collecting state |
| `Region` | `region` | Sub-region or sector |
| `Exact Site` | `locality` | Collecting locality name |
| `BIN` | `bin` | BOLD Barcode Index Number (e.g. `BOLD:AAE9516`) |
| `Habitat` | `habitat` | Habitat description |
| `Life Stage` | `lifeStage` | Adult / Larva / Pupa etc. |
| `Collectors` | `collector` | Collector initials or name |
| `Collection Date` | `collDate` | Collection date string |
| `Elev` | `elev` | Elevation in metres |
| `Identification` | `identification` | Full identification string |
| `Match_Status` | `matchStatus` | BOLD match result status |
| `Class` | `class` | Taxonomic class |
| `Phylum` | `phylum` | Taxonomic phylum |
| `COI-5P Seq. Length` | `seqLength` | COI-5P sequence length |
| `Image Count` | *(stat only)* | Number of specimen images in PDF |

## Columns used for statistics only

| CSV Column | Statistic computed |
|---|---|
| `Order` | ORDER_STATS, header Orders counter |
| `Species` | Unique species count |
| `Genus` | Unique genera count |
| `Family` | Unique families count |
| `BIN` | Total BINs assigned |
| `Image Count` | "With Images" header counter |

## Sector codes in Field ID

Field IDs encode the biogeographic sector:

| Prefix | Sector |
|---|---|
| `FDW_` | Western — Himachal Pradesh (GHNP) |
| `FDC_` | Central — West Bengal (SNP) |
| `FDE_` | Eastern — Arunachal Pradesh |

## Match_Status values

| Value | Meaning |
|---|---|
| `MATCHED via Field ID` | Record matched to PDF image via Field ID |
| `MATCHED via Sample ID` | Record matched to PDF image via Sample ID |
| `NO MATCH` | No corresponding image found in PDF |
| *(blank)* | Match not attempted |

## Notes

- `Lat` / `Lon` must be decimal degrees (WGS84). Records with missing or
  invalid coordinates will be excluded from the map but retained in the table.
- `BIN` format: `BOLD:XXXXXXX` — records without a BIN assignment appear
  as unresolved in the Analytics panel.
- The `Image Count` column is set by the BOLD export and indicates how many
  specimen photos were submitted. It does not guarantee the image appears in
  the PDF.
