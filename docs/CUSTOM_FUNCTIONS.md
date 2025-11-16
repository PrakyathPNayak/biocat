# Custom MySQL Functions in Biocat Database

This document describes the custom MySQL functions available in the biocat database and how to use them through the interface.

## Overview

The biocat database includes three powerful custom MySQL functions designed specifically for biological sequence analysis:

1. **`classify_sequence()`** - Sequence classification based on start codons
2. **`count_nucleotides()`** - Nucleotide frequency analysis
3. **`detect_mutations()`** - Sequence comparison and mutation detection

## Function Descriptions

### 1. classify_sequence(dna_sequence TEXT)

**Purpose**: Classifies DNA sequences based on the presence of start codons (ATG).

**Parameters**:
- `dna_sequence`: A TEXT field containing DNA sequence data

**Returns**: VARCHAR(20)
- `'Likely Gene'` if the sequence contains ATG
- `'Unknown'` if no ATG is found

**Example Usage**:
```sql
SELECT classify_sequence('ATGGCATAG') as classification;
-- Returns: 'Likely Gene'

SELECT classify_sequence('GCTAGC') as classification;
-- Returns: 'Unknown'
```

### 2. count_nucleotides(dna_sequence TEXT)

**Purpose**: Counts the frequency of each nucleotide (A, T, G, C) in a DNA sequence.

**Parameters**:
- `dna_sequence`: A TEXT field containing DNA sequence data

**Returns**: JSON
- JSON object with keys 'A', 'T', 'G', 'C' and their respective counts

**Example Usage**:
```sql
SELECT count_nucleotides('ATCGATCG') as composition;
-- Returns: {"A": 2, "C": 2, "G": 2, "T": 2}

SELECT count_nucleotides('AAATTTCCCGGG') as composition;
-- Returns: {"A": 3, "C": 3, "G": 3, "T": 3}
```

### 3. detect_mutations(seq1 TEXT, seq2 TEXT)

**Purpose**: Compares two DNA sequences base-by-base and identifies mutation positions.

**Parameters**:
- `seq1`: First DNA sequence for comparison
- `seq2`: Second DNA sequence for comparison

**Returns**: TEXT
- Detailed description of mutations found with positions
- `'No mutations found'` if sequences are identical

**Example Usage**:
```sql
SELECT detect_mutations('ATCGATCG', 'ATCGATCC') as mutations;
-- Returns: 'Pos 8: G->C; '

SELECT detect_mutations('ATCGATCG', 'GTCAATCG') as mutations;
-- Returns: 'Pos 1: A->G; Pos 4: G->A; '
```

## Using Custom Functions in the Interface

### 1. Custom MySQL Functions Tab

The biocat interface includes a dedicated "Custom MySQL Functions" tab with:

- **Interactive Testing**: Test functions with your own DNA sequences
- **Quick Examples**: Run predefined examples to see function capabilities
- **Real Data Analysis**: Execute queries using custom functions on actual biocat data

### 2. Sequence Analysis Queries

Custom functions are integrated into the "Sequence Analysis" category:

- **analyze_sequences**: Uses `classify_sequence()` on DNA data
- **nucleotide_composition**: Uses `count_nucleotides()` for composition analysis
- **dna_sequence_analysis**: Comprehensive analysis using multiple functions
- **compare_transcript_sequences**: Uses `detect_mutations()` for sequence comparison

### 3. Interactive Testing Interface

#### Function Testing
1. Enter DNA sequences in the provided text areas
2. Click the appropriate function test button:
   - "Test classify_sequence()"
   - "Test count_nucleotides()"
   - "Test detect_mutations()"
3. View results in the output area

#### Real Data Analysis
Use the predefined queries in the "Sequence Analysis" category to run comprehensive analyses on biocat data using custom functions.

## Advanced Usage Examples

### 1. Gene Classification Analysis
```sql
SELECT
    s.species_name,
    classify_sequence(g.dna_sequence) as sequence_classification,
    COUNT(*) as gene_count,
    AVG(LENGTH(g.dna_sequence)) as avg_sequence_length
FROM gene g
JOIN species s ON g.species_id = s.species_id
WHERE g.dna_sequence IS NOT NULL
GROUP BY s.species_name, classify_sequence(g.dna_sequence)
ORDER BY s.species_name, gene_count DESC;
```

### 2. GC Content Calculation
```sql
SELECT
    g.gene_symbol,
    JSON_EXTRACT(count_nucleotides(g.dna_sequence), '$.G') as guanine_count,
    JSON_EXTRACT(count_nucleotides(g.dna_sequence), '$.C') as cytosine_count,
    ROUND((JSON_EXTRACT(count_nucleotides(g.dna_sequence), '$.G') +
           JSON_EXTRACT(count_nucleotides(g.dna_sequence), '$.C')) /
           LENGTH(g.dna_sequence) * 100, 2) as gc_content_percent
FROM gene g
WHERE g.dna_sequence IS NOT NULL
AND LENGTH(g.dna_sequence) > 100
ORDER BY gc_content_percent DESC;
```

### 3. Cross-Species Mutation Analysis
```sql
SELECT
    g1.gene_symbol,
    s1.species_name as species1,
    s2.species_name as species2,
    LENGTH(g1.dna_sequence) as seq1_length,
    LENGTH(g2.dna_sequence) as seq2_length,
    LEFT(detect_mutations(g1.dna_sequence, g2.dna_sequence), 200) as mutation_summary
FROM gene g1
JOIN species s1 ON g1.species_id = s1.species_id
JOIN gene g2 ON g1.gene_symbol = g2.gene_symbol
JOIN species s2 ON g2.species_id = s2.species_id
WHERE g1.species_id < g2.species_id
AND g1.dna_sequence IS NOT NULL
AND g2.dna_sequence IS NOT NULL
AND LENGTH(g1.dna_sequence) > 50
AND LENGTH(g2.dna_sequence) > 50
AND g1.gene_symbol IS NOT NULL
LIMIT 10;
```

## Installation and Setup

### 1. Function Installation
The custom functions are defined in `functions.sql`. To install them:

```bash
mysql -u root -p biocat < ../functions.sql
```

### 2. Verifying Installation
Test that functions are available:

```sql
-- Test basic functionality
SELECT classify_sequence('ATGGCATAG') as test_classify;
SELECT count_nucleotides('ATCG') as test_count;
SELECT detect_mutations('ATCG', 'ATCC') as test_mutations;
```

### 3. Interface Access
1. Start the biocat interface
2. Connect to your database
3. Navigate to the "Custom MySQL Functions" tab
4. Begin testing and analysis

## Performance Considerations

- **classify_sequence()**: Very fast, simple string search
- **count_nucleotides()**: Linear time complexity O(n) where n is sequence length
- **detect_mutations()**: O(min(len1, len2)) for sequence comparison

For large datasets:
- Use LIMIT clauses to test queries first
- Consider indexing on sequence length columns
- Monitor query execution time for very long sequences

## Troubleshooting

### Common Issues

1. **Function not found error**
   - Ensure functions.sql has been executed
   - Check MySQL user permissions

2. **JSON parsing errors**
   - Verify MySQL version supports JSON functions (5.7+)
   - Use JSON_EXTRACT() for accessing count_nucleotides() results

3. **Performance issues**
   - Add WHERE clauses to filter sequence length
   - Use LIMIT for initial testing

### Getting Help

- Check the "Information" tab in the interface for usage tips
- Use the test functions in the interface to verify functionality
- Examine the predefined queries for usage examples

## Contributing

To add new custom functions:

1. Define the function in `functions.sql`
2. Add corresponding queries to `sql_queries.py`
3. Update the interface if needed
4. Add tests and documentation

## License

These custom functions are part of the biocat database project and follow the same licensing terms.