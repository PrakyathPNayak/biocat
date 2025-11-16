"""
Database Connection Module for Biocat Interface
Handles MySQL database connections and query execution
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
import logging
from typing import Optional, Dict, Any, List, Tuple
from contextlib import contextmanager


class BiocatDatabase:
    """Database connection handler for the Biocat biological database"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize database connection with configuration

        Args:
            config: Database configuration dictionary with keys:
                   host, port, user, password, database
        """
        self.config = config or {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "",
            "database": "biocat",
            "charset": "utf8mb4",
            "use_unicode": True,
            "autocommit": True,
        }
        self.connection = None
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging for database operations"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """
        Establish database connection

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self.connection and self.connection.is_connected():
                return True

            self.connection = mysql.connector.connect(**self.config)

            if self.connection.is_connected():
                self.logger.info("Successfully connected to Biocat database")
                return True
            else:
                self.logger.error("Failed to connect to database")
                return False

        except Error as e:
            self.logger.error(f"Database connection error: {e}")
            self.connection = None
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("Database connection closed")

    def is_connected(self) -> bool:
        """Check if database connection is active"""
        return self.connection and self.connection.is_connected()

    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        cursor = None
        try:
            if not self.is_connected():
                if not self.connect():
                    raise Error("Could not establish database connection")

            cursor = self.connection.cursor(dictionary=True)
            yield cursor

        except Error as e:
            self.logger.error(f"Cursor error: {e}")
            if cursor:
                cursor.close()
            raise
        finally:
            if cursor:
                cursor.close()

    def execute_query(
        self, query: str, params: Optional[Tuple] = None, fetch_all: bool = True
    ) -> Optional[List[Dict]]:
        """
        Execute a SELECT query and return results

        Args:
            query: SQL query string
            params: Query parameters tuple
            fetch_all: Whether to fetch all results or just one

        Returns:
            List of dictionaries containing query results, or None if error
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())

                if fetch_all:
                    results = cursor.fetchall()
                else:
                    results = cursor.fetchone()
                    results = [results] if results else []

                self.logger.info(
                    f"Query executed successfully, returned {len(results)} rows"
                )
                return results

        except Error as e:
            self.logger.error(f"Query execution error: {e}")
            self.logger.error(f"Query: {query}")
            if params:
                self.logger.error(f"Parameters: {params}")
            return None

    def execute_query_df(
        self, query: str, params: Optional[Tuple] = None
    ) -> Optional[pd.DataFrame]:
        """
        Execute query and return results as pandas DataFrame

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            pandas DataFrame with query results, or None if error
        """
        try:
            results = self.execute_query(query, params)
            if results is not None:
                df = pd.DataFrame(results)
                self.logger.info(f"DataFrame created with shape: {df.shape}")
                return df
            return None

        except Exception as e:
            self.logger.error(f"DataFrame creation error: {e}")
            return None

    def execute_update(self, query: str, params: Optional[Tuple] = None) -> bool:
        """
        Execute an UPDATE, INSERT, or DELETE query

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()

                affected_rows = cursor.rowcount
                self.logger.info(
                    f"Update executed successfully, affected {affected_rows} rows"
                )
                return True

        except Error as e:
            self.logger.error(f"Update execution error: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def get_table_info(self, table_name: str) -> Optional[pd.DataFrame]:
        """
        Get information about a table structure

        Args:
            table_name: Name of the table

        Returns:
            DataFrame with table structure information
        """
        query = f"DESCRIBE {table_name}"
        return self.execute_query_df(query)

    def get_table_names(self) -> List[str]:
        """
        Get list of all table names in the database

        Returns:
            List of table names
        """
        query = "SHOW TABLES"
        results = self.execute_query(query)

        if results:
            # Extract table names from the results
            table_key = f"Tables_in_{self.config['database']}"
            return [row[table_key] for row in results]
        return []

    def get_row_count(self, table_name: str) -> int:
        """
        Get number of rows in a table

        Args:
            table_name: Name of the table

        Returns:
            Number of rows in the table
        """
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query, fetch_all=False)

        if result and len(result) > 0:
            return result[0]["count"]
        return 0

    def test_connection(self) -> Dict[str, Any]:
        """
        Test database connection and return status information

        Returns:
            Dictionary with connection status and database information
        """
        status = {
            "connected": False,
            "database_name": None,
            "server_version": None,
            "tables": [],
            "error": None,
        }

        try:
            if self.connect():
                status["connected"] = True
                status["database_name"] = self.config["database"]

                with self.get_cursor() as cursor:
                    cursor.execute("SELECT VERSION() as version")
                    version_result = cursor.fetchone()
                    if version_result:
                        status["server_version"] = version_result["version"]

                status["tables"] = self.get_table_names()

        except Exception as e:
            status["error"] = str(e)
            self.logger.error(f"Connection test failed: {e}")

        return status

    def get_database_stats(self) -> Optional[pd.DataFrame]:
        """
        Get basic statistics about the database

        Returns:
            DataFrame with database statistics
        """
        query = """
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
        """

        return self.execute_query_df(query)

    def search_genes(self, search_term: str, limit: int = 50) -> Optional[pd.DataFrame]:
        """
        Search for genes by symbol, name, or description

        Args:
            search_term: Term to search for
            limit: Maximum number of results to return

        Returns:
            DataFrame with matching genes
        """
        search_pattern = f"%{search_term}%"
        query = """
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
        ORDER BY s.species_name, g.gene_symbol
        LIMIT %s
        """

        return self.execute_query_df(
            query, (search_pattern, search_pattern, search_pattern, limit)
        )

    def get_protein_sequence(self, protein_id: str) -> Optional[str]:
        """
        Get protein sequence by protein stable ID

        Args:
            protein_id: Protein stable ID

        Returns:
            Protein sequence string or None if not found
        """
        query = """
        SELECT protein_sequence
        FROM protein
        WHERE protein_stable_id = %s
        """

        result = self.execute_query(query, (protein_id,), fetch_all=False)
        if result and len(result) > 0:
            return result[0]["protein_sequence"]
        return None

    def check_dna_sequence_availability(self) -> Dict[str, Any]:
        """
        Check what DNA sequence data is available in the database

        Returns:
            Dictionary with information about DNA sequence availability
        """
        if not self.is_connected():
            return {"error": "Not connected to database"}

        try:
            results = {}

            # Check for sequence columns in various tables
            sequence_checks = [
                ("chromosome", "sequence", "Chromosome sequences"),
                ("gene", "dna_sequence", "Gene DNA sequences"),
                ("transcript", "cdna_sequence", "cDNA sequences"),
                ("transcript", "dna_sequence", "Transcript DNA sequences"),
                ("protein", "protein_sequence", "Protein sequences (amino acids)"),
                ("exon", "sequence", "Exon sequences"),
                ("intron", "sequence", "Intron sequences"),
            ]

            for table, column, description in sequence_checks:
                query = f"""
                    SELECT COUNT(*) as total_count,
                           COUNT({column}) as sequence_count,
                           ROUND(AVG(LENGTH({column})), 0) as avg_length
                    FROM {table}
                    WHERE {column} IS NOT NULL AND {column} != ''
                """

                try:
                    result = self.execute_query(query)
                    if result and len(result) > 0:
                        row = result[0]
                        if row["sequence_count"] > 0:
                            results[f"{table}.{column}"] = {
                                "description": description,
                                "table": table,
                                "column": column,
                                "sequence_count": row["sequence_count"],
                                "avg_length": row["avg_length"],
                            }
                except Exception as e:
                    # Column doesn't exist, skip it
                    continue

            # Check for any other potential sequence columns
            for table in [
                "chromosome",
                "gene",
                "transcript",
                "protein",
                "exon",
                "intron",
            ]:
                try:
                    info_query = f"DESCRIBE {table}"
                    columns = self.execute_query(info_query)
                    if columns:
                        for col_info in columns:
                            col_name = col_info["Field"].lower()
                            if (
                                "seq" in col_name
                                or "dna" in col_name
                                or "rna" in col_name
                            ) and col_name not in [
                                item["column"] for item in results.values()
                            ]:
                                # Check if this column has data
                                check_query = f"SELECT COUNT(*) as count FROM {table} WHERE {col_info['Field']} IS NOT NULL AND {col_info['Field']} != ''"
                                check_result = self.execute_query(check_query)
                                if check_result and check_result[0]["count"] > 0:
                                    results[f"{table}.{col_info['Field']}"] = {
                                        "description": f"{table.title()} {col_info['Field']}",
                                        "table": table,
                                        "column": col_info["Field"],
                                        "sequence_count": check_result[0]["count"],
                                        "avg_length": None,
                                    }
                except Exception:
                    continue

            return {"available_sequences": results, "total_sources": len(results)}

        except Exception as e:
            return {"error": f"Failed to check sequence availability: {str(e)}"}

    def get_dna_sequences(
        self,
        source_table: str,
        source_column: str,
        limit: int = 50,
        min_length: int = 10,
    ) -> Optional[pd.DataFrame]:
        """
        Fetch DNA sequences from the specified table and column

        Args:
            source_table: Table name containing sequences
            source_column: Column name containing sequences
            limit: Maximum number of sequences to fetch
            min_length: Minimum sequence length to include

        Returns:
            DataFrame with sequences and metadata
        """
        if not self.is_connected():
            return None

        try:
            # Build the query based on the table
            if source_table == "chromosome":
                query = f"""
                    SELECT
                        c.chromosome_id,
                        c.chromosome_name,
                        s.species_name,
                        c.sequence_length,
                        LEFT(c.{source_column}, 1000) as sequence_preview,
                        c.{source_column} as full_sequence
                    FROM chromosome c
                    JOIN genome_assembly ga ON c.assembly_id = ga.assembly_id
                    JOIN species s ON ga.species_id = s.species_id
                    WHERE c.{source_column} IS NOT NULL
                    AND LENGTH(c.{source_column}) >= {min_length}
                    ORDER BY c.sequence_length DESC
                    LIMIT {limit}
                """
            elif source_table == "gene":
                query = f"""
                    SELECT
                        g.gene_id,
                        g.gene_symbol,
                        g.gene_name,
                        s.species_name,
                        c.chromosome_name,
                        LENGTH(g.{source_column}) as sequence_length,
                        LEFT(g.{source_column}, 1000) as sequence_preview,
                        g.{source_column} as full_sequence
                    FROM gene g
                    JOIN species s ON g.species_id = s.species_id
                    LEFT JOIN chromosome c ON g.chromosome_id = c.chromosome_id
                    WHERE g.{source_column} IS NOT NULL
                    AND LENGTH(g.{source_column}) >= {min_length}
                    ORDER BY LENGTH(g.{source_column}) DESC
                    LIMIT {limit}
                """
            elif source_table == "transcript":
                query = f"""
                    SELECT
                        t.transcript_id,
                        t.transcript_stable_id,
                        g.gene_symbol,
                        g.gene_name,
                        s.species_name,
                        LENGTH(t.{source_column}) as sequence_length,
                        LEFT(t.{source_column}, 1000) as sequence_preview,
                        t.{source_column} as full_sequence
                    FROM transcript t
                    JOIN gene g ON t.gene_id = g.gene_id
                    JOIN species s ON g.species_id = s.species_id
                    WHERE t.{source_column} IS NOT NULL
                    AND LENGTH(t.{source_column}) >= {min_length}
                    ORDER BY LENGTH(t.{source_column}) DESC
                    LIMIT {limit}
                """
            else:
                # Generic query for other tables
                query = f"""
                    SELECT
                        *,
                        LENGTH({source_column}) as sequence_length,
                        LEFT({source_column}, 1000) as sequence_preview,
                        {source_column} as full_sequence
                    FROM {source_table}
                    WHERE {source_column} IS NOT NULL
                    AND LENGTH({source_column}) >= {min_length}
                    ORDER BY LENGTH({source_column}) DESC
                    LIMIT {limit}
                """

            return self.execute_query_df(query)

        except Exception as e:
            self.logger.error(f"Failed to fetch DNA sequences: {str(e)}")
            return None

    def get_random_dna_sequences(
        self, source_table: str, source_column: str, count: int = 10
    ) -> Optional[List[str]]:
        """
        Get random DNA sequences from the database for analysis

        Args:
            source_table: Table containing sequences
            source_column: Column containing sequences
            count: Number of sequences to return

        Returns:
            List of DNA sequence strings
        """
        if not self.is_connected():
            return None

        try:
            query = f"""
                SELECT {source_column} as sequence
                FROM {source_table}
                WHERE {source_column} IS NOT NULL
                AND LENGTH({source_column}) >= 20
                AND LENGTH({source_column}) <= 5000
                ORDER BY RAND()
                LIMIT {count}
            """

            result = self.execute_query(query)
            if result:
                return [row["sequence"] for row in result if row["sequence"]]
            return []

        except Exception as e:
            self.logger.error(f"Failed to fetch random DNA sequences: {str(e)}")
            return None

    def search_sequences_by_pattern(
        self, pattern: str, source_table: str, source_column: str, limit: int = 20
    ) -> Optional[pd.DataFrame]:
        """
        Search for sequences containing a specific pattern

        Args:
            pattern: DNA pattern to search for (e.g., "ATCG")
            source_table: Table to search in
            source_column: Column containing sequences
            limit: Maximum results to return

        Returns:
            DataFrame with matching sequences
        """
        if not self.is_connected():
            return None

        try:
            # Clean the pattern to only include valid DNA bases
            import re

            clean_pattern = re.sub(r"[^ATCG]", "", pattern.upper())

            if len(clean_pattern) < 3:
                return None

            if source_table == "gene":
                query = f"""
                    SELECT
                        g.gene_symbol,
                        g.gene_name,
                        s.species_name,
                        LENGTH(g.{source_column}) as sequence_length,
                        LOCATE('{clean_pattern}', g.{source_column}) as pattern_position,
                        LEFT(g.{source_column}, 500) as sequence_preview
                    FROM gene g
                    JOIN species s ON g.species_id = s.species_id
                    WHERE g.{source_column} LIKE '%{clean_pattern}%'
                    ORDER BY sequence_length DESC
                    LIMIT {limit}
                """
            elif source_table == "transcript":
                query = f"""
                    SELECT
                        t.transcript_stable_id,
                        g.gene_symbol,
                        s.species_name,
                        LENGTH(t.{source_column}) as sequence_length,
                        LOCATE('{clean_pattern}', t.{source_column}) as pattern_position,
                        LEFT(t.{source_column}, 500) as sequence_preview
                    FROM transcript t
                    JOIN gene g ON t.gene_id = g.gene_id
                    JOIN species s ON g.species_id = s.species_id
                    WHERE t.{source_column} LIKE '%{clean_pattern}%'
                    ORDER BY sequence_length DESC
                    LIMIT {limit}
                """
            else:
                query = f"""
                    SELECT
                        *,
                        LENGTH({source_column}) as sequence_length,
                        LOCATE('{clean_pattern}', {source_column}) as pattern_position,
                        LEFT({source_column}, 500) as sequence_preview
                    FROM {source_table}
                    WHERE {source_column} LIKE '%{clean_pattern}%'
                    ORDER BY LENGTH({source_column}) DESC
                    LIMIT {limit}
                """

            return self.execute_query_df(query)

        except Exception as e:
            self.logger.error(f"Failed to search sequences: {str(e)}")
            return None

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


def get_database_connection(config: Optional[Dict[str, Any]] = None) -> BiocatDatabase:
    """
    Get a database connection instance

    Args:
        config: Optional database configuration

    Returns:
        BiocatDatabase instance
    """
    if config:
        return BiocatDatabase(config)
    return BiocatDatabase()


def test_database_connection() -> Dict[str, Any]:
    """
    Test the default database connection

    Returns:
        Dictionary with connection test results
    """
    db = BiocatDatabase()
    return db.test_connection()
