"""
SQL Queries for Biocat Database Interface
Contains predefined useful queries for exploring biological data
"""

# Basic Statistics and Overview Queries
BASIC_STATS_QUERIES = {
    "database_overview": """
        SELECT
            'Species' as table_name, COUNT(*) as record_count
        FROM species
        UNION ALL
        SELECT 'Genes', COUNT(*) FROM gene
        UNION ALL
        SELECT 'Transcripts', COUNT(*) FROM transcript
        UNION ALL
        SELECT 'Proteins', COUNT(*) FROM protein
        UNION ALL
        SELECT 'Chromosomes', COUNT(*) FROM chromosome
        UNION ALL
        SELECT 'Genetic Variants', COUNT(*) FROM genetic_variant
        UNION ALL
        SELECT 'GO Annotations', COUNT(*) FROM gene_go_annotation
        ORDER BY record_count DESC;
    """,
    "species_summary": """
        SELECT
            s.species_name,
            s.common_name,
            COUNT(DISTINCT g.gene_id) as gene_count,
            COUNT(DISTINCT t.transcript_id) as transcript_count,
            COUNT(DISTINCT p.protein_id) as protein_count
        FROM species s
        LEFT JOIN gene g ON s.species_id = g.species_id
        LEFT JOIN transcript t ON g.gene_id = t.gene_id
        LEFT JOIN protein p ON t.transcript_id = p.transcript_id
        GROUP BY s.species_id, s.species_name, s.common_name
        ORDER BY gene_count DESC;
    """,
    "chromosome_stats": """
        SELECT
            s.species_name,
            c.chromosome_name,
            c.sequence_length,
            COUNT(g.gene_id) as gene_count,
            ROUND(COUNT(g.gene_id) / (c.sequence_length / 1000000), 2) as genes_per_mb
        FROM species s
        JOIN genome_assembly ga ON s.species_id = ga.species_id
        JOIN chromosome c ON ga.assembly_id = c.assembly_id
        LEFT JOIN gene g ON c.chromosome_id = g.chromosome_id
        WHERE c.sequence_length IS NOT NULL
        GROUP BY s.species_name, c.chromosome_name, c.sequence_length
        ORDER BY s.species_name, c.chromosome_name;
    """,
}

# Gene and Transcript Analysis Queries
GENE_QUERIES = {
    "genes_by_biotype": """
        SELECT
            s.species_name,
            g.gene_biotype,
            COUNT(*) as gene_count,
            ROUND(AVG(g.end_position - g.start_position + 1), 0) as avg_length
        FROM gene g
        JOIN species s ON g.species_id = s.species_id
        WHERE g.gene_biotype IS NOT NULL
        GROUP BY s.species_name, g.gene_biotype
        ORDER BY s.species_name, gene_count DESC;
    """,
    "longest_genes": """
        SELECT
            s.species_name,
            g.gene_symbol,
            g.gene_name,
            g.gene_biotype,
            c.chromosome_name,
            (g.end_position - g.start_position + 1) as gene_length,
            g.start_position,
            g.end_position
        FROM gene g
        JOIN species s ON g.species_id = s.species_id
        LEFT JOIN chromosome c ON g.chromosome_id = c.chromosome_id
        WHERE g.start_position IS NOT NULL AND g.end_position IS NOT NULL
        ORDER BY gene_length DESC
        LIMIT 50;
    """,
    "genes_with_multiple_transcripts": """
        SELECT
            s.species_name,
            g.gene_symbol,
            g.gene_name,
            COUNT(t.transcript_id) as transcript_count,
            GROUP_CONCAT(t.transcript_biotype) as transcript_types
        FROM gene g
        JOIN species s ON g.species_id = s.species_id
        JOIN transcript t ON g.gene_id = t.gene_id
        GROUP BY g.gene_id, s.species_name, g.gene_symbol, g.gene_name
        HAVING transcript_count > 1
        ORDER BY transcript_count DESC;
    """,
    "gene_search": """
        SELECT
            s.species_name,
            g.gene_symbol,
            g.gene_name,
            g.gene_description,
            g.gene_biotype,
            c.chromosome_name,
            g.start_position,
            g.end_position,
            (g.end_position - g.start_position + 1) as gene_length
        FROM gene g
        JOIN species s ON g.species_id = s.species_id
        LEFT JOIN chromosome c ON g.chromosome_id = c.chromosome_id
        WHERE (g.gene_symbol LIKE %s OR g.gene_name LIKE %s OR g.gene_description LIKE %s)
        ORDER BY s.species_name, g.gene_symbol;
    """,
}

# Protein Analysis Queries
PROTEIN_QUERIES = {
    "protein_length_distribution": """
        SELECT
            s.species_name,
            CASE
                WHEN p.protein_length < 100 THEN 'Very Short (<100 AA)'
                WHEN p.protein_length < 300 THEN 'Short (100-299 AA)'
                WHEN p.protein_length < 600 THEN 'Medium (300-599 AA)'
                WHEN p.protein_length < 1000 THEN 'Long (600-999 AA)'
                ELSE 'Very Long (≥1000 AA)'
            END as length_category,
            COUNT(*) as protein_count,
            ROUND(AVG(p.protein_length), 0) as avg_length
        FROM protein p
        JOIN transcript t ON p.transcript_id = t.transcript_id
        JOIN gene g ON t.gene_id = g.gene_id
        JOIN species s ON g.species_id = s.species_id
        WHERE p.protein_length IS NOT NULL
        GROUP BY s.species_name, length_category
        ORDER BY s.species_name, avg_length;
    """,
    "largest_proteins": """
        SELECT
            s.species_name,
            g.gene_symbol,
            g.gene_name,
            p.protein_stable_id,
            p.protein_length,
            p.molecular_weight,
            p.isoelectric_point
        FROM protein p
        JOIN transcript t ON p.transcript_id = t.transcript_id
        JOIN gene g ON t.gene_id = g.gene_id
        JOIN species s ON g.species_id = s.species_id
        WHERE p.protein_length IS NOT NULL
        ORDER BY p.protein_length DESC
        LIMIT 30;
    """,
    "protein_properties": """
        SELECT
            s.species_name,
            COUNT(*) as total_proteins,
            ROUND(AVG(p.protein_length), 0) as avg_length,
            ROUND(AVG(p.molecular_weight), 2) as avg_molecular_weight,
            ROUND(AVG(p.isoelectric_point), 2) as avg_isoelectric_point,
            MIN(p.protein_length) as min_length,
            MAX(p.protein_length) as max_length
        FROM protein p
        JOIN transcript t ON p.transcript_id = t.transcript_id
        JOIN gene g ON t.gene_id = g.gene_id
        JOIN species s ON g.species_id = s.species_id
        WHERE p.protein_length IS NOT NULL
        GROUP BY s.species_name
        ORDER BY total_proteins DESC;
    """,
}

# Sequence Analysis Queries
SEQUENCE_QUERIES = {
    "analyze_sequences": """
        SELECT
            g.gene_symbol,
            g.gene_name,
            LEFT(p.protein_sequence, 50) as sequence_start,
            p.protein_length,
            classify_sequence(p.protein_sequence) as classification
        FROM protein p
        JOIN transcript t ON p.transcript_id = t.transcript_id
        JOIN gene g ON t.gene_id = g.gene_id
        WHERE p.protein_sequence IS NOT NULL
        LIMIT 20;
    """,
    "nucleotide_composition": """
        SELECT
            g.gene_symbol,
            g.gene_name,
            LEFT(p.protein_sequence, 100) as sequence_sample,
            count_nucleotides(p.protein_sequence) as nucleotide_counts
        FROM protein p
        JOIN transcript t ON p.transcript_id = t.transcript_id
        JOIN gene g ON t.gene_id = g.gene_id
        WHERE p.protein_sequence IS NOT NULL
        LIMIT 10;
    """,
    "dna_sequence_analysis": """
        SELECT
            g.gene_symbol,
            g.gene_name,
            s.species_name,
            LEFT(g.dna_sequence, 60) as sequence_preview,
            LENGTH(g.dna_sequence) as sequence_length,
            classify_sequence(g.dna_sequence) as sequence_type,
            count_nucleotides(g.dna_sequence) as nucleotide_composition
        FROM gene g
        JOIN species s ON g.species_id = s.species_id
        WHERE g.dna_sequence IS NOT NULL
        AND LENGTH(g.dna_sequence) > 30
        ORDER BY sequence_length DESC
        LIMIT 15;
    """,
    "compare_transcript_sequences": """
        SELECT
            g.gene_symbol,
            t1.transcript_id as transcript1_id,
            t2.transcript_id as transcript2_id,
            LEFT(t1.cdna_sequence, 50) as seq1_preview,
            LEFT(t2.cdna_sequence, 50) as seq2_preview,
            LENGTH(t1.cdna_sequence) as seq1_length,
            LENGTH(t2.cdna_sequence) as seq2_length,
            detect_mutations(t1.cdna_sequence, t2.cdna_sequence) as sequence_differences
        FROM gene g
        JOIN transcript t1 ON g.gene_id = t1.gene_id
        JOIN transcript t2 ON g.gene_id = t2.gene_id
        WHERE t1.transcript_id < t2.transcript_id
        AND t1.cdna_sequence IS NOT NULL
        AND t2.cdna_sequence IS NOT NULL
        AND LENGTH(t1.cdna_sequence) > 50
        AND LENGTH(t2.cdna_sequence) > 50
        LIMIT 10;
    """,
    "gene_classification_summary": """
        SELECT
            s.species_name,
            classify_sequence(g.dna_sequence) as sequence_classification,
            COUNT(*) as gene_count,
            AVG(LENGTH(g.dna_sequence)) as avg_sequence_length,
            MIN(LENGTH(g.dna_sequence)) as min_length,
            MAX(LENGTH(g.dna_sequence)) as max_length
        FROM gene g
        JOIN species s ON g.species_id = s.species_id
        WHERE g.dna_sequence IS NOT NULL
        GROUP BY s.species_name, classify_sequence(g.dna_sequence)
        ORDER BY s.species_name, gene_count DESC;
    """,
    "dna_sequence_detection": """
        SELECT
            TABLE_NAME,
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        AND (COLUMN_NAME LIKE '%seq%' OR COLUMN_NAME LIKE '%dna%' OR COLUMN_NAME LIKE '%rna%')
        AND DATA_TYPE IN ('text', 'longtext', 'mediumtext', 'varchar')
        ORDER BY TABLE_NAME, COLUMN_NAME;
    """,
    "check_sequence_content": """
        SELECT
            'chromosome' as table_name,
            'sequence' as column_name,
            COUNT(*) as total_rows,
            COUNT(sequence) as non_null_rows,
            AVG(LENGTH(sequence)) as avg_length,
            MAX(LENGTH(sequence)) as max_length,
            MIN(LENGTH(sequence)) as min_length
        FROM chromosome
        WHERE sequence IS NOT NULL AND sequence != ''
        UNION ALL
        SELECT
            'gene' as table_name,
            'dna_sequence' as column_name,
            COUNT(*) as total_rows,
            COUNT(dna_sequence) as non_null_rows,
            AVG(LENGTH(dna_sequence)) as avg_length,
            MAX(LENGTH(dna_sequence)) as max_length,
            MIN(LENGTH(dna_sequence)) as min_length
        FROM gene
        WHERE dna_sequence IS NOT NULL AND dna_sequence != ''
        UNION ALL
        SELECT
            'transcript' as table_name,
            'cdna_sequence' as column_name,
            COUNT(*) as total_rows,
            COUNT(cdna_sequence) as non_null_rows,
            AVG(LENGTH(cdna_sequence)) as avg_length,
            MAX(LENGTH(cdna_sequence)) as max_length,
            MIN(LENGTH(cdna_sequence)) as min_length
        FROM transcript
        WHERE cdna_sequence IS NOT NULL AND cdna_sequence != '';
    """,
    "sample_dna_sequences": """
        SELECT
            g.gene_symbol,
            g.gene_name,
            s.species_name,
            LEFT(g.dna_sequence, 100) as sequence_preview,
            LENGTH(g.dna_sequence) as sequence_length
        FROM gene g
        JOIN species s ON g.species_id = s.species_id
        WHERE g.dna_sequence IS NOT NULL
        AND LENGTH(g.dna_sequence) > 50
        ORDER BY RAND()
        LIMIT 10;
    """,
    "validate_dna_bases": """
        SELECT
            g.gene_symbol,
            LENGTH(g.dna_sequence) as length,
            LENGTH(g.dna_sequence) - LENGTH(REPLACE(REPLACE(REPLACE(REPLACE(UPPER(g.dna_sequence), 'A', ''), 'T', ''), 'C', ''), 'G', '')) as valid_bases,
            ROUND((LENGTH(g.dna_sequence) - LENGTH(REPLACE(REPLACE(REPLACE(REPLACE(UPPER(g.dna_sequence), 'A', ''), 'T', ''), 'C', ''), 'G', ''))) / LENGTH(g.dna_sequence) * 100, 2) as percent_valid
        FROM gene g
        WHERE g.dna_sequence IS NOT NULL
        AND LENGTH(g.dna_sequence) > 20
        HAVING percent_valid > 80
        ORDER BY percent_valid DESC
        LIMIT 20;
    """,
}

# Comparative Analysis Queries
COMPARATIVE_QUERIES = {
    "species_comparison": """
        SELECT
            s1.species_name as species_1,
            s2.species_name as species_2,
            o.orthology_type,
            COUNT(*) as ortholog_count,
            ROUND(AVG(o.percentage_identity), 2) as avg_identity,
            ROUND(AVG(o.dn_ds_ratio), 4) as avg_dn_ds
        FROM ortholog o
        JOIN gene g1 ON o.gene_a_id = g1.gene_id
        JOIN gene g2 ON o.gene_b_id = g2.gene_id
        JOIN species s1 ON g1.species_id = s1.species_id
        JOIN species s2 ON g2.species_id = s2.species_id
        WHERE s1.species_id != s2.species_id
        GROUP BY s1.species_name, s2.species_name, o.orthology_type
        ORDER BY ortholog_count DESC;
    """,
    "cross_species_genes": """
        SELECT
            g1.gene_symbol,
            s1.species_name as species_1,
            s2.species_name as species_2,
            o.orthology_type,
            o.percentage_identity,
            o.dn_ds_ratio
        FROM ortholog o
        JOIN gene g1 ON o.gene_a_id = g1.gene_id
        JOIN gene g2 ON o.gene_b_id = g2.gene_id
        JOIN species s1 ON g1.species_id = s1.species_id
        JOIN species s2 ON g2.species_id = s2.species_id
        WHERE g1.gene_symbol IS NOT NULL
        AND o.percentage_identity IS NOT NULL
        ORDER BY o.percentage_identity DESC
        LIMIT 30;
    """,
}

# Functional Annotation Queries
ANNOTATION_QUERIES = {
    "go_term_distribution": """
        SELECT
            go.go_namespace,
            COUNT(DISTINCT gga.gene_id) as annotated_genes,
            COUNT(*) as total_annotations
        FROM gene_go_annotation gga
        JOIN gene_ontology go ON gga.go_id = go.go_id
        GROUP BY go.go_namespace
        ORDER BY annotated_genes DESC;
    """,
    "top_go_terms": """
        SELECT
            go.go_id,
            go.go_name,
            go.go_namespace,
            COUNT(gga.gene_id) as gene_count
        FROM gene_go_annotation gga
        JOIN gene_ontology go ON gga.go_id = go.go_id
        GROUP BY go.go_id, go.go_name, go.go_namespace
        ORDER BY gene_count DESC
        LIMIT 20;
    """,
    "genes_by_go_term": """
        SELECT
            s.species_name,
            g.gene_symbol,
            g.gene_name,
            go.go_name,
            go.go_namespace,
            gga.evidence_code
        FROM gene_go_annotation gga
        JOIN gene g ON gga.gene_id = g.gene_id
        JOIN species s ON g.species_id = s.species_id
        JOIN gene_ontology go ON gga.go_id = go.go_id
        WHERE go.go_id = %s OR go.go_name LIKE %s
        ORDER BY s.species_name, g.gene_symbol;
    """,
}

# Genomic Variation Queries
VARIATION_QUERIES = {
    "variant_types": """
        SELECT
            s.species_name,
            gv.variant_type,
            COUNT(*) as variant_count,
            ROUND(AVG(gv.minor_allele_frequency), 4) as avg_maf
        FROM genetic_variant gv
        JOIN chromosome c ON gv.chromosome_id = c.chromosome_id
        JOIN genome_assembly ga ON c.assembly_id = ga.assembly_id
        JOIN species s ON ga.species_id = s.species_id
        GROUP BY s.species_name, gv.variant_type
        ORDER BY s.species_name, variant_count DESC;
    """,
    "clinical_variants": """
        SELECT
            s.species_name,
            c.chromosome_name,
            gv.variant_name,
            gv.variant_type,
            gv.clinical_significance,
            gv.start_position,
            gv.minor_allele_frequency
        FROM genetic_variant gv
        JOIN chromosome c ON gv.chromosome_id = c.chromosome_id
        JOIN genome_assembly ga ON c.assembly_id = ga.assembly_id
        JOIN species s ON ga.species_id = s.species_id
        WHERE gv.clinical_significance IS NOT NULL
        AND gv.clinical_significance != ''
        ORDER BY s.species_name, c.chromosome_name, gv.start_position;
    """,
}

# Custom Query Templates
QUERY_TEMPLATES = {
    "gene_region_search": """
        SELECT
            s.species_name,
            g.gene_symbol,
            g.gene_name,
            c.chromosome_name,
            g.start_position,
            g.end_position,
            (g.end_position - g.start_position + 1) as gene_length
        FROM gene g
        JOIN species s ON g.species_id = s.species_id
        LEFT JOIN chromosome c ON g.chromosome_id = c.chromosome_id
        WHERE c.chromosome_name = %s
        AND g.start_position >= %s
        AND g.end_position <= %s
        ORDER BY g.start_position;
    """,
    "protein_length_range": """
        SELECT
            s.species_name,
            g.gene_symbol,
            g.gene_name,
            p.protein_stable_id,
            p.protein_length,
            p.molecular_weight
        FROM protein p
        JOIN transcript t ON p.transcript_id = t.transcript_id
        JOIN gene g ON t.gene_id = g.gene_id
        JOIN species s ON g.species_id = s.species_id
        WHERE p.protein_length BETWEEN %s AND %s
        ORDER BY p.protein_length DESC;
    """,
}

# All query categories grouped together
ALL_QUERIES = {
    "Basic Statistics": BASIC_STATS_QUERIES,
    "Gene Analysis": GENE_QUERIES,
    "Protein Analysis": PROTEIN_QUERIES,
    "Sequence Analysis": SEQUENCE_QUERIES,
    "Comparative Analysis": COMPARATIVE_QUERIES,
    "Functional Annotation": ANNOTATION_QUERIES,
    "Genomic Variation": VARIATION_QUERIES,
    "Custom Templates": QUERY_TEMPLATES,
}


def get_query_categories():
    """Return list of available query categories"""
    return list(ALL_QUERIES.keys())


def get_queries_in_category(category):
    """Return all queries in a specific category"""
    return ALL_QUERIES.get(category, {})


def get_query(category, query_name):
    """Get a specific query by category and name"""
    category_queries = ALL_QUERIES.get(category, {})
    return category_queries.get(query_name, "")


def get_all_query_names():
    """Return all query names across all categories"""
    all_names = []
    for category, queries in ALL_QUERIES.items():
        for query_name in queries.keys():
            all_names.append(f"{category}: {query_name}")
    return all_names
