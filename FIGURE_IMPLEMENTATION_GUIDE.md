# 📊 Figure 1: ARQA System Architecture Overview - Implementation Guide

## ✅ Files Generated

1. **`arqa_architecture.png`** (447KB) - High-resolution PNG for LaTeX inclusion
2. **`arqa_architecture.pdf`** (48KB) - Vector PDF version for best quality
3. **`arqa_architecture_ascii.txt`** - Text version for reference

## 📝 LaTeX Implementation

### Option 1: Using PNG (Recommended for submission)
```latex
\begin{figure}[htbp]
\centerline{\includegraphics[width=0.45\textwidth]{arqa_architecture.png}}
\caption{ARQA System Architecture Overview}
\label{fig:architecture}
\end{figure}
```

### Option 2: Using PDF (Best quality)
```latex
\begin{figure}[htbp]
\centerline{\includegraphics[width=0.45\textwidth]{arqa_architecture.pdf}}
\caption{ARQA System Architecture Overview}
\label{fig:architecture}
\end{figure}
```

## 🔧 Your Current LaTeX Code

The figure is already properly referenced in your paper at line ~89:

```latex
\section{System Architecture}
ARQA implements a four-stage pipeline (Figure \ref{fig:architecture}) designed for scalability and modularity:

\begin{figure}[htbp]
\centerline{\includegraphics[width=0.45\textwidth]{arqa_architecture.png}}
\caption{ARQA System Architecture Overview}
\label{fig:architecture}
\end{figure}
```

## 📊 Architecture Components Shown

The generated diagram includes:

### 🔹 **Input Layer**
- HTML Documents (Arabic Web Content)  
- User Questions (Arabic Text)

### 🔹 **Document Processing Pipeline**
- HTML Parser (BeautifulSoup)
- Text Preservation (No Normalization) ← **Your Key Innovation**
- Chunking (200 tokens, 50 overlap)

### 🔹 **Semantic Indexing**
- AraDPR Encoder (768-dim embeddings)
- FAISS Vector Index (Incremental)

### 🔹 **Query Processing**
- Question Normalization (Light)
- AraDPR Query Encoding  
- Top-K Similarity Search

### 🔹 **Answer Extraction**
- Multi-Model QA System:
  - Arabic BERT (Primary)
  - AraELECTRA (Fallback)
  - XLM-RoBERTa (Multilingual)
- Non-normalized Context + Span Prediction ← **Your Key Innovation**

### 🔹 **FastAPI REST Interface**
- Background Processing & Status Monitoring
- Real-time Interaction & Error Handling

### 🔹 **Output**
- Ranked Answers with Confidence Scores
- Original Arabic Character Preservation ← **Your Key Innovation**

## 🎯 Key Features Highlighted

The diagram emphasizes your unique contributions:
- ✅ **Text Authenticity Preservation**
- ✅ **Incremental Indexing** 
- ✅ **Multi-model Fallback**
- ✅ **Sub-130ms Response Time**

## 📁 File Placement

Place the image file in the same directory as your LaTeX document:
```
C:\Users\a-ahm\Desktop\arqa\
├── ARQA_Paper.tex
├── arqa_architecture.png  ← Use this file
├── arqa_architecture.pdf  ← Or this for better quality
└── ... other files
```

## 🚀 Ready for Compilation

Your LaTeX paper is now ready with the architecture diagram! The figure properly illustrates your system's modular design and highlights the key innovations in Arabic text preservation.

**Compilation command:**
```bash
pdflatex ARQA_Paper.tex
```

The diagram will be automatically included and referenced as Figure 1 in your paper.
