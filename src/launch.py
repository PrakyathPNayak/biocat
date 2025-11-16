#!/usr/bin/env python3
"""
Simple launcher for the Biocat Database Interface
"""

import sys
import os
from pathlib import Path


def main():
    """Launch the Biocat Database Interface"""
    print("Starting Biocat Database Interface...")

    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

    try:
        from app import create_interface

        print("Launching web interface...")
        print("Opening in your default web browser at: http://localhost:7860")
        print("Press Ctrl+C to stop the server")

        app = create_interface()
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            inbrowser=True,
            quiet=False,
        )

    except ImportError as e:
        print(f"Error: Failed to import application: {e}")
        print("Please ensure all required files are present:")
        print("- app.py, database.py, sql_queries.py, dna_visualization.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
