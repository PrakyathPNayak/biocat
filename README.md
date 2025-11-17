# Biocat Database - Ensembl Data Population

A Python project to populate a biological database with taxonomic and genetic data from Ensembl and NCBI.

## Quick Start

### 1. Install Dependencies
```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or using regular pip
pip install -r requirements.txt
```

### 2. Setup Database
```bash
mysql -u root -p < create_biocat_db.sql
```

### 3. Configure
Edit `populate_ensembl_data_v2.py`:
- Update database credentials in `DB_CONFIG`
- Set your email in `Entrez.email`

### 4. Run Population

#### Option A: Run Complete Population (Taxonomy + Genetics)
```bash
uv run populate_ensembl_data_v2.py
```

#### Option B: Run Only Genetic Data Population  
```bash
# Simple version (creates mock data)
uv run populate_genetic_data.py

# Optimized version (handles duplicates, resumes)
uv run populate_genetic_optimized.py
```

#### Option C: Check Current Database Status
```bash
uv run check_database.py
```

## Testing

Test your setup before running the full population:

```bash
uv run test_setup.py
```

## What Gets Populated

### Genetic Data 
- **~4,000 genes** across 3 model organisms
- **~5,500 transcripts** with multiple variants per gene
- **~4,000 proteins** with full sequences
- **Distribution**: Human (2,651), Zebrafish (617), Mouse (381)

### Additional Data
- **Taxonomy**: NCBI taxonomy nodes with lineages
- **Assemblies**: Genome assembly information  
- **Chromosomes**: Chromosome data for each species

**Current Database Size**: 7.72 MB (well under 10GB limit)

## Requirements

- Python 3.8+
- MySQL 8.0+
- ~5GB disk space for library caches
- Internet connection for initial data download

## Expected Runtime

- First run: 30-60 minutes (downloads and caches data)
- Subsequent runs: 10-15 minutes (uses cached data)

## Database Size

Final database size: ~2-3 GB (under 10GB limit)

## File structure
biocat/\
├── README.md\
├── requirements.txt\
├── .gitignore\
├── sql/\
│   ├── create_biocat_db.sql\
│   ├── functions.sql\
│   ├── procedures.sql\
│   ├── triggers.sql\
│   └── sample_data.sql\
├── src/\
│   ├── app.py\
│   ├── database.py\
│   ├── sql_queries.py\
│   ├── dna_visualization.py\
│   ├── launch.py\
│   └── config_example.py\
├── docs/\
│   ├── DBMS_Project_Report.md\
│   ├── ER-diagram.pdf\
│   ├── Relational-Schema.pdf\
│   ├── INTERFACE_README.md\
│   ├── CUSTOM_FUNCTIONS.md\
│   └── screenshots/\
├── tests/\
│   └── test_custom_functions.py\
└── data/\
    └── sample_queries.txt\

## Dependencies
```tree
biocat-interface v0.1.0
├── biopython v1.86
│   └── numpy v2.3.4
├── gradio v5.49.1
│   ├── aiofiles v24.1.0
│   ├── anyio v4.11.0
│   │   ├── idna v3.11
│   │   ├── sniffio v1.3.1
│   │   └── typing-extensions v4.15.0
│   ├── brotli v1.1.0
│   ├── fastapi v0.120.4
│   │   ├── annotated-doc v0.0.3
│   │   ├── pydantic v2.11.10
│   │   │   ├── annotated-types v0.7.0
│   │   │   ├── pydantic-core v2.33.2
│   │   │   │   └── typing-extensions v4.15.0
│   │   │   ├── typing-extensions v4.15.0
│   │   │   └── typing-inspection v0.4.2
│   │   │       └── typing-extensions v4.15.0
│   │   ├── starlette v0.49.3
│   │   │   ├── anyio v4.11.0 (*)
│   │   │   └── typing-extensions v4.15.0
│   │   └── typing-extensions v4.15.0
│   ├── ffmpy v0.6.4
│   ├── gradio-client v1.13.3
│   │   ├── fsspec v2025.10.0
│   │   ├── httpx v0.28.1
│   │   │   ├── anyio v4.11.0 (*)
│   │   │   ├── certifi v2025.10.5
│   │   │   ├── httpcore v1.0.9
│   │   │   │   ├── certifi v2025.10.5
│   │   │   │   └── h11 v0.16.0
│   │   │   └── idna v3.11
│   │   ├── huggingface-hub v1.0.1
│   │   │   ├── filelock v3.20.0
│   │   │   ├── fsspec v2025.10.0
│   │   │   ├── hf-xet v1.2.0
│   │   │   ├── httpx v0.28.1 (*)
│   │   │   ├── packaging v25.0
│   │   │   ├── pyyaml v6.0.3
│   │   │   ├── shellingham v1.5.4
│   │   │   ├── tqdm v4.67.1
│   │   │   │   └── colorama v0.4.6
│   │   │   ├── typer-slim v0.20.0
│   │   │   │   ├── click v8.3.0
│   │   │   │   │   └── colorama v0.4.6
│   │   │   │   └── typing-extensions v4.15.0
│   │   │   └── typing-extensions v4.15.0
│   │   ├── packaging v25.0
│   │   ├── typing-extensions v4.15.0
│   │   └── websockets v15.0.1
│   ├── groovy v0.1.2
│   ├── httpx v0.28.1 (*)
│   ├── huggingface-hub v1.0.1 (*)
│   ├── jinja2 v3.1.6
│   │   └── markupsafe v3.0.3
│   ├── markupsafe v3.0.3
│   ├── numpy v2.3.4
│   ├── orjson v3.11.4
│   ├── packaging v25.0
│   ├── pandas v2.3.3
│   │   ├── numpy v2.3.4
│   │   ├── python-dateutil v2.9.0.post0
│   │   │   └── six v1.17.0
│   │   ├── pytz v2025.2
│   │   └── tzdata v2025.2
│   ├── pillow v11.3.0
│   ├── pydantic v2.11.10 (*)
│   ├── pydub v0.25.1
│   ├── python-multipart v0.0.20
│   ├── pyyaml v6.0.3
│   ├── ruff v0.14.3
│   ├── safehttpx v0.1.7
│   │   └── httpx v0.28.1 (*)
│   ├── semantic-version v2.10.0
│   ├── starlette v0.49.3 (*)
│   ├── tomlkit v0.13.3
│   ├── typer v0.20.0
│   │   ├── click v8.3.0 (*)
│   │   ├── rich v14.2.0
│   │   │   ├── markdown-it-py v4.0.0
│   │   │   │   └── mdurl v0.1.2
│   │   │   └── pygments v2.19.2
│   │   ├── shellingham v1.5.4
│   │   └── typing-extensions v4.15.0
│   ├── typing-extensions v4.15.0
│   └── uvicorn v0.38.0
│       ├── click v8.3.0 (*)
│       └── h11 v0.16.0
├── matplotlib v3.10.7
│   ├── contourpy v1.3.3
│   │   └── numpy v2.3.4
│   ├── cycler v0.12.1
│   ├── fonttools v4.60.1
│   ├── kiwisolver v1.4.9
│   ├── numpy v2.3.4
│   ├── packaging v25.0
│   ├── pillow v11.3.0
│   ├── pyparsing v3.2.5
│   └── python-dateutil v2.9.0.post0 (*)
├── mysql-connector-python v9.5.0
├── numpy v2.3.4
├── pandas v2.3.3 (*)
├── plotly v6.3.1
│   ├── narwhals v2.10.1
│   └── packaging v25.0
└── seaborn v0.13.2
    ├── matplotlib v3.10.7 (*)
    ├── numpy v2.3.4
    └── pandas v2.3.3 (*)
```
