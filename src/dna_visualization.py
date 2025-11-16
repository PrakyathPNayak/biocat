"""
DNA Visualization Module for Biocat Interface
Provides visualization functions for DNA sequences, protein sequences, and genomic data
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import re
from collections import Counter

# Removed unused imports: GC and molecular_weight are not used in this code
from Bio.SeqUtils.ProtParam import ProteinAnalysis

import warnings

warnings.filterwarnings("ignore")

# Set style for matplotlib
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")


class DNAVisualizer:
    """Class for visualizing DNA and protein sequences"""

    def __init__(self):
        self.colors = {
            "A": "#FF6B6B",  # Red
            "T": "#4ECDC4",  # Teal
            "G": "#45B7D1",  # Blue
            "C": "#FFA726",  # Orange
            "U": "#9C27B0",  # Purple (for RNA)
            "N": "#757575",  # Gray (for unknown)
        }
        self.amino_acid_colors = {
            "A": "#FF9999",
            "R": "#FF6666",
            "N": "#FF3333",
            "D": "#FF0000",
            "C": "#FFCC99",
            "Q": "#FF9966",
            "E": "#FF6633",
            "G": "#FF3300",
            "H": "#99FF99",
            "I": "#66FF66",
            "L": "#33FF33",
            "K": "#00FF00",
            "M": "#99FFFF",
            "F": "#66FFFF",
            "P": "#33FFFF",
            "S": "#00FFFF",
            "T": "#9999FF",
            "W": "#6666FF",
            "Y": "#3333FF",
            "V": "#0000FF",
            "*": "#000000",  # Stop codon
        }

    def analyze_nucleotide_composition(self, sequence: str) -> Dict[str, float]:
        """
        Analyze nucleotide composition of a DNA sequence

        Args:
            sequence: DNA sequence string

        Returns:
            Dictionary with nucleotide frequencies
        """
        if not sequence:
            return {}

        sequence = sequence.upper().replace(" ", "")
        total_length = len(sequence)

        composition = {}
        for nucleotide in ["A", "T", "G", "C", "N"]:
            count = sequence.count(nucleotide)
            composition[nucleotide] = (
                (count / total_length) * 100 if total_length > 0 else 0
            )

        # Calculate GC content
        gc_count = sequence.count("G") + sequence.count("C")
        composition["GC_content"] = (
            (gc_count / total_length) * 100 if total_length > 0 else 0
        )

        return composition

    def plot_nucleotide_composition(
        self, sequence: str, title: str = "Nucleotide Composition"
    ) -> go.Figure:
        """
        Create a pie chart showing nucleotide composition

        Args:
            sequence: DNA sequence string
            title: Plot title

        Returns:
            Plotly figure object
        """
        composition = self.analyze_nucleotide_composition(sequence)

        # Filter out zero values and N
        filtered_comp = {
            k: v
            for k, v in composition.items()
            if v > 0 and k not in ["GC_content", "N"]
        }

        if not filtered_comp:
            # Create empty figure if no valid data
            fig = go.Figure()
            fig.add_annotation(
                text="No valid nucleotide data",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        nucleotides = list(filtered_comp.keys())
        percentages = list(filtered_comp.values())
        colors = [self.colors.get(n, "#757575") for n in nucleotides]

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=nucleotides,
                    values=percentages,
                    hole=0.4,
                    marker_colors=colors,
                    textinfo="label+percent",
                    textfont_size=12,
                )
            ]
        )

        fig.update_layout(
            title=f"{title}<br><sub>GC Content: {composition.get('GC_content', 0):.1f}%</sub>",
            font=dict(size=14),
            showlegend=True,
            width=500,
            height=400,
        )

        return fig

    def plot_sequence_logo(
        self, sequences: List[str], title: str = "Sequence Logo"
    ) -> go.Figure:
        """
        Create a sequence logo visualization for multiple aligned sequences

        Args:
            sequences: List of aligned DNA sequences
            title: Plot title

        Returns:
            Plotly figure object
        """
        if not sequences or not sequences[0]:
            fig = go.Figure()
            fig.add_annotation(
                text="No sequence data available",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        # Calculate position weight matrix
        seq_length = len(sequences[0])
        position_counts = []

        for pos in range(seq_length):
            pos_nucleotides = [seq[pos].upper() for seq in sequences if pos < len(seq)]
            counter = Counter(pos_nucleotides)
            position_counts.append(counter)

        # Create heatmap data
        nucleotides = ["A", "T", "G", "C"]
        heatmap_data = []

        for nucleotide in nucleotides:
            row = []
            for pos_count in position_counts:
                total = sum(pos_count.values())
                freq = pos_count.get(nucleotide, 0) / total if total > 0 else 0
                row.append(freq)
            heatmap_data.append(row)

        fig = go.Figure(
            data=go.Heatmap(
                z=heatmap_data,
                x=list(range(1, seq_length + 1)),
                y=nucleotides,
                colorscale="RdYlBu_r",
                showscale=True,
                colorbar=dict(title="Frequency"),
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="Position",
            yaxis_title="Nucleotide",
            font=dict(size=12),
            width=800,
            height=300,
        )

        return fig

    def plot_gc_content_window(
        self, sequence: str, window_size: int = 100, title: str = "GC Content"
    ) -> go.Figure:
        """
        Plot GC content across a sequence using a sliding window

        Args:
            sequence: DNA sequence string
            window_size: Size of sliding window
            title: Plot title

        Returns:
            Plotly figure object
        """
        if not sequence or len(sequence) < window_size:
            fig = go.Figure()
            fig.add_annotation(
                text="Sequence too short for analysis",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        sequence = sequence.upper().replace(" ", "")
        positions = []
        gc_contents = []

        for i in range(0, len(sequence) - window_size + 1, window_size // 4):
            window = sequence[i : i + window_size]
            gc_count = window.count("G") + window.count("C")
            gc_content = (gc_count / len(window)) * 100

            positions.append(i + window_size // 2)
            gc_contents.append(gc_content)

        fig = go.Figure(
            data=go.Scatter(
                x=positions,
                y=gc_contents,
                mode="lines+markers",
                line=dict(color="#2E86AB", width=2),
                marker=dict(size=4, color="#F24236"),
                name="GC Content",
            )
        )

        # Add average line
        avg_gc = np.mean(gc_contents)
        fig.add_hline(
            y=avg_gc,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Average: {avg_gc:.1f}%",
        )

        fig.update_layout(
            title=f"{title} (Window size: {window_size}bp)",
            xaxis_title="Position (bp)",
            yaxis_title="GC Content (%)",
            font=dict(size=12),
            width=800,
            height=400,
            showlegend=True,
        )

        return fig

    def analyze_protein_properties(self, sequence: str) -> Dict[str, Any]:
        """
        Analyze protein sequence properties

        Args:
            sequence: Protein sequence string

        Returns:
            Dictionary with protein properties
        """
        if not sequence:
            return {}

        # Clean sequence
        sequence = re.sub(r"[^ACDEFGHIKLMNPQRSTVWY*]", "", sequence.upper())

        if not sequence:
            return {}

        try:
            protein_analysis = ProteinAnalysis(sequence.replace("*", ""))

            properties = {
                "length": len(sequence),
                "molecular_weight": protein_analysis.molecular_weight(),
                "isoelectric_point": protein_analysis.isoelectric_point(),
                "instability_index": protein_analysis.instability_index(),
                "flexibility": np.mean(protein_analysis.flexibility())
                if protein_analysis.flexibility()
                else 0,
            }

            # Calculate hydrophobicity manually to avoid BioPython issue
            if len(sequence) >= 9:
                try:
                    hydro_values = []
                    kyte_doolittle = {
                        "A": 1.8,
                        "R": -4.5,
                        "N": -3.5,
                        "D": -3.5,
                        "C": 2.5,
                        "Q": -3.5,
                        "E": -3.5,
                        "G": -0.4,
                        "H": -3.2,
                        "I": 4.5,
                        "L": 3.8,
                        "K": -3.9,
                        "M": 1.9,
                        "F": 2.8,
                        "P": -1.6,
                        "S": -0.8,
                        "T": -0.7,
                        "W": -0.9,
                        "Y": -1.3,
                        "V": 4.2,
                    }
                    window = 9
                    for i in range(len(sequence) - window + 1):
                        window_seq = sequence[i : i + window]
                        hydro_sum = sum(kyte_doolittle.get(aa, 0) for aa in window_seq)
                        hydro_values.append(hydro_sum / window)
                    properties["hydrophobicity"] = (
                        np.mean(hydro_values) if hydro_values else 0
                    )
                except Exception:
                    properties["hydrophobicity"] = 0
            else:
                properties["hydrophobicity"] = 0

            # Amino acid composition
            aa_percent = protein_analysis.get_amino_acids_percent()
            properties.update(
                {f"aa_{aa}": percent * 100 for aa, percent in aa_percent.items()}
            )

            return properties

        except Exception as e:
            return {"length": len(sequence), "error": str(e)}

    def plot_amino_acid_composition(
        self, sequence: str, title: str = "Amino Acid Composition"
    ) -> go.Figure:
        """
        Create a bar plot showing amino acid composition

        Args:
            sequence: Protein sequence string
            title: Plot title

        Returns:
            Plotly figure object
        """
        properties = self.analyze_protein_properties(sequence)

        # Check if there was an error in analysis
        if "error" in properties:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Analysis error: {properties['error']}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        # Extract amino acid percentages
        aa_data = {
            k.replace("aa_", ""): v
            for k, v in properties.items()
            if k.startswith("aa_")
        }

        if not aa_data:
            # Try direct amino acid counting if BioPython analysis failed
            from collections import Counter

            clean_seq = re.sub(r"[^ACDEFGHIKLMNPQRSTVWY]", "", sequence.upper())
            if clean_seq:
                aa_counts = Counter(clean_seq)
                total = len(clean_seq)
                aa_data = {aa: (count / total) * 100 for aa, count in aa_counts.items()}

            if not aa_data:
                fig = go.Figure()
                fig.add_annotation(
                    text="No valid amino acid data found",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                )
                return fig

        amino_acids = list(aa_data.keys())
        percentages = list(aa_data.values())
        colors = [self.amino_acid_colors.get(aa, "#757575") for aa in amino_acids]

        fig = go.Figure(
            data=[
                go.Bar(
                    x=amino_acids,
                    y=percentages,
                    marker_color=colors,
                    text=[f"{p:.1f}%" for p in percentages],
                    textposition="auto",
                )
            ]
        )

        fig.update_layout(
            title=title,
            xaxis_title="Amino Acid",
            yaxis_title="Percentage (%)",
            font=dict(size=12),
            width=800,
            height=400,
        )

        return fig

    def plot_hydrophobicity_profile(
        self, sequence: str, window_size: int = 9, title: str = "Hydrophobicity Profile"
    ) -> go.Figure:
        """
        Plot hydrophobicity profile along protein sequence

        Args:
            sequence: Protein sequence string
            window_size: Window size for calculation
            title: Plot title

        Returns:
            Plotly figure object
        """
        if not sequence or len(sequence) < window_size:
            fig = go.Figure()
            fig.add_annotation(
                text="Sequence too short for analysis",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        # Clean sequence
        sequence = re.sub(r"[^ACDEFGHIKLMNPQRSTVWY]", "", sequence.upper())

        if len(sequence) < window_size:
            fig = go.Figure()
            fig.add_annotation(
                text="Cleaned sequence too short",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        try:
            # Calculate hydrophobicity manually to avoid BioPython issue
            kyte_doolittle = {
                "A": 1.8,
                "R": -4.5,
                "N": -3.5,
                "D": -3.5,
                "C": 2.5,
                "Q": -3.5,
                "E": -3.5,
                "G": -0.4,
                "H": -3.2,
                "I": 4.5,
                "L": 3.8,
                "K": -3.9,
                "M": 1.9,
                "F": 2.8,
                "P": -1.6,
                "S": -0.8,
                "T": -0.7,
                "W": -0.9,
                "Y": -1.3,
                "V": 4.2,
            }

            hydrophobicity = []
            positions = []

            for i in range(len(sequence) - window_size + 1):
                window_seq = sequence[i : i + window_size]
                hydro_sum = sum(kyte_doolittle.get(aa, 0) for aa in window_seq)
                hydrophobicity.append(hydro_sum / window_size)
                positions.append(i + window_size // 2 + 1)

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=positions,
                    y=hydrophobicity,
                    mode="lines",
                    line=dict(color="#FF6B6B", width=2),
                    fill="tozeroy",
                    name="Hydrophobicity",
                )
            )

            # Add zero line
            fig.add_hline(
                y=0, line_dash="dash", line_color="black", annotation_text="Neutral"
            )

            fig.update_layout(
                title=title,
                xaxis_title="Position",
                yaxis_title="Hydrophobicity Index",
                font=dict(size=12),
                width=800,
                height=400,
            )

            return fig

        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error calculating hydrophobicity: {str(e)}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

    def create_sequence_comparison_plot(
        self, sequences: Dict[str, str], title: str = "Sequence Comparison"
    ) -> go.Figure:
        """
        Create a visual comparison of multiple sequences

        Args:
            sequences: Dictionary with sequence names as keys and sequences as values
            title: Plot title

        Returns:
            Plotly figure object
        """
        if not sequences:
            fig = go.Figure()
            fig.add_annotation(
                text="No sequences to compare",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        # Create subplots for each sequence
        seq_names = list(sequences.keys())
        n_sequences = len(seq_names)

        fig = make_subplots(
            rows=n_sequences, cols=1, subplot_titles=seq_names, vertical_spacing=0.1
        )

        for i, (name, sequence) in enumerate(sequences.items(), 1):
            if sequence:
                composition = self.analyze_nucleotide_composition(sequence)
                nucleotides = ["A", "T", "G", "C"]
                values = [composition.get(n, 0) for n in nucleotides]
                colors = [self.colors[n] for n in nucleotides]

                fig.add_trace(
                    go.Bar(
                        x=nucleotides,
                        y=values,
                        marker_color=colors,
                        name=name,
                        showlegend=i == 1,
                    ),
                    row=i,
                    col=1,
                )

        fig.update_layout(title=title, height=200 * n_sequences, font=dict(size=10))

        return fig

    def plot_gene_structure(
        self, gene_data: Dict, title: str = "Gene Structure"
    ) -> go.Figure:
        """
        Visualize gene structure with exons, introns, and features

        Args:
            gene_data: Dictionary containing gene information
            title: Plot title

        Returns:
            Plotly figure object
        """
        fig = go.Figure()

        if not gene_data:
            fig.add_annotation(
                text="No gene data available",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        # Basic gene structure
        start = gene_data.get("start_position", 0)
        end = gene_data.get("end_position", 1000)

        # Gene body
        fig.add_shape(
            type="rect",
            x0=start,
            y0=0.4,
            x1=end,
            y1=0.6,
            fillcolor="lightblue",
            line=dict(color="blue", width=2),
        )

        # Add gene information
        fig.add_annotation(
            x=(start + end) / 2,
            y=0.7,
            text=f"Gene: {gene_data.get('gene_symbol', 'Unknown')}<br>"
            f"Length: {end - start:,} bp<br>"
            f"Type: {gene_data.get('gene_biotype', 'Unknown')}",
            showarrow=False,
            font=dict(size=12),
        )

        fig.update_layout(
            title=title,
            xaxis_title="Genomic Position (bp)",
            yaxis=dict(visible=False),
            showlegend=False,
            height=200,
            width=800,
        )

        return fig

    def plot_dna_double_helix(
        self,
        sequence: str,
        title: str = "DNA Double Helix Visualization",
        max_length: int = 50,
    ) -> go.Figure:
        """
        Create a 3D double helix visualization of DNA sequence

        Args:
            sequence: DNA sequence string
            title: Plot title
            max_length: Maximum sequence length to visualize

        Returns:
            Plotly figure object
        """
        if not sequence:
            fig = go.Figure()
            fig.add_annotation(
                text="No sequence provided",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        # Clean and limit sequence
        sequence = sequence.upper().replace(" ", "").replace("\n", "")
        sequence = re.sub(r"[^ATGC]", "", sequence)

        if len(sequence) > max_length:
            sequence = sequence[:max_length]

        if not sequence:
            fig = go.Figure()
            fig.add_annotation(
                text="No valid DNA bases found",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        # Generate helix coordinates
        n_bases = len(sequence)
        t = np.linspace(0, 4 * np.pi * n_bases / 10, n_bases)

        # Strand 1 (forward)
        x1 = np.cos(t)
        y1 = np.sin(t)
        z1 = np.linspace(0, n_bases * 0.34, n_bases)  # 0.34 nm per base pair

        # Strand 2 (reverse complement)
        x2 = -np.cos(t)
        y2 = -np.sin(t)
        z2 = z1

        # Base colors
        base_colors = {"A": "#FF6B6B", "T": "#4ECDC4", "G": "#45B7D1", "C": "#FFA726"}
        complement = {"A": "T", "T": "A", "G": "C", "C": "G"}

        fig = go.Figure()

        # Add backbone traces
        fig.add_trace(
            go.Scatter3d(
                x=x1,
                y=y1,
                z=z1,
                mode="lines+markers",
                line=dict(color="gray", width=4),
                marker=dict(size=3, color="gray"),
                name="Strand 1 Backbone",
                showlegend=True,
            )
        )

        fig.add_trace(
            go.Scatter3d(
                x=x2,
                y=y2,
                z=z2,
                mode="lines+markers",
                line=dict(color="gray", width=4),
                marker=dict(size=3, color="gray"),
                name="Strand 2 Backbone",
                showlegend=True,
            )
        )

        # Add base pairs and connections
        for i, base in enumerate(sequence):
            comp_base = complement[base]
            color = base_colors[base]
            comp_color = base_colors[comp_base]

            # Base markers
            fig.add_trace(
                go.Scatter3d(
                    x=[x1[i]],
                    y=[y1[i]],
                    z=[z1[i]],
                    mode="markers+text",
                    marker=dict(size=8, color=color),
                    text=base,
                    textposition="middle center",
                    name=f"Base {base}",
                    showlegend=False,
                )
            )

            fig.add_trace(
                go.Scatter3d(
                    x=[x2[i]],
                    y=[y2[i]],
                    z=[z2[i]],
                    mode="markers+text",
                    marker=dict(size=8, color=comp_color),
                    text=comp_base,
                    textposition="middle center",
                    name=f"Base {comp_base}",
                    showlegend=False,
                )
            )

            # Hydrogen bonds between base pairs
            fig.add_trace(
                go.Scatter3d(
                    x=[x1[i], x2[i]],
                    y=[y1[i], y2[i]],
                    z=[z1[i], z2[i]],
                    mode="lines",
                    line=dict(color="lightblue", width=2, dash="dash"),
                    name="H-bonds",
                    showlegend=False,
                )
            )

        fig.update_layout(
            title=f"{title}<br><sub>Sequence: {sequence[:20]}{'...' if len(sequence) > 20 else ''}</sub>",
            scene=dict(
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="Z (Length)",
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
            ),
            width=800,
            height=600,
            showlegend=True,
        )

        return fig


def create_genomic_overview_plot(df: pd.DataFrame) -> go.Figure:
    """
    Create an overview plot of genomic data distribution

    Args:
        df: DataFrame with genomic data

    Returns:
        Plotly figure object
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Create subplot based on available columns
    if "species_name" in df.columns:
        species_counts = df["species_name"].value_counts()

        fig = go.Figure(
            data=[
                go.Bar(
                    x=species_counts.index,
                    y=species_counts.values,
                    marker_color="lightblue",
                )
            ]
        )

        fig.update_layout(
            title="Data Distribution by Species",
            xaxis_title="Species",
            yaxis_title="Count",
            font=dict(size=12),
        )
    else:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for visualization",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )

    return fig


def create_protein_length_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Create histogram of protein length distribution

    Args:
        df: DataFrame with protein data

    Returns:
        Plotly figure object
    """
    if df.empty or "protein_length" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No protein length data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    lengths = df["protein_length"].dropna()

    if lengths.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No valid protein length data",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    fig = go.Figure(
        data=[
            go.Histogram(x=lengths, nbinsx=30, marker_color="lightgreen", opacity=0.7)
        ]
    )

    fig.update_layout(
        title="Protein Length Distribution",
        xaxis_title="Protein Length (amino acids)",
        yaxis_title="Frequency",
        font=dict(size=12),
    )

    return fig


def create_chromosome_gene_density_plot(df: pd.DataFrame) -> go.Figure:
    """
    Create a plot showing gene density across chromosomes

    Args:
        df: DataFrame with chromosome and gene data

    Returns:
        Plotly figure object
    """
    if df.empty or "chromosome_name" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No chromosome data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    chr_counts = df["chromosome_name"].value_counts().sort_index()

    fig = go.Figure(
        data=[go.Bar(x=chr_counts.index, y=chr_counts.values, marker_color="coral")]
    )

    fig.update_layout(
        title="Gene Distribution Across Chromosomes",
        xaxis_title="Chromosome",
        yaxis_title="Number of Genes",
        font=dict(size=12),
        xaxis={"categoryorder": "category ascending"},
    )

    return fig
