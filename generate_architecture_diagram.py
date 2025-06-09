#!/usr/bin/env python3
"""
Generate ARQA System Architecture Diagram for Paper
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_arqa_architecture_diagram():
    """Create a professional architecture diagram for ARQA system."""
    
    # Create figure with larger size for better quality
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Color scheme
    colors = {
        'input': '#E8F4FD',
        'processing': '#D4E6F1', 
        'indexing': '#A9DFBF',
        'query': '#F9E79F',
        'extraction': '#F1C40F',
        'api': '#E8DAEF',
        'output': '#FADBD8',
        'arrow': '#2C3E50',
        'text': '#2C3E50'
    }
    
    # Box style
    box_style = "round,pad=0.1"
    
    # Title
    ax.text(5, 11.5, 'ARQA System Architecture Overview', 
            fontsize=16, fontweight='bold', ha='center', color=colors['text'])
    
    # Input Layer
    input_box1 = FancyBboxPatch((0.5, 10), 2, 0.8, boxstyle=box_style, 
                               facecolor=colors['input'], edgecolor='black', linewidth=1)
    ax.add_patch(input_box1)
    ax.text(1.5, 10.4, 'HTML Documents\n(Arabic Content)', 
            ha='center', va='center', fontsize=10, fontweight='bold')
    
    input_box2 = FancyBboxPatch((7.5, 10), 2, 0.8, boxstyle=box_style,
                               facecolor=colors['input'], edgecolor='black', linewidth=1)
    ax.add_patch(input_box2)
    ax.text(8.5, 10.4, 'User Questions\n(Arabic Text)', 
            ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Document Processing
    proc_box = FancyBboxPatch((0.5, 8.5), 4, 1.2, boxstyle=box_style,
                             facecolor=colors['processing'], edgecolor='black', linewidth=1)
    ax.add_patch(proc_box)
    ax.text(2.5, 9.1, 'Document Processing Pipeline', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(2.5, 8.8, '• HTML Parser (BeautifulSoup)', ha='center', va='center', fontsize=9)
    ax.text(2.5, 8.6, '• Text Preservation (No Normalization)', ha='center', va='center', fontsize=9)
    ax.text(2.5, 8.4, '• Chunking (200 tokens, 50 overlap)', ha='center', va='center', fontsize=9)
    
    # Semantic Indexing
    index_box = FancyBboxPatch((0.5, 6.8), 4, 1.2, boxstyle=box_style,
                              facecolor=colors['indexing'], edgecolor='black', linewidth=1)
    ax.add_patch(index_box)
    ax.text(2.5, 7.4, 'Semantic Indexing', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(2.5, 7.1, '• AraDPR Encoder (768-dim)', ha='center', va='center', fontsize=9)
    ax.text(2.5, 6.9, '• FAISS Vector Index (Incremental)', ha='center', va='center', fontsize=9)
    
    # Query Processing
    query_box = FancyBboxPatch((5.5, 8.5), 4, 1.2, boxstyle=box_style,
                              facecolor=colors['query'], edgecolor='black', linewidth=1)
    ax.add_patch(query_box)
    ax.text(7.5, 9.1, 'Query Processing', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(7.5, 8.8, '• Question Normalization (Light)', ha='center', va='center', fontsize=9)
    ax.text(7.5, 8.6, '• AraDPR Query Encoding', ha='center', va='center', fontsize=9)
    ax.text(7.5, 8.4, '• Top-K Similarity Search', ha='center', va='center', fontsize=9)
    
    # Answer Extraction
    extract_box = FancyBboxPatch((2.5, 4.5), 5, 1.8, boxstyle=box_style,
                                facecolor=colors['extraction'], edgecolor='black', linewidth=1)
    ax.add_patch(extract_box)
    ax.text(5, 5.7, 'Answer Extraction', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(5, 5.4, '• Multi-Model QA System:', ha='center', va='center', fontsize=9, fontweight='bold')
    ax.text(5, 5.2, '  - Arabic BERT (Primary)', ha='center', va='center', fontsize=9)
    ax.text(5, 5.0, '  - AraELECTRA (Fallback)', ha='center', va='center', fontsize=9)
    ax.text(5, 4.8, '  - XLM-RoBERTa (Multilingual)', ha='center', va='center', fontsize=9)
    ax.text(5, 4.6, '• Non-normalized Context + Span Prediction', ha='center', va='center', fontsize=9)
    
    # API Layer
    api_box = FancyBboxPatch((2.5, 2.8), 5, 1.2, boxstyle=box_style,
                            facecolor=colors['api'], edgecolor='black', linewidth=1)
    ax.add_patch(api_box)
    ax.text(5, 3.4, 'FastAPI REST Interface', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(5, 3.1, '• Background Processing & Status Monitoring', ha='center', va='center', fontsize=9)
    ax.text(5, 2.9, '• Real-time Interaction & Error Handling', ha='center', va='center', fontsize=9)
    
    # Output
    output_box = FancyBboxPatch((2.5, 1), 5, 1.2, boxstyle=box_style,
                               facecolor=colors['output'], edgecolor='black', linewidth=1)
    ax.add_patch(output_box)
    ax.text(5, 1.6, 'Output', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(5, 1.3, '• Ranked Answers with Confidence Scores', ha='center', va='center', fontsize=9)
    ax.text(5, 1.1, '• Original Arabic Character Preservation', ha='center', va='center', fontsize=9)
    
    # Arrows - Data Flow
    arrows = [
        # HTML to Processing
        ((1.5, 10), (2.5, 9.7)),
        # Processing to Indexing  
        ((2.5, 8.5), (2.5, 8.0)),
        # Questions to Query Processing
        ((8.5, 10), (7.5, 9.7)),
        # Query Processing to Answer Extraction
        ((7.5, 8.5), (6, 6.3)),
        # Indexing to Answer Extraction  
        ((2.5, 6.8), (4, 6.3)),
        # Answer Extraction to API
        ((5, 4.5), (5, 4.0)),
        # API to Output
        ((5, 2.8), (5, 2.2))
    ]
    
    for start, end in arrows:
        arrow = ConnectionPatch(start, end, "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5,
                              mutation_scale=20, fc=colors['arrow'], 
                              edgecolor=colors['arrow'], linewidth=2)
        ax.add_patch(arrow)
    
    # Key Features Box
    features_box = FancyBboxPatch((0.2, 0.2), 9.6, 0.6, boxstyle=box_style,
                                 facecolor='white', edgecolor='black', linewidth=1)
    ax.add_patch(features_box)
    ax.text(5, 0.5, 'Key Features: Text Authenticity Preservation • Incremental Indexing • Multi-model Fallback • Sub-130ms Response Time',
            ha='center', va='center', fontsize=10, fontweight='bold', style='italic')
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # Set matplotlib to non-interactive backend
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    
    # Generate the diagram
    fig = create_arqa_architecture_diagram()
    
    # Save as high-quality PNG for paper
    fig.savefig('arqa_architecture.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    # Also save as PDF for vector graphics
    fig.savefig('arqa_architecture.pdf', bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print("✅ Architecture diagram saved as:")
    print("   📄 arqa_architecture.png (for LaTeX)")
    print("   📄 arqa_architecture.pdf (vector version)")
    
    # Don't show the diagram in headless mode
    # plt.show()
