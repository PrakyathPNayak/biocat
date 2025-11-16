# Biocat Database Interface

A comprehensive web-based interface for exploring biological data in the biocat database. Built with Gradio, this application provides interactive queries, visualizations, and analysis tools for genomic, proteomic, and functional annotation data.

## Features

### Database Connectivity
- Configurable MySQL database connections
- Connection testing and status monitoring
- Support for custom database configurations

### Query System
- **Predefined Queries**: Organized by category with optimized SQL queries
- **Custom MySQL Functions**: Three specialized functions for sequence analysis
  - `classify_sequence()` - Gene classification based on start codons
  - `count_nucleotides()` - Nucleotide frequency analysis with JSON output
  - `detect_mutations()` - Base-by-base sequence comparison
- **Custom Query Editor**: Execute custom SELECT statements with safety checks
- **Gene Search**: Fast search by gene symbol, name, or description
- **Parameter Support**: Dynamic query parameters for flexible filtering

### Data Visualization
- **DNA Sequence Analysis**: Nucleotide composition and GC content plots
- **Protein Analysis**: Amino acid composition and hydrophobicity profiles
- **Genomic Overviews**: Distribution plots and statistical summaries
- **Interactive Charts**: Plotly-powered visualizations with zoom and export

### Analysis Tools
- **Custom Function Testing**: Interactive interface for testing MySQL functions
- **Real Data Analysis**: Apply custom functions to biocat sequences
- Protein sequence property calculation
- DNA composition analysis
- Gene structure visualization
- Cross-species comparative analysis
- Functional annotation exploration

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL 8.0+ with biocat database
- Internet connection for package installation

### Quick Start

1. **Clone or Download**: Ensure you have all the interface files:
   ```
   biocat-interface/
   ├── app.py
   ├── database.py
   ├── sql_queries.py
   ├── dna_visualization.py
   ├── launch.py
   ├── requirements.txt
   └── INTERFACE_README.md
   ```

2. **Install Dependencies**: 
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install gradio pandas mysql-connector-python plotly biopython seaborn matplotlib numpy
   ```

3. **Launch the Interface**:
   ```bash
   python launch.py
   ```
   
   Or run directly:
   ```bash
   python app.py
   ```

4. **Access the Interface**: Open your browser to `http://localhost:7860`

## Database Setup

Ensure your biocat database is properly set up:

1. **Create Database**:
   ```bash
   mysql -u root -p < ../create_biocat_db.sql
   ```

2. **Add Custom Functions** (required for full functionality):
   ```bash
   mysql -u root -p biocat < ../functions.sql
   ```
   
   This adds three custom MySQL functions for sequence analysis:
   - `classify_sequence()` for gene classification
   - `count_nucleotides()` for composition analysis  
   - `detect_mutations()` for sequence comparison

3. **Verify Tables**: Check that tables exist and contain data

## Usage Guide

### 1. Database Connection
- Navigate to the "Database Connection" tab
- Enter your MySQL credentials
- Test the connection before proceeding
- Default settings work for local installations

### 2. Database Overview
- View basic statistics about your database
- See record counts for all major tables
- Understand the scope of available data

### 3. Query Explorer
- Browse predefined queries by category:
  - **Basic Statistics**: Database overview and summary statistics
  - **Gene Analysis**: Gene-focused queries and comparisons
  - **Protein Analysis**: Protein properties and distributions
  - **Sequence Analysis**: DNA/protein sequence exploration
  - **Comparative Analysis**: Cross-species comparisons
  - **Functional Annotation**: GO terms and pathway analysis
  - **Genomic Variation**: Variant analysis and effects

- Select a query and provide parameters as needed
- Set result limits to manage large datasets
- View automatic visualizations for supported queries

### 4. Custom Queries
- Write custom SQL SELECT statements
- Use for advanced analysis beyond predefined queries
- Safety checks prevent dangerous operations
- Results displayed in interactive tables

### 5. Gene Search
- Search by gene symbol (e.g., "BRCA1")
- Search by gene name (e.g., "breast cancer")
- Search by description keywords
- Results include genomic coordinates and annotations

### 6. Protein Analysis
- Enter protein stable IDs from your database
- View amino acid composition charts
- Analyze hydrophobicity profiles
- Get detailed protein properties

### 7. DNA Analysis
- Paste DNA sequences for analysis
- View nucleotide composition
- Analyze GC content across sliding windows
- Supports sequences of any length

## Available Query Categories

### Basic Statistics
- Database overview with record counts
- Species summary with gene/protein counts
- Chromosome statistics and gene density

### Gene Analysis
- Genes by biotype and species
- Longest genes across genomes
- Genes with multiple transcript variants
- Gene search functionality

### Protein Analysis
- Protein length distributions
- Largest proteins by species
- Protein property statistics
- Molecular weight and isoelectric point analysis

### Sequence Analysis
- Sequence classification using `classify_sequence()` function
- Nucleotide composition analysis with `count_nucleotides()` function
- Cross-sequence mutation detection with `detect_mutations()` function
- Mutation detection between sequences

### Comparative Analysis
- Species-to-species ortholog relationships
- Cross-species gene comparisons
- Evolutionary analysis metrics

### Functional Annotation
- GO term distributions
- Most common functional annotations
- Genes associated with specific GO terms

### Genomic Variation
- Variant type distributions
- Clinical significance analysis
- Chromosome-specific variant patterns

## Technical Details

### Architecture
- **Frontend**: Gradio web interface with multiple tabs
- **Backend**: Python with pandas for data processing
- **Database**: MySQL with mysql-connector-python
- **Visualization**: Plotly for interactive charts
- **Analysis**: BioPython for sequence analysis

### File Structure
- `app.py`: Main Gradio application
- `database.py`: Database connection and query handling
- `sql_queries.py`: Predefined SQL queries organized by category
- `dna_visualization.py`: Visualization and analysis functions
- `launch.py`: Launcher with dependency checking
- `requirements.txt`: Python package dependencies

### Database Schema Support
The interface supports the complete biocat schema including:
- Species and taxonomy information
- Genome assemblies and chromosomes
- Genes, transcripts, and proteins
- Genetic variants and annotations
- Functional annotations (GO, pathways, domains)
- Orthology relationships

## Customization

### Adding New Queries
1. Edit `sql_queries.py`
2. Add queries to appropriate category dictionaries
3. Use parameterized queries for user input
4. Test queries before deployment

### Custom Visualizations
1. Modify `dna_visualization.py`
2. Add new plotting functions
3. Update `app.py` to call new visualizations
4. Use Plotly for interactive charts

### Database Configuration
1. Modify default settings in `database.py`
2. Update connection parameters
3. Add custom database-specific functions

## Troubleshooting

### Connection Issues
- Verify MySQL server is running
- Check database credentials
- Ensure biocat database exists
- Test connection manually with mysql client

### Missing Dependencies
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)
- Use virtual environment if needed

### Query Errors
- Check database schema matches expectations
- Verify table names and column names
- Review parameter formats for custom queries

### Performance Issues
- Reduce result limits for large queries
- Add database indexes for frequently queried columns
- Use connection pooling for high usage

## Security Notes

- Only SELECT queries are allowed in custom query editor
- SQL injection protection through parameterized queries
- No database modification capabilities in the interface
- Connection credentials are handled securely

## Development

### Requirements for Development
- Python 3.8+
- All packages in requirements.txt
- MySQL database with biocat schema
- Code editor with Python support

### Testing
- Test with sample data first
- Verify all query categories work
- Check visualization rendering
- Test with different database sizes

### Contributing
- Follow Python PEP 8 style guidelines
- Add docstrings to new functions
- Test new features thoroughly
- Update this README for new capabilities

## Support

For issues with the interface:
1. Check the troubleshooting section
2. Verify database setup and connectivity
3. Review error messages in the interface
4. Check Python console for detailed errors

For database issues:
1. Verify biocat schema is properly installed
2. Check data population status
3. Review MySQL error logs
4. Ensure proper user permissions

## License

This interface is designed for educational and research purposes. Please ensure compliance with your institution's data usage policies.