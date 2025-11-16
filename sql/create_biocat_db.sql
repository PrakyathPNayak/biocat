-- Create biocat database - Streamlined Ensembl-compatible schema
-- Execute this script as a MySQL user with CREATE privileges
-- This schema includes only tables that can be populated from Ensembl data
-- Fixed for MySQL 8.0+ compatibility

-- Create the database
CREATE DATABASE IF NOT EXISTS biocat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE biocat;

-- Drop tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS variant_gene_annotation;
DROP TABLE IF EXISTS ortholog;
DROP TABLE IF EXISTS protein_interaction;
DROP TABLE IF EXISTS gene_pathway_annotation;
DROP TABLE IF EXISTS protein_domain_annotation;
DROP TABLE IF EXISTS gene_go_annotation;
DROP TABLE IF EXISTS genetic_variant;
DROP TABLE IF EXISTS protein;
DROP TABLE IF EXISTS transcript;
DROP TABLE IF EXISTS gene;
DROP TABLE IF EXISTS chromosome;
DROP TABLE IF EXISTS genome_assembly;
DROP TABLE IF EXISTS species;
DROP TABLE IF EXISTS pathway;
DROP TABLE IF EXISTS protein_domain;
DROP TABLE IF EXISTS gene_ontology;
DROP TABLE IF EXISTS data_source;
DROP TABLE IF EXISTS ncbi_taxa_name;
DROP TABLE IF EXISTS ncbi_taxa_node;

-- Create ncbi_taxa_node table (main taxonomy hierarchy)
CREATE TABLE ncbi_taxa_node (
    taxon_id INT UNSIGNED NOT NULL,
    parent_id INT UNSIGNED NOT NULL,
    `rank` VARCHAR(32) NOT NULL DEFAULT '',
    genbank_hidden_flag TINYINT(1) NOT NULL DEFAULT 0,
    left_index INT NOT NULL DEFAULT 0,
    right_index INT NOT NULL DEFAULT 0,
    root_id INT NOT NULL DEFAULT 1,
    PRIMARY KEY (taxon_id),
    KEY idx_parent_id (parent_id),
    KEY idx_rank (`rank`),
    KEY idx_left_index (left_index),
    KEY idx_right_index (right_index),
    KEY idx_parent_rank (parent_id, `rank`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create ncbi_taxa_name table (taxonomy names and synonyms)
CREATE TABLE ncbi_taxa_name (
    taxon_id INT UNSIGNED NOT NULL,
    name VARCHAR(255) NOT NULL,
    name_class VARCHAR(50) NOT NULL,
    PRIMARY KEY (taxon_id, name, name_class),
    KEY idx_name (name),
    KEY idx_name_class (name_class),
    KEY idx_name_class_name (name_class, name),
    CONSTRAINT fk_ncbi_taxa_name_taxon_id 
        FOREIGN KEY (taxon_id) REFERENCES ncbi_taxa_node (taxon_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create species table (species information linked to taxonomy)
CREATE TABLE species (
    species_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    taxon_id INT UNSIGNED DEFAULT NULL,
    species_name VARCHAR(255) NOT NULL,
    binomial_name VARCHAR(255) DEFAULT NULL,
    common_name VARCHAR(255) DEFAULT NULL,
    web_name VARCHAR(255) DEFAULT NULL,
    is_current TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (species_id),
    UNIQUE KEY uk_species_name (species_name),
    KEY idx_taxon_id (taxon_id),
    KEY idx_is_current (is_current),
    KEY idx_common_name (common_name),
    KEY idx_binomial_name (binomial_name),
    CONSTRAINT fk_species_taxon_id 
        FOREIGN KEY (taxon_id) REFERENCES ncbi_taxa_node (taxon_id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert root taxon (if needed)
INSERT IGNORE INTO ncbi_taxa_node (taxon_id, parent_id, `rank`, left_index, right_index, root_id) 
VALUES (1, 1, 'no rank', 1, 2, 1);

INSERT IGNORE INTO ncbi_taxa_name (taxon_id, name, name_class) 
VALUES (1, 'root', 'scientific name');

-- ========================================
-- DATA SOURCE TRACKING
-- ========================================

-- Data sources and their versions
CREATE TABLE data_source (
    source_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    source_name VARCHAR(100) NOT NULL,
    source_url VARCHAR(500),
    source_version VARCHAR(50),
    release_date DATE,
    description TEXT,
    contact_email VARCHAR(255),
    is_active TINYINT(1) DEFAULT 1,
    PRIMARY KEY (source_id),
    UNIQUE KEY uk_source_version (source_name, source_version),
    KEY idx_source_name (source_name),
    KEY idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- FUNCTIONAL ANNOTATION ENTITIES
-- ========================================

-- Gene ontology terms
CREATE TABLE gene_ontology (
    go_id VARCHAR(20) NOT NULL,
    go_name VARCHAR(255) NOT NULL,
    go_namespace ENUM('biological_process', 'molecular_function', 'cellular_component') NOT NULL,
    go_definition TEXT,
    is_obsolete TINYINT(1) DEFAULT 0,
    PRIMARY KEY (go_id),
    KEY idx_go_namespace (go_namespace),
    KEY idx_is_obsolete (is_obsolete)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Protein domains and families
CREATE TABLE protein_domain (
    domain_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    domain_accession VARCHAR(50) NOT NULL,
    domain_name VARCHAR(255) NOT NULL,
    domain_description TEXT,
    domain_type VARCHAR(100),
    database_source VARCHAR(50),
    PRIMARY KEY (domain_id),
    UNIQUE KEY uk_domain_accession (domain_accession),
    KEY idx_domain_type (domain_type),
    KEY idx_database_source (database_source)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Biological pathways (limited coverage from Ensembl)
CREATE TABLE pathway (
    pathway_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    pathway_accession VARCHAR(50) NOT NULL,
    pathway_name VARCHAR(255) NOT NULL,
    pathway_description TEXT,
    pathway_category VARCHAR(100),
    database_source VARCHAR(50),
    PRIMARY KEY (pathway_id),
    UNIQUE KEY uk_pathway_accession (pathway_accession),
    KEY idx_pathway_category (pathway_category),
    KEY idx_database_source (database_source)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- GENOMIC INFORMATION ENTITIES
-- ========================================

-- Genome assemblies for species
CREATE TABLE genome_assembly (
    assembly_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    species_id INT UNSIGNED NOT NULL,
    assembly_name VARCHAR(255) NOT NULL,
    assembly_accession VARCHAR(100),
    assembly_level ENUM('complete genome', 'chromosome', 'scaffold', 'contig') NOT NULL,
    genome_size BIGINT UNSIGNED,
    chromosome_count INT UNSIGNED,
    scaffold_count INT UNSIGNED,
    contig_count INT UNSIGNED,
    n50_value INT UNSIGNED,
    gc_content DECIMAL(5,2),
    assembly_date DATE,
    submitter VARCHAR(255),
    is_reference TINYINT(1) DEFAULT 0,
    is_representative TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (assembly_id),
    UNIQUE KEY uk_assembly_accession (assembly_accession),
    KEY idx_species_id (species_id),
    KEY idx_assembly_level (assembly_level),
    KEY idx_is_reference (is_reference),
    KEY idx_species_reference (species_id, is_reference),
    CONSTRAINT fk_genome_assembly_species_id 
        FOREIGN KEY (species_id) REFERENCES species (species_id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Chromosomes within genome assemblies
CREATE TABLE chromosome (
    chromosome_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    assembly_id INT UNSIGNED NOT NULL,
    chromosome_name VARCHAR(100) NOT NULL,
    chromosome_type ENUM('autosome', 'sex_chromosome', 'mitochondrial', 'chloroplast', 'plasmid', 'other') DEFAULT 'autosome',
    sequence_length BIGINT UNSIGNED,
    sequence_accession VARCHAR(100),
    is_circular TINYINT(1) DEFAULT 0,
    PRIMARY KEY (chromosome_id),
    KEY idx_assembly_id (assembly_id),
    KEY idx_chromosome_name (chromosome_name),
    KEY idx_chromosome_type (chromosome_type),
    CONSTRAINT fk_chromosome_assembly_id 
        FOREIGN KEY (assembly_id) REFERENCES genome_assembly (assembly_id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- GENE AND ANNOTATION ENTITIES
-- ========================================

-- Genes within species
CREATE TABLE gene (
    gene_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    species_id INT UNSIGNED NOT NULL,
    chromosome_id INT UNSIGNED,
    gene_stable_id VARCHAR(100) NOT NULL,
    gene_symbol VARCHAR(100),
    gene_name TEXT,
    gene_description TEXT,
    gene_biotype VARCHAR(100),
    start_position BIGINT UNSIGNED,
    end_position BIGINT UNSIGNED,
    strand TINYINT,
    is_canonical TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (gene_id),
    UNIQUE KEY uk_gene_stable_id (gene_stable_id),
    KEY idx_species_id (species_id),
    KEY idx_chromosome_id (chromosome_id),
    KEY idx_gene_symbol (gene_symbol),
    KEY idx_gene_biotype (gene_biotype),
    KEY idx_position (chromosome_id, start_position, end_position),
    KEY idx_species_biotype (species_id, gene_biotype),
    CONSTRAINT fk_gene_species_id 
        FOREIGN KEY (species_id) REFERENCES species (species_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_gene_chromosome_id 
        FOREIGN KEY (chromosome_id) REFERENCES chromosome (chromosome_id) 
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Transcripts of genes
CREATE TABLE transcript (
    transcript_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    gene_id INT UNSIGNED NOT NULL,
    transcript_stable_id VARCHAR(100) NOT NULL,
    transcript_name VARCHAR(255),
    transcript_biotype VARCHAR(100),
    start_position BIGINT UNSIGNED,
    end_position BIGINT UNSIGNED,
    strand TINYINT,
    transcript_length INT UNSIGNED,
    is_canonical TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (transcript_id),
    UNIQUE KEY uk_transcript_stable_id (transcript_stable_id),
    KEY idx_gene_id (gene_id),
    KEY idx_transcript_biotype (transcript_biotype),
    KEY idx_is_canonical (is_canonical),
    KEY idx_gene_canonical (gene_id, is_canonical),
    CONSTRAINT fk_transcript_gene_id 
        FOREIGN KEY (gene_id) REFERENCES gene (gene_id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Proteins translated from transcripts
CREATE TABLE protein (
    protein_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    transcript_id INT UNSIGNED NOT NULL,
    protein_stable_id VARCHAR(100) NOT NULL,
    protein_sequence LONGTEXT,
    protein_length INT UNSIGNED,
    molecular_weight DECIMAL(10,2),
    isoelectric_point DECIMAL(4,2),
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (protein_id),
    UNIQUE KEY uk_protein_stable_id (protein_stable_id),
    KEY idx_transcript_id (transcript_id),
    KEY idx_protein_length (protein_length),
    CONSTRAINT fk_protein_transcript_id 
        FOREIGN KEY (transcript_id) REFERENCES transcript (transcript_id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- VARIATION AND EVOLUTION ENTITIES
-- ========================================

-- Genetic variants
CREATE TABLE genetic_variant (
    variant_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    chromosome_id INT UNSIGNED NOT NULL,
    variant_name VARCHAR(255),
    variant_type ENUM('SNP', 'indel', 'CNV', 'SV', 'other') NOT NULL,
    start_position BIGINT UNSIGNED NOT NULL,
    end_position BIGINT UNSIGNED,
    reference_allele TEXT,
    alternate_allele TEXT,
    variant_class VARCHAR(100),
    minor_allele_frequency DECIMAL(6,5),
    validation_status VARCHAR(50),
    clinical_significance VARCHAR(100),
    PRIMARY KEY (variant_id),
    KEY idx_chromosome_id (chromosome_id),
    KEY idx_variant_type (variant_type),
    KEY idx_position (chromosome_id, start_position),
    KEY idx_clinical_significance (clinical_significance),
    KEY idx_position_type (chromosome_id, start_position, variant_type),
    CONSTRAINT fk_variant_chromosome_id 
        FOREIGN KEY (chromosome_id) REFERENCES chromosome (chromosome_id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- ASSOCIATION TABLES
-- ========================================

-- Gene-GO term associations
CREATE TABLE gene_go_annotation (
    annotation_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    gene_id INT UNSIGNED NOT NULL,
    go_id VARCHAR(20) NOT NULL,
    evidence_code VARCHAR(10),
    annotation_source VARCHAR(100),
    annotation_date DATE,
    PRIMARY KEY (annotation_id),
    UNIQUE KEY uk_gene_go (gene_id, go_id),
    KEY idx_gene_id (gene_id),
    KEY idx_go_id (go_id),
    KEY idx_evidence_code (evidence_code),
    CONSTRAINT fk_gene_go_gene_id 
        FOREIGN KEY (gene_id) REFERENCES gene (gene_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_gene_go_go_id 
        FOREIGN KEY (go_id) REFERENCES gene_ontology (go_id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Protein-domain associations
CREATE TABLE protein_domain_annotation (
    annotation_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    protein_id INT UNSIGNED NOT NULL,
    domain_id INT UNSIGNED NOT NULL,
    start_position INT UNSIGNED,
    end_position INT UNSIGNED,
    e_value DECIMAL(10,3),
    score DECIMAL(8,2),
    PRIMARY KEY (annotation_id),
    KEY idx_protein_id (protein_id),
    KEY idx_domain_id (domain_id),
    KEY idx_protein_position (protein_id, start_position, end_position),
    CONSTRAINT fk_protein_domain_protein_id 
        FOREIGN KEY (protein_id) REFERENCES protein (protein_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_protein_domain_domain_id 
        FOREIGN KEY (domain_id) REFERENCES protein_domain (domain_id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Gene-pathway associations
CREATE TABLE gene_pathway_annotation (
    annotation_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    gene_id INT UNSIGNED NOT NULL,
    pathway_id INT UNSIGNED NOT NULL,
    annotation_source VARCHAR(100),
    annotation_date DATE,
    PRIMARY KEY (annotation_id),
    UNIQUE KEY uk_gene_pathway (gene_id, pathway_id),
    KEY idx_gene_id (gene_id),
    KEY idx_pathway_id (pathway_id),
    CONSTRAINT fk_gene_pathway_gene_id 
        FOREIGN KEY (gene_id) REFERENCES gene (gene_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_gene_pathway_pathway_id 
        FOREIGN KEY (pathway_id) REFERENCES pathway (pathway_id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Protein-protein interactions (limited data from Ensembl)
CREATE TABLE protein_interaction (
    interaction_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    protein_a_id INT UNSIGNED NOT NULL,
    protein_b_id INT UNSIGNED NOT NULL,
    interaction_type VARCHAR(100),
    confidence_score DECIMAL(5,4),
    detection_method VARCHAR(100),
    interaction_source VARCHAR(100),
    pubmed_id INT UNSIGNED,
    PRIMARY KEY (interaction_id),
    KEY idx_protein_a_id (protein_a_id),
    KEY idx_protein_b_id (protein_b_id),
    KEY idx_interaction_type (interaction_type),
    KEY idx_confidence_score (confidence_score),
    CONSTRAINT fk_interaction_protein_a 
        FOREIGN KEY (protein_a_id) REFERENCES protein (protein_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_interaction_protein_b 
        FOREIGN KEY (protein_b_id) REFERENCES protein (protein_id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Variant-gene associations
CREATE TABLE variant_gene_annotation (
    annotation_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    variant_id INT UNSIGNED NOT NULL,
    gene_id INT UNSIGNED NOT NULL,
    variant_effect VARCHAR(100),
    impact_severity ENUM('high', 'moderate', 'low', 'modifier'),
    annotation_source VARCHAR(100),
    PRIMARY KEY (annotation_id),
    KEY idx_variant_id (variant_id),
    KEY idx_gene_id (gene_id),
    KEY idx_variant_effect (variant_effect),
    KEY idx_impact_severity (impact_severity),
    CONSTRAINT fk_variant_gene_variant_id 
        FOREIGN KEY (variant_id) REFERENCES genetic_variant (variant_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_variant_gene_gene_id 
        FOREIGN KEY (gene_id) REFERENCES gene (gene_id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Orthology relationships between genes across species
CREATE TABLE ortholog (
    ortholog_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    gene_a_id INT UNSIGNED NOT NULL,
    gene_b_id INT UNSIGNED NOT NULL,
    orthology_type ENUM('one2one', 'one2many', 'many2many') NOT NULL,
    orthology_confidence DECIMAL(5,4),
    dn_ds_ratio DECIMAL(8,6),
    percentage_identity DECIMAL(5,2),
    alignment_coverage DECIMAL(5,2),
    PRIMARY KEY (ortholog_id),
    UNIQUE KEY uk_ortholog_pair (gene_a_id, gene_b_id),
    KEY idx_gene_a_id (gene_a_id),
    KEY idx_gene_b_id (gene_b_id),
    KEY idx_orthology_type (orthology_type),
    KEY idx_orthology_confidence (orthology_confidence),
    CONSTRAINT fk_ortholog_gene_a 
        FOREIGN KEY (gene_a_id) REFERENCES gene (gene_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_ortholog_gene_b 
        FOREIGN KEY (gene_b_id) REFERENCES gene (gene_id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert Ensembl data source
INSERT IGNORE INTO data_source (source_name, source_url, source_version, description, is_active) 
VALUES ('Ensembl', 'https://rest.ensembl.org', '112', 'Ensembl genome browser and annotation database', 1);

-- Show the created tables
SHOW TABLES;

-- Display table structures for core tables
DESCRIBE ncbi_taxa_node;
DESCRIBE ncbi_taxa_name;
DESCRIBE species;
DESCRIBE gene;
DESCRIBE transcript;
DESCRIBE protein;

SELECT 'Streamlined biocat database created successfully!' as message;
SELECT 'Total tables: 18 (all compatible with Ensembl data)' as info;