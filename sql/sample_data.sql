-- Sample data population script for biocat database
-- This script adds basic test data to demonstrate the database functionality

USE biocat;

-- Insert sample NCBI taxonomy nodes
INSERT INTO ncbi_taxa_node (taxon_id, parent_id, `rank`, left_index, right_index, root_id) VALUES
(9606, 9605, 'species', 10, 11, 1),  -- Homo sapiens
(10090, 10088, 'species', 20, 21, 1), -- Mus musculus  
(7955, 7954, 'species', 30, 31, 1);   -- Danio rerio

-- Insert taxonomy names
INSERT INTO ncbi_taxa_name (taxon_id, name, name_class) VALUES
(9606, 'Homo sapiens', 'scientific name'),
(9606, 'human', 'common name'),
(10090, 'Mus musculus', 'scientific name'),
(10090, 'house mouse', 'common name'),
(7955, 'Danio rerio', 'scientific name'),
(7955, 'zebraf ish', 'common name');

-- Insert species
INSERT INTO species (taxon_id, species_name, binomial_name, common_name, is_current) VALUES
(9606, 'homo_sapiens', 'Homo sapiens', 'Human', 1),
(10090, 'mus_musculus', 'Mus musculus', 'Mouse', 1),
(7955, 'danio_rerio', 'Danio rerio', 'Zebrafish', 1);

-- Insert genome assemblies
INSERT INTO genome_assembly (species_id, assembly_name, assembly_accession, assembly_level, genome_size, chromosome_count, gc_content, is_reference) VALUES
(1, 'GRCh38', 'GCA_000001405.28', 'chromosome', 3088269832, 24, 40.90, 1),
(2, 'GRCm39', 'GCA_000001635.9', 'chromosome', 2728222451, 21, 42.50, 1),
(3, 'GRCz11', 'GCA_000002035.4', 'chromosome', 1373471384, 25, 36.50, 1);

-- Insert chromosomes for Human
INSERT INTO chromosome (assembly_id, chromosome_name, chromosome_type, sequence_length) VALUES
(1, '1', 'autosome', 248956422),
(1, '2', 'autosome', 242193529),
(1, 'X', 'sex_chromosome', 156040895),
(1, 'Y', 'sex_chromosome', 57227415),
(1, 'MT', 'mitochondrial', 16569);

-- Insert chromosomes for Mouse
INSERT INTO chromosome (assembly_id, chromosome_name, chromosome_type, sequence_length) VALUES
(2, '1', 'autosome', 195154279),
(2, '2', 'autosome', 181755017),
(2, 'X', 'sex_chromosome', 169476592),
(2, 'Y', 'sex_chromosome', 91455967),
(2, 'MT', 'mitochondrial', 16299);

-- Insert chromosomes for Zebrafish
INSERT INTO chromosome (assembly_id, chromosome_name, chromosome_type, sequence_length) VALUES
(3, '1', 'autosome', 59578282),
(3, '2', 'autosome', 59640629),
(3, 'MT', 'mitochondrial', 16596);

-- Insert sample genes (Human)
INSERT INTO gene (species_id, chromosome_id, gene_stable_id, gene_symbol, gene_name, gene_description, gene_biotype, start_position, end_position, strand) VALUES
(1, 1, 'ENSG00000139618', 'BRCA2', 'BRCA2 DNA repair associated', 'DNA repair protein involved in homologous recombination', 'protein_coding', 32315086, 32400268, 1),
(1, 1, 'ENSG00000157764', 'BRAF', 'B-Raf proto-oncogene', 'Serine/threonine kinase involved in cell signaling', 'protein_coding', 140719327, 140924929, -1),
(1, 2, 'ENSG00000141510', 'TP53', 'tumor protein p53', 'Tumor suppressor regulating cell cycle', 'protein_coding', 29533204, 29554982, -1),
(1, 2, 'ENSG00000106565', 'TMEM127', 'transmembrane protein 127', 'Transmembrane protein', 'protein_coding', 96508842, 96517943, 1),
(1, 3, 'ENSG00000275221', 'VEGFA', 'vascular endothelial growth factor A', 'Growth factor involved in angiogenesis', 'protein_coding', 43737946, 43751762, 1);

-- Insert sample genes (Mouse)
INSERT INTO gene (species_id, chromosome_id, gene_stable_id, gene_symbol, gene_name, gene_description, gene_biotype, start_position, end_position, strand) VALUES
(2, 6, 'ENSMUSG00000041147', 'Brca2', 'breast cancer 2', 'DNA repair protein', 'protein_coding', 101449878, 101525997, -1),
(2, 6, 'ENSMUSG00000055866', 'Trp53', 'transformation related protein 53', 'Tumor suppressor', 'protein_coding', 69463439, 69489200, 1),
(2, 7, 'ENSMUSG00000026728', 'Braf', 'Braf transforming gene', 'Serine/threonine kinase', 'protein_coding', 121717000, 121853500, -1);

-- Insert sample genes (Zebrafish)
INSERT INTO gene (species_id, chromosome_id, gene_stable_id, gene_symbol, gene_name, gene_description, gene_biotype, start_position, end_position, strand) VALUES
(3, 11, 'ENSDARG00000037251', 'tp53', 'tumor protein p53', 'Tumor suppressor protein', 'protein_coding', 28547832, 28565255, 1),
(3, 11, 'ENSDARG00000056102', 'brca2', 'breast cancer 2', 'DNA repair associated', 'protein_coding', 45123456, 45178901, -1);

-- Insert transcripts (Human)
INSERT INTO transcript (gene_id, transcript_stable_id, transcript_name, transcript_biotype, start_position, end_position, strand, transcript_length, is_canonical) VALUES
(1, 'ENST00000380152', 'BRCA2-201', 'protein_coding', 32315086, 32400268, 1, 11386, 1),
(1, 'ENST00000614259', 'BRCA2-202', 'protein_coding', 32315086, 32399672, 1, 10782, 0),
(2, 'ENST00000288602', 'BRAF-201', 'protein_coding', 140719327, 140924929, -1, 2301, 1),
(3, 'ENST00000269305', 'TP53-201', 'protein_coding', 29533204, 29554982, -1, 2579, 1),
(3, 'ENST00000420246', 'TP53-202', 'protein_coding', 29533204, 29552341, -1, 1182, 0),
(4, 'ENST00000369300', 'TMEM127-201', 'protein_coding', 96508842, 96517943, 1, 1329, 1),
(5, 'ENST00000230882', 'VEGFA-201', 'protein_coding', 43737946, 43751762, 1, 4146, 1);

-- Insert transcripts (Mouse)
INSERT INTO transcript (gene_id, transcript_stable_id, transcript_name, transcript_biotype, start_position, end_position, strand, transcript_length, is_canonical) VALUES
(6, 'ENSMUST00000109262', 'Brca2-201', 'protein_coding', 101449878, 101525997, -1, 11343, 1),
(7, 'ENSMUST00000005585', 'Trp53-201', 'protein_coding', 69463439, 69489200, 1, 2453, 1),
(8, 'ENSMUST00000035233', 'Braf-201', 'protein_coding', 121717000, 121853500, -1, 2300, 1);

-- Insert transcripts (Zebrafish)
INSERT INTO transcript (gene_id, transcript_stable_id, transcript_name, transcript_biotype, start_position, end_position, strand, transcript_length, is_canonical) VALUES
(9, 'ENSDART00000090913', 'tp53-201', 'protein_coding', 28547832, 28565255, 1, 1692, 1),
(10, 'ENSDART00000165814', 'brca2-201', 'protein_coding', 45123456, 45178901, -1, 10890, 1);

-- Insert proteins (Human)
INSERT INTO protein (transcript_id, protein_stable_id, protein_sequence, protein_length, molecular_weight, isoelectric_point) VALUES
(1, 'ENSP00000369497', 'MPIGSKERPTFFEIFKTRCNKADLGPISLNWFEELSSEAPPYNSEPAEESEHKNNNYEPNLFKTPQR', 3418, 384232.15, 6.85),
(3, 'ENSP00000284967', 'MPKKKPTPIQLNPAPDGSTKDPKAEGKRGQVKGKPKAWQMNLKFGKLRFAQTKDIIIKAKPKQATFRSI', 766, 86452.23, 9.14),
(4, 'ENSP00000269305', 'MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPV', 393, 43653.34, 6.33),
(6, 'ENSP00000369082', 'MAAAGPGAAAGPGAGGPALAGPSFKPTPSLSLQPGLPGAAGPPGAAGPPGPPGPGSPGLPGPQ', 239, 26432.45, 10.23),
(7, 'ENSP00000230882', 'MNFLLSWVHWSLALLLYLHHAKWSQAAPMAEGGGQNHHEVVKFMDVYQRSYCHPIETLVDIFQEYPDEIEYIFKP', 412, 46155.23, 8.92);

-- Insert proteins (Mouse)
INSERT INTO protein (transcript_id, protein_stable_id, protein_sequence, protein_length, molecular_weight, isoelectric_point) VALUES
(8, 'ENSMUSP00000105932', 'MPIGSKERPTFFEIFKTRCNKADLGPISLNWFEELSSEAPPYNSEPAEESEHKNNNYEPNLFKTPQR', 3329, 373892.45, 6.79),
(9, 'ENSMUSP00000005585', 'MTAMEESQSDISLELPLSQETFSGLWKLLPPEDILPSPHCMDDLML', 387, 43012.56, 6.28),
(10, 'ENSMUSP00000035233', 'MAALSGGGGGAEPGQALFNGDMEPEAGAGAGAAASSAADPAIPEEVWNIKQMIKLTQEHIEALLDKFGGEHNPPSIYLEAYEE', 753, 84923.12, 8.98);

-- Insert proteins (Zebrafish)
INSERT INTO protein (transcript_id, protein_stable_id, protein_sequence, protein_length, molecular_weight, isoelectric_point) VALUES
(11, 'ENSDARP00000085221', 'MEPVQSDMSLELPLGQETFSHLWKLLPPESMVLTMDDVMLSP', 361, 40123.45, 6.01),
(12, 'ENSDARP00000139022', 'MPIGSKERPTFFEIFKTRCNKADLGPISLNWFEELSAEAPPYNSEPAEESDHKNNNYEPNLFKTPQR', 3234, 361234.78, 6.72);

-- Insert sample GO terms
INSERT INTO gene_ontology (go_id, go_name, go_namespace, go_definition) VALUES
('GO:0006281', 'DNA repair', 'biological_process', 'The process of restoring DNA after damage'),
('GO:0006915', 'apoptosis', 'biological_process', 'Programmed cell death'),
('GO:0005634', 'nucleus', 'cellular_component', 'A membrane-bounded organelle of eukaryotic cells'),
('GO:0003677', 'DNA binding', 'molecular_function', 'Interacting selectively with DNA'),
('GO:0000122', 'negative regulation of transcription', 'biological_process', 'Any process that stops transcription');

-- Insert gene-GO annotations (Human)
INSERT INTO gene_go_annotation (gene_id, go_id, evidence_code, annotation_source) VALUES
(1, 'GO:0006281', 'IEA', 'Ensembl'),
(1, 'GO:0005634', 'IDA', 'Ensembl'),
(2, 'GO:0006915', 'IMP', 'Ensembl'),
(3, 'GO:0006915', 'IDA', 'Ensembl'),
(3, 'GO:0005634', 'IDA', 'Ensembl'),
(3, 'GO:0003677', 'IDA', 'Ensembl'),
(3, 'GO:0000122', 'IMP', 'Ensembl');

-- Insert gene-GO annotations (Mouse)
INSERT INTO gene_go_annotation (gene_id, go_id, evidence_code, annotation_source) VALUES
(6, 'GO:0006281', 'IEA', 'Ensembl'),
(7, 'GO:0006915', 'IDA', 'Ensembl'),
(7, 'GO:0003677', 'IDA', 'Ensembl');

-- Insert gene-GO annotations (Zebrafish)
INSERT INTO gene_go_annotation (gene_id, go_id, evidence_code, annotation_source) VALUES
(9, 'GO:0006915', 'IEA', 'Ensembl'),
(9, 'GO:0003677', 'IEA', 'Ensembl'),
(10, 'GO:0006281', 'IEA', 'Ensembl');

-- Insert sample protein domains
INSERT INTO protein_domain (domain_accession, domain_name, domain_description, domain_type, database_source) VALUES
('PF00533', 'BRCA2 repeat', 'BRCA2 repeat profile', 'Family', 'Pfam'),
('PF00017', 'SH2 domain', 'Src homology 2 domain', 'Domain', 'Pfam'),
('PF00870', 'P53 DNA-binding domain', 'P53 DNA-binding domain', 'Domain', 'Pfam'),
('PF07714', 'Protein kinase domain', 'Protein tyrosine and serine/threonine kinase', 'Domain', 'Pfam');

-- Insert protein-domain annotations
INSERT INTO protein_domain_annotation (protein_id, domain_id, start_position, end_position, e_value, score) VALUES
(1, 1, 1002, 1036, 0.001, 45.2),
(1, 1, 1212, 1246, 0.001, 43.8),
(2, 4, 235, 490, 0.000, 298.5),
(3, 3, 94, 289, 0.000, 215.3),
(8, 1, 995, 1029, 0.001, 44.9),
(9, 3, 92, 287, 0.000, 213.7);

-- Insert sample pathways
INSERT INTO pathway (pathway_accession, pathway_name, pathway_description, pathway_category, database_source) VALUES
('R-HSA-5693532', 'DNA Double-Strand Break Repair', 'Pathway for repairing DNA double-strand breaks', 'DNA Repair', 'Reactome'),
('R-HSA-109581', 'Apoptosis', 'Programmed cell death pathway', 'Cell Death', 'Reactome'),
('R-HSA-5683057', 'MAPK family signaling cascades', 'Signal transduction via MAP kinases', 'Signaling', 'Reactome');

-- Insert gene-pathway annotations
INSERT INTO gene_pathway_annotation (gene_id, pathway_id, annotation_source) VALUES
(1, 1, 'Reactome'),
(3, 1, 'Reactome'),
(3, 2, 'Reactome'),
(2, 3, 'Reactome'),
(6, 1, 'Reactome'),
(7, 2, 'Reactome'),
(8, 3, 'Reactome');

-- Insert sample genetic variants (Human chromosome 17 - BRCA2)
INSERT INTO genetic_variant (chromosome_id, variant_name, variant_type, start_position, end_position, reference_allele, alternate_allele, variant_class, clinical_significance) VALUES
(1, 'rs80359550', 'SNP', 32363178, 32363178, 'G', 'A', 'missense_variant', 'Pathogenic'),
(1, 'rs80359505', 'SNP', 32370402, 32370402, 'C', 'T', 'nonsense', 'Pathogenic'),
(3, 'rs28934578', 'SNP', 29541762, 29541762, 'C', 'T', 'missense_variant', 'Pathogenic');

-- Insert variant-gene annotations
INSERT INTO variant_gene_annotation (variant_id, gene_id, variant_effect, impact_severity, annotation_source) VALUES
(1, 1, 'missense_variant', 'moderate', 'ClinVar'),
(2, 1, 'stop_gained', 'high', 'ClinVar'),
(3, 3, 'missense_variant', 'moderate', 'ClinVar');

-- Insert ortholog relationships
INSERT INTO ortholog (gene_a_id, gene_b_id, orthology_type, orthology_confidence, percentage_identity, alignment_coverage) VALUES
(1, 6, 'one2one', 0.95, 89.5, 95.2),  -- Human BRCA2 - Mouse Brca2
(3, 7, 'one2one', 0.98, 91.2, 96.8),  -- Human TP53 - Mouse Trp53
(3, 9, 'one2one', 0.92, 75.3, 88.5),  -- Human TP53 - Zebrafish tp53
(1, 10, 'one2one', 0.89, 72.1, 82.3); -- Human BRCA2 - Zebrafish brca2

-- Verify insertion
SELECT 'Data population completed successfully!' as Status;

SELECT 
    'Species' as Entity,
    COUNT(*) as Count
FROM species
UNION ALL
SELECT 'Chromosomes', COUNT(*) FROM chromosome
UNION ALL
SELECT 'Genes', COUNT(*) FROM gene
UNION ALL
SELECT 'Transcripts', COUNT(*) FROM transcript
UNION ALL
SELECT 'Proteins', COUNT(*) FROM protein
UNION ALL
SELECT 'GO Terms', COUNT(*) FROM gene_ontology
UNION ALL
SELECT 'Gene-GO Annotations', COUNT(*) FROM gene_go_annotation
UNION ALL
SELECT 'Protein Domains', COUNT(*) FROM protein_domain
UNION ALL
SELECT 'Protein-Domain Annotations', COUNT(*) FROM protein_domain_annotation
UNION ALL
SELECT 'Pathways', COUNT(*) FROM pathway
UNION ALL
SELECT 'Gene-Pathway Annotations', COUNT(*) FROM gene_pathway_annotation
UNION ALL
SELECT 'Genetic Variants', COUNT(*) FROM genetic_variant
UNION ALL
SELECT 'Variant-Gene Annotations', COUNT(*) FROM variant_gene_annotation
UNION ALL
SELECT 'Orthologs', COUNT(*) FROM ortholog;
