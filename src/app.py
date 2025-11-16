"""
Biocat Database Interface - Main Gradio Application
A comprehensive interface for exploring biological data in the biocat database
"""

import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from typing import Optional, Dict, Tuple, List
import traceback

# Global variables
db = None
visualizer = None

# Import handling with fallbacks
MODULES_AVAILABLE = True
error_message = ""

try:
    from database import BiocatDatabase, get_database_connection
    from sql_queries import (
        get_query_categories,
        get_queries_in_category,
        get_query,
    )
    from dna_visualization import (
        DNAVisualizer,
        create_genomic_overview_plot,
        create_protein_length_distribution,
        create_chromosome_gene_density_plot,
    )
except ImportError as e:
    MODULES_AVAILABLE = False
    error_message = f"Warning: Could not import custom modules: {e}\nPlease ensure all dependencies are installed."
    print(error_message)


def initialize_app():
    """Initialize the application components"""
    global visualizer

    if not MODULES_AVAILABLE:
        return f"Required modules are not available: {error_message}"

    try:
        # Import functions are available at this point
        from dna_visualization import DNAVisualizer

        visualizer = DNAVisualizer()
        return "SUCCESS: Visualization module initialized successfully. Please connect to database using the Connection tab."
    except Exception as e:
        return f"ERROR: Failed to initialize visualization module: {str(e)}"


def check_dna_availability() -> Tuple[str, Optional[Dict]]:
    """Check what DNA sequence data is available in the database"""
    if not MODULES_AVAILABLE:
        return "Database modules not available", None

    try:
        if not db:
            return (
                "ERROR: No database connection established. Please connect to database first using the Connection tab.",
                None,
            )

        if not db.is_connected():
            return (
                "ERROR: Database connection lost. Please reconnect to database using the Connection tab.",
                None,
            )

        availability_info = db.check_dna_sequence_availability()

        if "error" in availability_info:
            return f"ERROR: {availability_info['error']}", None

        if availability_info.get("total_sources", 0) == 0:
            return "No DNA sequence data found in the database", None

        return (
            f"SUCCESS: Found {availability_info['total_sources']} DNA sequence sources",
            availability_info,
        )

    except Exception as e:
        return f"ERROR: Failed to check DNA availability: {str(e)}", None


def fetch_dna_sequences(
    source_info: str, limit: int = 20
) -> Tuple[str, Optional[pd.DataFrame]]:
    """Fetch DNA sequences from the database"""
    if not MODULES_AVAILABLE:
        return "Database modules not available", None

    try:
        if not db:
            return (
                "ERROR: No database connection established. Please connect to database first using the Connection tab.",
                None,
            )

        if not db.is_connected():
            return (
                "ERROR: Database connection lost. Please reconnect to database using the Connection tab.",
                None,
            )

        if not source_info or "." not in source_info:
            return "ERROR: Please select a valid sequence source", None

        # Parse the source info (format: "table.column")
        table_name, column_name = source_info.split(".", 1)

        sequences_df = db.get_dna_sequences(
            table_name, column_name, limit=limit, min_length=10
        )

        if sequences_df is None or sequences_df.empty:
            return "No sequences found with the specified criteria", None

        return (
            f"SUCCESS: Retrieved {len(sequences_df)} DNA sequences from {table_name}.{column_name}",
            sequences_df,
        )

    except Exception as e:
        return f"ERROR: Failed to fetch DNA sequences: {str(e)}", None


def get_random_sequences_for_analysis(
    source_info: str, count: int = 5
) -> Tuple[str, List[str]]:
    """Get random DNA sequences for analysis"""
    if not MODULES_AVAILABLE:
        return "Database modules not available", []

    try:
        if not db:
            return (
                "ERROR: No database connection established. Please connect to database first using the Connection tab.",
                [],
            )

        if not db.is_connected():
            return (
                "ERROR: Database connection lost. Please reconnect to database using the Connection tab.",
                [],
            )

        if not source_info or "." not in source_info:
            return "ERROR: Please select a valid sequence source", []

        # Parse the source info
        table_name, column_name = source_info.split(".", 1)

        sequences = db.get_random_dna_sequences(table_name, column_name, count=count)

        if not sequences:
            return "No sequences found for analysis", []

        return f"SUCCESS: Retrieved {len(sequences)} random sequences", sequences

    except Exception as e:
        return f"ERROR: Failed to get random sequences: {str(e)}", []


def search_sequences_by_pattern(
    pattern: str, source_info: str, limit: int = 10
) -> Tuple[str, Optional[pd.DataFrame]]:
    """Search for DNA sequences containing a specific pattern"""
    if not MODULES_AVAILABLE:
        return "Database modules not available", None

    try:
        if not pattern or not pattern.strip():
            return "ERROR: Please enter a search pattern", None

        if not db:
            return (
                "ERROR: No database connection established. Please connect to database first using the Connection tab.",
                None,
            )

        if not db.is_connected():
            return (
                "ERROR: Database connection lost. Please reconnect to database using the Connection tab.",
                None,
            )

        if not source_info or "." not in source_info:
            return "ERROR: Please select a valid sequence source", None

        # Clean pattern to only include valid DNA bases
        import re

        clean_pattern = re.sub(r"[^ATCG]", "", pattern.upper())

        if len(clean_pattern) < 3:
            return (
                "ERROR: Pattern must contain at least 3 valid DNA bases (A, T, C, G)",
                None,
            )

        # Parse the source info
        table_name, column_name = source_info.split(".", 1)

        results_df = db.search_sequences_by_pattern(
            clean_pattern, table_name, column_name, limit=limit
        )

        if results_df is None or results_df.empty:
            return f"No sequences found containing pattern '{clean_pattern}'", None

        return (
            f"SUCCESS: Found {len(results_df)} sequences containing pattern '{clean_pattern}'",
            results_df,
        )

    except Exception as e:
        return f"ERROR: Failed to search sequences: {str(e)}", None


def test_connection(
    host: str, port: int, user: str, password: str, database: str
) -> Tuple[bool, str, Dict, str]:
    """Test database connection with provided credentials and update global connection"""
    global db

    if not MODULES_AVAILABLE:
        return (
            False,
            "Database modules not available",
            {},
            '<div style="color: orange; font-weight: bold;">WARNING: Modules Not Available</div>',
        )

    try:
        config = {
            "host": host,
            "port": int(port),
            "user": user,
            "password": password,
            "database": database,
        }
        from database import BiocatDatabase

        test_db = BiocatDatabase(config)
        connection_info = test_db.test_connection()

        if connection_info["connected"]:
            # Update global database connection
            if db:
                db.disconnect()
            db = test_db
            return (
                True,
                "SUCCESS: Connection successful! Database is now connected and ready for queries.",
                connection_info,
                '<div style="color: green; font-weight: bold;">CONNECTED: Database Ready</div>',
            )
        else:
            test_db.disconnect()
            return (
                False,
                f"ERROR: Connection failed: {connection_info.get('error', 'Unknown error')}",
                connection_info,
                '<div style="color: red; font-weight: bold;">ERROR: Connection Failed</div>',
            )
    except Exception as e:
        return (
            False,
            f"Connection test failed: {str(e)}",
            {},
            '<div style="color: red; font-weight: bold;">ERROR: Connection Error</div>',
        )


def get_database_overview() -> Tuple[str, Optional[pd.DataFrame]]:
    """Get basic overview of database statistics"""
    if not MODULES_AVAILABLE:
        return "Database modules not available", None

    try:
        if not db:
            return (
                "ERROR: No database connection established. Please connect to database first using the Connection tab.",
                None,
            )

        if not db.is_connected():
            return (
                "ERROR: Database connection lost. Please reconnect to database using the Connection tab.",
                None,
            )

        stats_df = db.get_database_stats()
        if stats_df is not None and not stats_df.empty:
            return "SUCCESS: Database overview retrieved successfully", stats_df
        else:
            return "WARNING: No data retrieved from database", None
    except Exception as e:
        return f"ERROR: Error getting database overview: {str(e)}", None


def execute_query(
    query: str, limit: int = 100
) -> Tuple[str, Optional[pd.DataFrame], Optional[go.Figure]]:
    """Execute a SQL query and return results"""
    if not MODULES_AVAILABLE:
        return "Database modules not available", None, None

    try:
        if not query.strip():
            return "Please enter a SQL query", None, None

        if not db:
            return (
                "ERROR: No database connection established. Please connect to database first using the Connection tab.",
                None,
                None,
            )

        if not db.is_connected():
            return (
                "ERROR: Database connection lost. Please reconnect to database using the Connection tab.",
                None,
                None,
            )

        # Add LIMIT if not present and it's a SELECT query
        query_upper = query.upper().strip()
        if query_upper.startswith("SELECT") and "LIMIT" not in query_upper:
            query = f"{query.rstrip(';')} LIMIT {limit};"

        result_df = db.execute_query_df(query)

        if result_df is None:
            return "Query executed but returned no data", None, None

        if result_df.empty:
            return "Query executed successfully but returned no rows", result_df, None

        # Create visualization based on result type
        visualization = None
        if len(result_df.columns) >= 2:
            try:
                # Try to create a basic plot if data looks suitable
                from dna_visualization import (
                    create_genomic_overview_plot,
                    create_protein_length_distribution,
                    create_chromosome_gene_density_plot,
                )

                if "gene_count" in result_df.columns.str.lower():
                    visualization = create_genomic_overview_plot(result_df)
                elif "protein_length" in result_df.columns.str.lower():
                    visualization = create_protein_length_distribution(result_df)
                elif "chromosome" in result_df.columns.str.lower():
                    visualization = create_chromosome_gene_density_plot(result_df)
            except Exception as viz_error:
                print(f"Visualization error: {viz_error}")

        return (
            f"SUCCESS: Query executed successfully. Retrieved {len(result_df)} rows.",
            result_df,
            visualization,
        )

    except Exception as e:
        error_msg = f"ERROR: Query execution failed: {str(e)}"
        print(f"Query error: {traceback.format_exc()}")
        return error_msg, None, None


def execute_custom_query(custom_query: str) -> Tuple[str, Optional[pd.DataFrame]]:
    """Execute a custom SQL query"""
    if not MODULES_AVAILABLE:
        return "Database modules not available", None

    try:
        if not custom_query.strip():
            return "Please enter a custom SQL query", None

        if not db:
            return (
                "ERROR: No database connection established. Please connect to database first using the Connection tab.",
                None,
            )

        if not db.is_connected():
            return (
                "ERROR: Database connection lost. Please reconnect to database using the Connection tab.",
                None,
            )

        result_df = db.execute_query_df(custom_query)

        if result_df is None:
            return "Query executed but returned no data", None

        return (
            f"SUCCESS: Custom query executed successfully. Retrieved {len(result_df)} rows.",
            result_df,
        )

    except Exception as e:
        return f"ERROR: Custom query execution failed: {str(e)}", None


def search_genes(
    search_term: str, limit: int = 50
) -> Tuple[str, Optional[pd.DataFrame]]:
    """Search for genes by symbol, name, or description"""
    if not MODULES_AVAILABLE:
        return "Database modules not available", None

    try:
        if not search_term.strip():
            return "Please enter a search term", None

        if not db:
            return (
                "ERROR: No database connection established. Please connect to database first using the Connection tab.",
                None,
            )

        if not db.is_connected():
            return (
                "ERROR: Database connection lost. Please reconnect to database using the Connection tab.",
                None,
            )

        result_df = db.search_genes(search_term, limit)

        if result_df is None or result_df.empty:
            return f"No genes found matching '{search_term}'", None

        return (
            f"SUCCESS: Found {len(result_df)} genes matching '{search_term}'",
            result_df,
        )

    except Exception as e:
        return f"ERROR: Gene search failed: {str(e)}", None


def get_protein_sequence_analysis(
    protein_id: str,
) -> Tuple[str, Optional[go.Figure], Optional[go.Figure]]:
    """Get and analyze protein sequence"""
    if not MODULES_AVAILABLE:
        return "Analysis modules not available", None, None

    try:
        if not protein_id.strip():
            return "Please enter a protein ID", None, None

        if not db:
            return (
                "ERROR: No database connection established. Please connect to database first using the Connection tab.",
                None,
                None,
            )

        if not db.is_connected():
            return (
                "ERROR: Database connection lost. Please reconnect to database using the Connection tab.",
                None,
                None,
            )

        # Get protein sequence
        sequence = db.get_protein_sequence(protein_id)
        if not sequence:
            return f"No sequence found for protein ID: {protein_id}", None, None

        if not visualizer:
            return "Visualizer not initialized", None, None

        # Analyze sequence
        composition_fig = visualizer.plot_amino_acid_composition(
            sequence, title=f"Amino Acid Composition - {protein_id}"
        )

        hydrophobicity_fig = visualizer.plot_hydrophobicity_profile(
            sequence, title=f"Hydrophobicity Profile - {protein_id}"
        )

        return (
            f"SUCCESS: Analysis completed for {protein_id} (length: {len(sequence)} aa)",
            composition_fig,
            hydrophobicity_fig,
        )

    except Exception as e:
        return f"ERROR: Protein analysis failed: {str(e)}", None, None


def analyze_dna_sequence(
    sequence: str,
) -> Tuple[Optional[go.Figure], Optional[go.Figure], Optional[go.Figure], str]:
    """Analyze DNA sequence composition, GC content, and create 3D helix visualization"""
    if not MODULES_AVAILABLE:
        return None, None, None, "Analysis modules not available"

    try:
        if not sequence.strip():
            return None, None, None, "Please enter a DNA sequence"

        if not visualizer:
            return None, None, None, "Visualizer not initialized"

        # Clean and validate sequence
        sequence = sequence.upper().replace(" ", "").replace("\n", "")

        composition_fig = visualizer.plot_nucleotide_composition(
            sequence, title="Nucleotide Composition"
        )
        gc_fig = visualizer.plot_gc_content_window(
            sequence, window_size=50, title="GC Content Analysis"
        )
        helix_fig = visualizer.plot_dna_double_helix(
            sequence, title="DNA Double Helix Structure", max_length=50
        )

        return (
            composition_fig,
            gc_fig,
            helix_fig,
            f"SUCCESS: Analysis completed for sequence of length {len(sequence)} bp",
        )

    except Exception as e:
        return None, None, None, f"ERROR: DNA analysis failed: {str(e)}"


def test_custom_function(function_name: str, seq1: str, seq2: Optional[str] = None):
    """Test custom MySQL functions with user-provided sequences"""
    if not MODULES_AVAILABLE:
        return "Error: Analysis modules not available"

    try:
        # Validate input sequences (basic DNA validation)
        if seq1:
            seq1 = seq1.upper().strip()
            if not all(c in "ATCG" for c in seq1):
                return "Error: Sequence 1 contains invalid characters. Only A, T, C, G allowed."

        if seq2:
            seq2 = seq2.upper().strip()
            if not all(c in "ATCG" for c in seq2):
                return "Error: Sequence 2 contains invalid characters. Only A, T, C, G allowed."

        # Build query based on function type
        if function_name == "classify_sequence":
            if not seq1:
                return "Error: Sequence 1 is required for classification"
            query = f"SELECT '{seq1}' as input_sequence, classify_sequence('{seq1}') as classification;"

        elif function_name == "count_nucleotides":
            if not seq1:
                return "Error: Sequence 1 is required for nucleotide counting"
            query = f"SELECT '{seq1}' as input_sequence, count_nucleotides('{seq1}') as nucleotide_counts;"

        elif function_name == "detect_mutations":
            if not seq1 or not seq2:
                return "Error: Both sequences are required for mutation detection"
            query = f"SELECT '{seq1}' as sequence1, '{seq2}' as sequence2, detect_mutations('{seq1}', '{seq2}') as mutations;"

        else:
            return f"Error: Unknown function: {function_name}"

        # Execute the query using existing infrastructure
        status, result_df, _ = execute_query(query, limit=10)

        if result_df is not None and not result_df.empty:
            # Format results as readable text
            result_text = f"{function_name}() Results:\n\n"
            result_text += f"Query: {query}\n\n"
            result_text += "Results:\n"
            for idx, row in result_df.iterrows():
                for col, val in row.items():
                    result_text += f"  {col}: {val}\n"
                result_text += "\n"
            return result_text.strip()
        else:
            return f"Error: Query failed: {status}"

    except Exception as e:
        return f"Error: Function test failed: {str(e)}"


def update_query_dropdown(category: str):
    """Update query dropdown based on selected category"""
    if not MODULES_AVAILABLE:
        return gr.Dropdown(choices=[], value="")

    from sql_queries import get_queries_in_category

    queries = get_queries_in_category(category)
    return gr.Dropdown(choices=list(queries.keys()), value="")


def get_query_description(category: str, query_name: str) -> str:
    """Get the SQL query for the selected category and query name"""
    if not MODULES_AVAILABLE:
        return "Query modules not available"

    if not category or not query_name:
        return ""

    from sql_queries import get_query

    query = get_query(category, query_name)
    return query if query else "Query not found"


def create_interface() -> gr.Blocks:
    """Create and configure the Gradio interface"""

    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .gr-button-primary {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border: none;
    }
    .gr-button-primary:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    }
    """

    with gr.Blocks(
        title="Biocat Database Interface", theme="soft", css=custom_css
    ) as interface:
        gr.Markdown(
            """
            # Biocat Database Interface
            ### A comprehensive tool for exploring biological sequence data

            This interface provides access to the Biocat biological database with tools for:
            - **Database querying** with predefined and custom SQL queries
            - **Gene and protein search** functionality
            - **DNA sequence analysis** and visualization
            - **Protein sequence analysis** and composition plots
            """
        )

        # Application status
        init_status = None
        init_btn = None

        with gr.Row():
            with gr.Column():
                if not MODULES_AVAILABLE:
                    gr.Markdown(
                        f"""
                        **WARNING: Required modules are not available**

                        {error_message}

                        Please install the required dependencies:
                        ```bash
                        pip install gradio pandas mysql-connector-python plotly biopython seaborn matplotlib
                        ```
                        """
                    )
                else:
                    init_status = gr.Textbox(
                        label="Application Status",
                        value="Click 'Initialize Visualization Module' to prepare DNA/protein analysis tools.",
                        interactive=False,
                    )
                    init_btn = gr.Button(
                        "Initialize Visualization Module", variant="primary"
                    )

                # Add connection status display
                with gr.Row():
                    connection_indicator = gr.HTML(
                        value='<div style="color: red; font-weight: bold;">STATUS: Not Connected to Database</div>',
                        elem_id="connection_indicator",
                    )

        if MODULES_AVAILABLE:
            with gr.Tabs():
                # Database Connection Tab
                with gr.Tab("Database Connection"):
                    gr.Markdown("### Database Connection Settings")

                    with gr.Row():
                        with gr.Column(scale=1):
                            host_input = gr.Textbox(label="Host", value="localhost")
                            port_input = gr.Number(label="Port", value=3306)
                            user_input = gr.Textbox(label="Username", value="root")
                        with gr.Column(scale=1):
                            password_input = gr.Textbox(
                                label="Password", type="password"
                            )
                            database_input = gr.Textbox(
                                label="Database", value="biocat"
                            )
                            test_btn = gr.Button("Test Connection", variant="primary")

                    connection_status = gr.Textbox(
                        label="Connection Status", interactive=False
                    )
                    connection_info = gr.JSON(label="Connection Details")

                # Database Overview Tab
                with gr.Tab("Database Overview"):
                    gr.Markdown("### Database Statistics and Overview")

                    overview_btn = gr.Button("Get Database Overview", variant="primary")
                    overview_status = gr.Textbox(label="Status", interactive=False)
                    overview_data = gr.DataFrame(label="Database Statistics")

                # Predefined Queries Tab
                with gr.Tab("Predefined Queries"):
                    gr.Markdown("### Execute Predefined Database Queries")

                    with gr.Row():
                        if MODULES_AVAILABLE:
                            from sql_queries import get_query_categories

                            categories = get_query_categories()
                        else:
                            categories = []
                        category_dropdown = gr.Dropdown(
                            label="Query Category",
                            choices=categories,
                            value=categories[0] if categories else None,
                        )
                        query_dropdown = gr.Dropdown(label="Select Query", choices=[])

                    query_display = gr.Code(
                        label="SQL Query",
                        language="sql",
                        value="SELECT * FROM gene LIMIT 10;",
                        lines=8,
                    )

                    with gr.Row():
                        limit_input = gr.Number(
                            label="Result Limit", value=100, minimum=1, maximum=10000
                        )
                        execute_btn = gr.Button("Execute Query", variant="primary")

                    query_status = gr.Textbox(
                        label="Execution Status", interactive=False
                    )
                    query_results = gr.DataFrame(label="Query Results")
                    query_viz = gr.Plot(label="Data Visualization")

                # Custom Query Tab
                with gr.Tab("Custom Query"):
                    gr.Markdown("### Execute Custom SQL Queries")

                    custom_query_input = gr.Code(
                        label="Custom SQL Query",
                        language="sql",
                        value="",
                        lines=10,
                    )
                    custom_execute_btn = gr.Button(
                        "Execute Custom Query", variant="primary"
                    )

                    custom_status = gr.Textbox(
                        label="Execution Status", interactive=False
                    )
                    custom_results = gr.DataFrame(label="Query Results")

                # Gene Search Tab
                with gr.Tab("Gene Search"):
                    gr.Markdown("### Search for Genes by Symbol, Name, or Description")

                    with gr.Row():
                        search_input = gr.Textbox(
                            label="Search Term",
                            placeholder="Enter gene symbol, name, or description...",
                        )
                        search_limit = gr.Number(
                            label="Max Results", value=50, minimum=1, maximum=500
                        )
                        search_btn = gr.Button("Search Genes", variant="primary")

                    search_status = gr.Textbox(label="Search Status", interactive=False)
                    search_results = gr.DataFrame(label="Search Results")

                # Protein Analysis Tab
                with gr.Tab("Protein Analysis"):
                    gr.Markdown("### Analyze Protein Sequences")

                    protein_id_input = gr.Textbox(
                        label="Protein ID", placeholder="Enter protein stable ID..."
                    )
                    protein_analyze_btn = gr.Button(
                        "Analyze Protein", variant="primary"
                    )

                    protein_status = gr.Textbox(
                        label="Analysis Status", interactive=False
                    )

                    with gr.Row():
                        protein_composition_plot = gr.Plot(
                            label="Amino Acid Composition"
                        )
                        protein_hydrophobicity_plot = gr.Plot(
                            label="Hydrophobicity Profile"
                        )

                # DNA Analysis Tab
                with gr.Tab("DNA Analysis"):
                    gr.Markdown("### DNA Sequence Composition and GC Content Analysis")

                    dna_sequence_input = gr.TextArea(
                        label="DNA Sequence",
                        placeholder="Enter DNA sequence (A, T, G, C)",
                        lines=5,
                    )
                    dna_analyze_btn = gr.Button("Analyze DNA", variant="primary")

                    dna_status = gr.Textbox(label="Analysis Status", interactive=False)

                    with gr.Row():
                        dna_comp_plot = gr.Plot(label="Nucleotide Composition")
                        dna_gc_plot = gr.Plot(label="GC Content Window")

                    dna_helix_plot = gr.Plot(label="3D Double Helix Structure")

                # DNA Database Fetching Tab
                with gr.Tab("DNA Database"):
                    gr.Markdown("### Fetch DNA Sequences from Database")

                    with gr.Row():
                        check_dna_btn = gr.Button(
                            "Check DNA Availability", variant="primary"
                        )

                    dna_check_status = gr.Textbox(
                        label="Availability Check Status", interactive=False
                    )
                    dna_sources_info = gr.JSON(label="Available DNA Sources")

                    with gr.Row():
                        with gr.Column(scale=2):
                            sequence_source_dropdown = gr.Dropdown(
                                label="Select DNA Source", choices=[], interactive=True
                            )
                        with gr.Column(scale=1):
                            fetch_limit = gr.Number(
                                label="Max Sequences", value=20, minimum=1, maximum=100
                            )

                    with gr.Row():
                        fetch_sequences_btn = gr.Button(
                            "Fetch Sequences", variant="primary"
                        )
                        get_random_btn = gr.Button("Get Random Sequences")

                    fetch_status = gr.Textbox(label="Fetch Status", interactive=False)
                    sequences_table = gr.DataFrame(label="DNA Sequences")

                    gr.Markdown("#### Pattern Search")
                    with gr.Row():
                        pattern_input = gr.Textbox(
                            label="DNA Pattern",
                            placeholder="Enter DNA pattern (e.g., ATCG, GGCC)",
                            scale=2,
                        )
                        pattern_search_btn = gr.Button("Search Pattern")

                    pattern_status = gr.Textbox(
                        label="Pattern Search Status", interactive=False
                    )
                    pattern_results = gr.DataFrame(label="Pattern Search Results")

                    gr.Markdown("#### Quick Analysis")
                    with gr.Row():
                        analyze_from_db_btn = gr.Button(
                            "Analyze Random Sequence from DB"
                        )

                    db_analysis_status = gr.Textbox(
                        label="Database Analysis Status", interactive=False
                    )

                    with gr.Row():
                        db_comp_plot = gr.Plot(label="DB Sequence Composition")
                        db_gc_plot = gr.Plot(label="DB Sequence GC Content")

                    db_helix_plot = gr.Plot(label="DB Sequence 3D Helix")

            # Custom MySQL Functions Tab
            with gr.Tab("Custom MySQL Functions"):
                gr.Markdown(
                    """
                    ## Custom MySQL Functions

                    The biocat database includes three powerful custom MySQL functions for sequence analysis:

                    ### Available Functions:

                    1. **`classify_sequence(dna_sequence TEXT)`**
                       - Classifies DNA sequences based on the presence of start codons
                       - Returns 'Likely Gene' if ATG is found, 'Unknown' otherwise

                    2. **`count_nucleotides(dna_sequence TEXT)`**
                       - Counts frequency of each nucleotide (A, T, G, C)
                       - Returns results as JSON for easy parsing

                    3. **`detect_mutations(seq1 TEXT, seq2 TEXT)`**
                       - Compares two sequences base-by-base
                       - Returns detailed mutation positions and changes

                    ### ⚠️ Important: Database Connection Required

                    **Before using these features, you must:**
                    1. Connect to the database using the "Database Connection" tab
                    2. Ensure the custom functions are installed (see documentation)
                    3. Verify connection status shows "CONNECTED"

                    ### Interactive Testing

                    Use the sections below to test these functions with your own sequences or run predefined examples.
                    """
                )

                # Function Testing Section
                gr.Markdown("### Test Custom Functions")

                with gr.Row():
                    with gr.Column():
                        test_sequence1 = gr.TextArea(
                            label="DNA Sequence 1",
                            placeholder="Enter DNA sequence (e.g., ATGCGATCGTAGC)",
                            value="ATGCGATCGTAGC",
                            lines=3,
                        )
                    with gr.Column():
                        test_sequence2 = gr.TextArea(
                            label="DNA Sequence 2 (for mutation detection)",
                            placeholder="Enter second DNA sequence",
                            value="ATGCGATCCTAGC",
                            lines=3,
                        )

                with gr.Row():
                    test_classify_btn = gr.Button(
                        "Test classify_sequence()", variant="primary"
                    )
                    test_count_btn = gr.Button(
                        "Test count_nucleotides()", variant="primary"
                    )
                    test_mutations_btn = gr.Button(
                        "Test detect_mutations()", variant="primary"
                    )

                function_test_results = gr.TextArea(
                    label="Function Test Results", interactive=False, lines=8
                )

            # Information Tab
            with gr.Tab("Information"):
                gr.Markdown(
                    """
                    ## About This Interface

                    This Gradio-based interface provides comprehensive access to the Biocat biological database.

                    ### 🧬 **Custom MySQL Functions** - NEW FEATURE!

                    The biocat database includes three powerful custom MySQL functions for sequence analysis:

                    #### Available Functions:
                    - **`classify_sequence(dna_sequence)`** - Classify DNA sequences as 'Likely Gene' or 'Unknown' based on start codons
                    - **`count_nucleotides(dna_sequence)`** - Count A, T, G, C nucleotides and return detailed composition as JSON
                    - **`detect_mutations(seq1, seq2)`** - Compare two sequences base-by-base and identify mutation positions

                    #### How to Use:
                    1. **Interactive Testing**: Use the "Custom MySQL Functions" tab to test functions with your own sequences
                    2. **Query Integration**: Functions are available in "Sequence Analysis" and "Custom MySQL Functions" categories

                    ### Features:

                    #### Database Connection
                    - Test and configure database connections
                    - View connection status and details

                    #### Data Exploration
                    - Execute predefined queries organized by category
                    - Write and execute custom SQL queries using built-in functions
                    - View database statistics and overview

                    #### Gene Analysis
                    - Search genes by symbol, name, or description
                    - View detailed gene information

                    #### Protein Analysis
                    - Retrieve protein sequences by ID
                    - Analyze amino acid composition
                    - Generate hydrophobicity profiles

                    #### DNA Analysis
                    - Analyze nucleotide composition of DNA sequences
                    - Calculate GC content across sliding windows
                    - Visualize sequence properties with 3D double helix

                    #### DNA Database Access
                    - Check what DNA sequence data is available in the database
                    - Fetch DNA sequences directly from database tables
                    - Search for sequences containing specific patterns
                    - Analyze sequences fetched from the database

                    ### Usage Tips:
                    1. Start by testing your database connection
                    2. **🧬 Try the Custom MySQL Functions tab** - Test sequence analysis functions with your own data
                    3. Check DNA availability to see what sequences are stored
                    4. Use the predefined queries to explore common data patterns (look for "Custom MySQL Functions" category)
                    5. Fetch DNA sequences directly from the database for analysis
                    6. Search for specific DNA patterns across stored sequences
                    7. Use the search functionality to find specific genes
                    8. Analyze individual sequences using the protein and DNA analysis tools

                    ### Technical Details:
                    - Built with Gradio for interactive web interface
                    - Uses pandas for data manipulation
                    - Plotly for interactive visualizations
                    - BioPython for sequence analysis
                    - MySQL connector for database access
                    - Automatic detection of DNA sequence storage locations
                    """
                )

            # Event handlers
            if MODULES_AVAILABLE:
                # Initialize app (only for visualization module)
                if init_btn is not None:
                    init_btn.click(fn=initialize_app, outputs=init_status)

                # Test connection
                test_btn.click(
                    fn=test_connection,
                    inputs=[
                        host_input,
                        port_input,
                        user_input,
                        password_input,
                        database_input,
                    ],
                    outputs=[
                        gr.State(),
                        connection_status,
                        connection_info,
                        connection_indicator,
                    ],
                )

                # Database overview
                overview_btn.click(
                    fn=get_database_overview, outputs=[overview_status, overview_data]
                )

                # Predefined queries
                category_dropdown.change(
                    fn=update_query_dropdown,
                    inputs=[category_dropdown],
                    outputs=[query_dropdown],
                )

                query_dropdown.change(
                    fn=get_query_description,
                    inputs=[category_dropdown, query_dropdown],
                    outputs=[query_display],
                )

                execute_btn.click(
                    fn=execute_query,
                    inputs=[query_display, limit_input],
                    outputs=[query_status, query_results, query_viz],
                )

                # Custom queries
                custom_execute_btn.click(
                    fn=execute_custom_query,
                    inputs=[custom_query_input],
                    outputs=[custom_status, custom_results],
                )

                # Gene search
                search_btn.click(
                    fn=search_genes,
                    inputs=[search_input, search_limit],
                    outputs=[search_status, search_results],
                )

                # Protein analysis
                protein_analyze_btn.click(
                    fn=get_protein_sequence_analysis,
                    inputs=[protein_id_input],
                    outputs=[
                        protein_status,
                        protein_composition_plot,
                        protein_hydrophobicity_plot,
                    ],
                )

                # DNA analysis
                dna_analyze_btn.click(
                    fn=analyze_dna_sequence,
                    inputs=[dna_sequence_input],
                    outputs=[dna_comp_plot, dna_gc_plot, dna_helix_plot, dna_status],
                )

                # DNA Database functions
                def update_sequence_sources(availability_info):
                    """Update sequence source dropdown based on availability check"""
                    if availability_info and "available_sequences" in availability_info:
                        sources = list(availability_info["available_sequences"].keys())
                        return gr.Dropdown(
                            choices=sources, value=sources[0] if sources else None
                        )
                    return gr.Dropdown(choices=[], value=None)

                def analyze_random_from_db(source_info):
                    """Get a random sequence from database and analyze it"""
                    if not source_info:
                        return (
                            "ERROR: Please select a DNA source first",
                            None,
                            None,
                            None,
                        )

                    # Get a random sequence
                    status, sequences = get_random_sequences_for_analysis(
                        source_info, count=1
                    )

                    if not sequences:
                        return status, None, None, None

                    # Analyze the first sequence
                    sequence = sequences[0]
                    comp_fig, gc_fig, helix_fig, analysis_status = analyze_dna_sequence(
                        sequence
                    )

                    combined_status = f"{status}\nAnalysis: {analysis_status}"
                    return combined_status, comp_fig, gc_fig, helix_fig

                # DNA database event handlers
                check_dna_btn.click(
                    fn=check_dna_availability,
                    outputs=[dna_check_status, dna_sources_info],
                ).then(
                    fn=update_sequence_sources,
                    inputs=[dna_sources_info],
                    outputs=[sequence_source_dropdown],
                )

                fetch_sequences_btn.click(
                    fn=fetch_dna_sequences,
                    inputs=[sequence_source_dropdown, fetch_limit],
                    outputs=[fetch_status, sequences_table],
                )

                get_random_btn.click(
                    fn=lambda source: get_random_sequences_for_analysis(
                        source, count=5
                    ),
                    inputs=[sequence_source_dropdown],
                    outputs=[fetch_status, gr.State()],
                )

                pattern_search_btn.click(
                    fn=search_sequences_by_pattern,
                    inputs=[pattern_input, sequence_source_dropdown],
                    outputs=[pattern_status, pattern_results],
                )

                analyze_from_db_btn.click(
                    fn=analyze_random_from_db,
                    inputs=[sequence_source_dropdown],
                    outputs=[
                        db_analysis_status,
                        db_comp_plot,
                        db_gc_plot,
                        db_helix_plot,
                    ],
                )

                # Custom MySQL Functions event handlers
                test_classify_btn.click(
                    fn=lambda seq1, seq2: test_custom_function(
                        "classify_sequence", seq1, seq2
                    ),
                    inputs=[test_sequence1, test_sequence2],
                    outputs=[function_test_results],
                )

                test_count_btn.click(
                    fn=lambda seq1, seq2: test_custom_function(
                        "count_nucleotides", seq1, seq2
                    ),
                    inputs=[test_sequence1, test_sequence2],
                    outputs=[function_test_results],
                )

                test_mutations_btn.click(
                    fn=lambda seq1, seq2: test_custom_function(
                        "detect_mutations", seq1, seq2
                    ),
                    inputs=[test_sequence1, test_sequence2],
                    outputs=[function_test_results],
                )

    return interface


if __name__ == "__main__":
    # Create and launch the interface
    interface = create_interface()

    # Launch with appropriate settings
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True,
    )
