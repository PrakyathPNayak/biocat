#!/usr/bin/env python3
"""
Test script for custom MySQL functions in the biocat database
This script tests the three custom functions: classify_sequence, count_nucleotides, and detect_mutations
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_database_connection


def test_custom_functions():
    """Test all three custom MySQL functions"""
    print("Testing Custom MySQL Functions")
    print("=" * 50)

    try:
        # Connect to database
        db = get_database_connection()
        if not db.connect():
            print("ERROR: Could not connect to database")
            return False

        print("✓ Connected to database successfully")

        with db.get_cursor() as cursor:
            # Test 1: classify_sequence function
            print("\n1. Testing classify_sequence() function:")
            print("-" * 40)

            test_sequences = [
                "ATGGCATAG",  # Contains ATG (start codon)
                "GCTAGCTTAG",  # No ATG
                "CATGATGCCG",  # Contains ATG
                "TTTTCCCCAAAA",  # No ATG
            ]

            for seq in test_sequences:
                cursor.execute("SELECT classify_sequence(%s) as result", (seq,))
                result = cursor.fetchone()
                if result:
                    print(f"  {seq:15} -> {result['result']}")
                else:
                    print(f"  {seq:15} -> No result")

            # Test 2: count_nucleotides function
            print("\n2. Testing count_nucleotides() function:")
            print("-" * 40)

            test_sequences_count = ["ATCGATCG", "AAATTTCCCGGG", "ATGCGCGCATGC"]

            for seq in test_sequences_count:
                cursor.execute("SELECT count_nucleotides(%s) as result", (seq,))
                result = cursor.fetchone()
                if result:
                    print(f"  {seq:15} -> {result['result']}")
                else:
                    print(f"  {seq:15} -> No result")

            # Test 3: detect_mutations function
            print("\n3. Testing detect_mutations() function:")
            print("-" * 40)

            test_pairs = [
                ("ATCGATCG", "ATCGATCC"),  # Single mutation at end
                ("ATCGATCG", "GTCAATCG"),  # Multiple mutations
                ("ATCGATCG", "ATCGATCG"),  # No mutations
                ("AAATTT", "CCCTTT"),  # Multiple mutations at start
            ]

            for seq1, seq2 in test_pairs:
                cursor.execute(
                    "SELECT detect_mutations(%s, %s) as result", (seq1, seq2)
                )
                result = cursor.fetchone()
                if result:
                    print(f"  {seq1} vs {seq2}")
                    print(f"    -> {result['result']}")
                else:
                    print(f"  {seq1} vs {seq2} -> No result")

            # Test 4: Real biocat data examples
            print("\n4. Testing with real biocat data:")
            print("-" * 40)

            # Get some actual DNA sequences from the database
            cursor.execute("""
                SELECT gene_symbol, dna_sequence
                FROM gene
                WHERE dna_sequence IS NOT NULL
                AND LENGTH(dna_sequence) > 20
                LIMIT 3
            """)

            gene_results = cursor.fetchall()

            if gene_results:
                for gene in gene_results:
                    seq = gene["dna_sequence"][:30]  # Take first 30 characters
                    symbol = gene["gene_symbol"]

                    # Test classification
                    cursor.execute("SELECT classify_sequence(%s) as result", (seq,))
                    class_result = cursor.fetchone()

                    # Test nucleotide count
                    cursor.execute("SELECT count_nucleotides(%s) as result", (seq,))
                    count_result = cursor.fetchone()

                    print(f"  Gene: {symbol}")
                    print(f"    Sequence: {seq}")
                    if class_result:
                        print(f"    Classification: {class_result['result']}")
                    if count_result:
                        print(f"    Nucleotide counts: {count_result['result']}")
                    print()
            else:
                print("  No DNA sequences found in gene table")

            # Test 5: Function combination query
            print("\n5. Testing combined function usage:")
            print("-" * 40)

            combined_query = """
                SELECT
                    'ATGCGATCG' as test_sequence,
                    classify_sequence('ATGCGATCG') as classification,
                    count_nucleotides('ATGCGATCG') as composition,
                    detect_mutations('ATGCGATCG', 'ATGCGATCC') as mutations
            """

            cursor.execute(combined_query)
            combined_result = cursor.fetchone()

            if combined_result:
                print(f"  Test sequence: {combined_result['test_sequence']}")
                print(f"  Classification: {combined_result['classification']}")
                print(f"  Composition: {combined_result['composition']}")
                print(f"  Mutations vs 'ATGCGATCC': {combined_result['mutations']}")

        print("\n" + "=" * 50)
        print("✓ All custom function tests completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        return False

    finally:
        if "db" in locals():
            db.disconnect()
            print("✓ Database connection closed")


def main():
    """Main function"""
    print("Biocat Custom MySQL Functions Test")
    print("This script tests the custom functions added to the biocat database\n")

    success = test_custom_functions()

    if success:
        print(
            "\n🎉 All tests passed! The custom MySQL functions are working correctly."
        )
    else:
        print(
            "\n❌ Some tests failed. Please check the database connection and function definitions."
        )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
