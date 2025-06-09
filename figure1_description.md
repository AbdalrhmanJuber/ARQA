# ARQA System Architecture - Figure 1 Description

## Components to Include in the Architecture Diagram:

### 1. **Input Layer**
- HTML Documents (various sources)
- User Questions (Arabic text)

### 2. **Document Processing Pipeline**
- HTML Parser (BeautifulSoup)
- Text Extraction & Cleaning
- Original Text Preservation (No Normalization)
- Chunking (200 tokens with 50 overlap)

### 3. **Semantic Indexing**
- AraDPR Encoder (768-dim embeddings)
- FAISS Vector Index
- Incremental Indexing Support
- Document Metadata Storage

### 4. **Query Processing**
- Question Normalization (light)
- AraDPR Query Encoding
- Similarity Search (FAISS)
- Top-K Retrieval

### 5. **Answer Extraction**
- Multi-Model QA System:
  - zohaib99k/Bert_Arabic-SQuADv2-QA (Primary)
  - ZeyadAhmed/AraElectra-Arabic-SQuADv2-QA (Fallback)
  - deepset/xlm-roberta-base-squad2 (Multilingual)
- Non-normalized Context Processing
- Span Prediction & Confidence Scoring

### 6. **API Layer**
- FastAPI REST Interface
- Background Processing
- Real-time Status Monitoring

### 7. **Output**
- Ranked Answers with Confidence
- Original Arabic Character Preservation
- Document Context & Metadata

## Data Flow:
1. HTML → Document Processing → Chunking
2. Chunks → AraDPR → FAISS Index
3. Question → Query Processing → Retrieval
4. Retrieved Docs + Question → QA Models → Answers
5. Answers → API Response → User

## Key Features to Highlight:
- Non-normalized text preservation
- Incremental indexing
- Multi-model fallback
- Background processing
- Authentic Arabic output
