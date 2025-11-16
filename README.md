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

## Libraries Used

- **PyEnsembl** - Ensembl genome data access
- **ETE3** - NCBI taxonomy database
- **Biopython** - Additional biological data access
- **mysql-connector-python** - Database connectivity
