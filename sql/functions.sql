-- 1. Basic Sequence Classification
DELIMITER //
CREATE FUNCTION classify_sequence(dna_sequence TEXT) 
RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
  IF LOCATE('ATG', dna_sequence) > 0 THEN
    RETURN 'Likely Gene';
  ELSE
    RETURN 'Unknown';
  END IF;
END //
DELIMITER ;

-- 2. Counting Nucleotide Frequencies
DELIMITER //
CREATE FUNCTION count_nucleotides(dna_sequence TEXT) 
RETURNS JSON
DETERMINISTIC
BEGIN
  DECLARE a_count, c_count, t_count, g_count INT;
  SET a_count = LENGTH(dna_sequence) - LENGTH(REPLACE(dna_sequence, 'A', ''));
  SET c_count = LENGTH(dna_sequence) - LENGTH(REPLACE(dna_sequence, 'C', ''));
  SET t_count = LENGTH(dna_sequence) - LENGTH(REPLACE(dna_sequence, 'T', ''));
  SET g_count = LENGTH(dna_sequence) - LENGTH(REPLACE(dna_sequence, 'G', ''));
  RETURN JSON_OBJECT('A', a_count, 'C', c_count, 'T', t_count, 'G', g_count);
END //
DELIMITER ;

-- 3. Mutation/Variant Detection (Base-by-Base Comparison)
DELIMITER //
CREATE FUNCTION detect_mutations(seq1 TEXT, seq2 TEXT) 
RETURNS TEXT
DETERMINISTIC
BEGIN
  DECLARE len INT;
  DECLARE i INT DEFAULT 1;
  DECLARE mutations TEXT DEFAULT '';
  DECLARE base1 CHAR(1);
  DECLARE base2 CHAR(1);
  
  SET len = LEAST(CHAR_LENGTH(seq1), CHAR_LENGTH(seq2));
  
  WHILE i <= len DO
    SET base1 = SUBSTRING(seq1, i, 1);
    SET base2 = SUBSTRING(seq2, i, 1);
    IF base1 <> base2 THEN
      SET mutations = CONCAT(mutations, 'Pos ', i, ': ', base1, '->', base2, '; ');
    END IF;
    SET i = i + 1;
  END WHILE;
  
  IF mutations = '' THEN
    RETURN 'No mutations found';
  ELSE
    RETURN mutations;
  END IF;
END //
DELIMITER ;