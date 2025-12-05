# 🐍 Python Code Assistant | Βοηθός Κώδικα Python

A comprehensive AI-powered Python code generation and optimization system built with OpenAI GPT models, featuring RAG (Retrieval-Augmented Generation), Control Flow Graph (CFG) and Data Flow Graph (DFG) visualization, and intelligent code optimization.

Ένα ολοκληρωμένο σύστημα δημιουργίας και βελτιστοποίησης κώδικα Python με τεχνητή νοημοσύνη, που χρησιμοποιεί μοντέλα OpenAI GPT, με χαρακτηριστικά RAG (Retrieval-Augmented Generation), οπτικοποίηση Control Flow Graph (CFG) και Data Flow Graph (DFG), και έξυπνη βελτιστοποίηση κώδικα.

---

## 📋 Table of Contents | Πίνακας Περιεχομένων

- [Features | Χαρακτηριστικά](#features--χαρακτηριστικά)
- [Project Structure | Δομή Έργου](#project-structure--δομή-έργου)
- [Setup Instructions | Οδηγίες Εγκατάστασης](#setup-instructions--οδηγίες-εγκατάστασης)
- [How to Run | Πώς να Εκτελέσετε](#how-to-run--πώς-να-εκτελέσετε)
- [Architecture Overview | Επισκόπηση Αρχιτεκτονικής](#architecture-overview--επισκόπηση-αρχιτεκτονικής)
- [Component Details | Λεπτομέρειες Στοιχείων](#component-details--λεπτομέρειες-στοιχείων)
- [How It Works | Πώς Λειτουργεί](#how-it-works--πώς-λειτουργεί)
- [Configuration | Διαμόρφωση](#configuration--διαμόρφωση)

---

## ✨ Features | Χαρακτηριστικά

### Part A: Code Generation Chatbot | Μέρος Α: Chatbot Δημιουργίας Κώδικα

**English:**

- **Intelligent Code Generation**: Generate Python functions based on natural language descriptions
- **RAG-Enhanced Responses**: Retrieves relevant specifications from a knowledge base using semantic search
- **Visual Diagrams**: Automatically generates Control Flow Graphs (CFG) and Data Flow Graphs (DFG)
- **Conversation History**: Maintains context across multiple interactions
- **Knowledge Base Integration**: Uses embedded specifications to generate accurate, specification-compliant code

**Ελληνικά:**

- **Έξυπνη Δημιουργία Κώδικα**: Δημιουργία συναρτήσεων Python βασισμένη σε περιγραφές φυσικής γλώσσας
- **Βελτιωμένες Απαντήσεις με RAG**: Ανακτά σχετικές προδιαγραφές από βάση γνώσης χρησιμοποιώντας σημασιολογική αναζήτηση
- **Οπτικά Διαγράμματα**: Αυτόματη δημιουργία Διαγραμμάτων Ροής Ελέγχου (CFG) και Διαγραμμάτων Ροής Δεδομένων (DFG)
- **Ιστορικό Συνομιλίας**: Διατηρεί το πλαίσιο σε πολλαπλές αλληλεπιδράσεις
- **Ενσωμάτωση Βάσης Γνώσης**: Χρησιμοποιεί ενσωματωμένες προδιαγραφές για τη δημιουργία ακριβούς κώδικα συμβατού με τις προδιαγραφές

### Part B: Code Optimizer | Μέρος Β: Βελτιστοποιητής Κώδικα

**English:**

- **Nested IF Detection**: Identifies and warns about deeply nested conditional statements
- **LLM-Powered Optimization**: Uses GPT models to suggest cleaner, more readable code
- **PDF-Based System Prompt**: Loads optimization instructions from a PDF file
- **Side-by-Side Comparison**: View original and optimized code simultaneously

**Ελληνικά:**

- **Ανίχνευση Εμφωλευμένων IF**: Εντοπίζει και προειδοποιεί για βαθιά εμφωλευμένες δηλώσεις συνθηκών
- **Βελτιστοποίηση με LLM**: Χρησιμοποιεί μοντέλα GPT για να προτείνει καθαρότερο, πιο αναγνώσιμο κώδικα
- **Οδηγίες από PDF**: Φορτώνει οδηγίες βελτιστοποίησης από αρχείο PDF
- **Σύγκριση Δίπλα-Δίπλα**: Προβολή του αρχικού και του βελτιστοποιημένου κώδικα ταυτόχρονα

---

## 📁 Project Structure | Δομή Έργου

**English:** Project organized into two main parts - Part A for code generation with RAG and Part B for code optimization.

**Ελληνικά:** Το έργο οργανώνεται σε δύο κύρια μέρη - Μέρος Α για δημιουργία κώδικα με RAG και Μέρος Β για βελτιστοποίηση κώδικα.

```text
GenerativeAI/
├── streamlit_app.py              # Main web application entry point
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (API keys)
├── .gitignore                    # Git ignore rules
│
├── partA/                        # Code Generation Module
│   ├── llm_agent.py             # LLM agent with function calling
│   ├── rag_system.py            # RAG system with embeddings
│   └── knowledge_base/
│       ├── functions.txt        # Knowledge base specifications
│       └── embeddings.json      # Cached embeddings
│
├── partB/                        # Code Optimization Module
│   ├── optimizer.py             # Code optimizer
│   ├── systemPrompt.pdf         # Optimization instructions
│   ├── systemPrompt.txt         # Source text for PDF
│   └── create_system_prompt_pdf.py  # PDF generator
│
├── diagrams/                     # Generated CFG/DFG diagrams (auto-created)
└── sessions/                     # Conversation sessions (optional)
```

---

## 🚀 Setup Instructions | Οδηγίες Εγκατάστασης

### Prerequisites | Προαπαιτούμενα

**English:**

- Python 3.8 or higher
- OpenAI API key
- Graphviz system library (for diagram rendering)

**Ελληνικά:**

- Python 3.8 ή νεότερη έκδοση
- Κλειδί API του OpenAI
- Βιβλιοθήκη συστήματος Graphviz (για απόδοση διαγραμμάτων)

### 1. Clone the Repository | Κλωνοποίηση του Αποθετηρίου

```bash
git clone <repository-url>
cd GenerativeAI
```

### 2. Install Graphviz | Εγκατάσταση Graphviz (System Dependency)

**macOS:**

```bash
brew install graphviz
```

**Ubuntu/Debian:**

```bash
sudo apt-get install graphviz
```

**Windows:**

Download and install from [graphviz.org](https://graphviz.org/download/)

Κατεβάστε και εγκαταστήστε από [graphviz.org](https://graphviz.org/download/)

### 3. Create Virtual Environment | Δημιουργία Εικονικού Περιβάλλοντος

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 4. Install Python Dependencies | Εγκατάσταση Εξαρτήσεων Python

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables | Διαμόρφωση Μεταβλητών Περιβάλλοντος

**English:** Create a `.env` file in the project root:

**Ελληνικά:** Δημιουργήστε ένα αρχείο `.env` στη ρίζα του έργου:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 6. Generate System Prompt PDF | Δημιουργία PDF Οδηγιών Συστήματος (Part B)

```bash
python partB/create_system_prompt_pdf.py
```

---

## ▶️ How to Run | Πώς να Εκτελέσετε

### Start the Application | Εκκίνηση της Εφαρμογής

```bash
streamlit run streamlit_app.py
```

**English:** The application will open in your default browser at `http://localhost:8501`

**Ελληνικά:** Η εφαρμογή θα ανοίξει στο προεπιλεγμένο πρόγραμμα περιήγησης στη διεύθυνση `http://localhost:8501`

### Restart the Application | Επανεκκίνηση της Εφαρμογής

```bash
pkill -f streamlit; sleep 1; streamlit run streamlit_app.py
```

---

## 🏗️ Architecture Overview | Επισκόπηση Αρχιτεκτονικής

**English:** The system consists of a Streamlit web interface that orchestrates two main components: Part A (code generation with RAG) and Part B (code optimization).

**Ελληνικά:** Το σύστημα αποτελείται από μια διεπαφή ιστού Streamlit που ενορχηστρώνει δύο κύρια στοιχεία: Μέρος Α (δημιουργία κώδικα με RAG) και Μέρος Β (βελτιστοποίηση κώδικα).

```text
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Web App                    │
│                  (streamlit_app.py)                     │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
               ▼                      ▼
    ┌──────────────────┐   ┌──────────────────┐
    │   Part A: Chat   │   │ Part B: Optimizer│
    │   (llm_agent.py) │   │  (optimizer.py)  │
    └────────┬─────────┘   └──────────────────┘
             │
             ▼
    ┌──────────────────┐
    │   RAG System     │
    │ (rag_system.py)  │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  Knowledge Base  │
    │  (functions.txt) │
    └──────────────────┘
```

---

## 🔍 Component Details | Λεπτομέρειες Στοιχείων

### Part A: Code Generation Chatbot | Μέρος Α: Chatbot Δημιουργίας Κώδικα

#### **LLMAgent (`partA/llm_agent.py`)**

**English Purpose:** Orchestrates code generation with structured outputs using OpenAI function calling.

**Ελληνικός Σκοπός:** Ενορχηστρώνει τη δημιουργία κώδικα με δομημένες εξόδους χρησιμοποιώντας κλήσεις συναρτήσεων του OpenAI.

**Key Methods:**

1. **`__init__(model="o4-mini")`**
   - Initializes OpenAI client
   - Creates `diagrams/` directory for CFG/DFG outputs
   - Initializes RAG system
   - Defines function schema for structured responses

2. **`chat(user_message, conversation_history) -> Dict`**
   - **Step 1**: Retrieves relevant context from knowledge base using RAG
   - **Step 2**: Builds conversation messages with system prompt
   - **Step 3**: Calls OpenAI API with forced function calling (`tool_choice`)
   - **Step 4**: Extracts structured arguments from LLM response
   - **Step 5**: Processes response and renders diagrams
   
   **Returns**: Dictionary with `chat_reply`, `generated_code`, `cfg_path`, `dfg_path`

3. **`_build_system_prompt(rag_context) -> str`**
   - Formats RAG context with similarity scores
   - Instructs LLM to follow specifications if score > 0.5
   - Returns system prompt with embedded context

4. **`_render_diagram(dot_string, diagram_type) -> str`**
   - Converts DOT notation to PNG using Graphviz
   - Saves to `diagrams/` with timestamp
   - Returns file path for Streamlit display

5. **`_process_llm_response(args) -> Dict`**
   - Extracts code and DOT strings from function call
   - Renders CFG and DFG diagrams
   - Returns structured result dictionary

**Function Calling Schema:**
```python
{
    "name": "respond",
    "parameters": {
        "chat_reply": "Conversational response",
        "generated_code": "Python code (optional)",
        "cfg_dot": "Control Flow Graph in DOT format",
        "dfg_dot": "Data Flow Graph in DOT format"
    }
}
```

#### **InMemoryRAG (`partA/rag_system.py`)**

**Purpose**: Semantic search over knowledge base using OpenAI embeddings.

**Key Methods:**

1. **`__init__()`**
   - Sets paths to `knowledge_base/functions.txt` and `embeddings.json`
   - Initializes OpenAI client
   - Uses `text-embedding-3-small` model

2. **`initialize()`**
   - Loads text chunks from knowledge base
   - Generates or loads cached embeddings

3. **`_load_chunks()`**
   - Reads `functions.txt`
   - Splits by `---` delimiter
   - Filters chunks with minimum 20 characters

4. **`_generate_embeddings()`**
   - Computes SHA256 hash of knowledge base
   - Loads cached embeddings if hash matches (avoids redundant API calls)
   - Generates new embeddings via OpenAI API if needed
   - Caches embeddings with hash for validation

5. **`_compute_kb_hash() -> str`**
   - Computes SHA256 hash of knowledge base file
   - Used for cache invalidation

6. **`retrieve_relevant_embeddings(query, top_k=3) -> List[Dict]`**
   - Embeds user query using OpenAI
   - Computes cosine similarity with all knowledge base chunks
   - Returns top-k most relevant chunks with scores

**Embedding Cache Structure:**
```json
{
  "chunks": ["chunk1", "chunk2", ...],
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
  "model": "text-embedding-3-small",
  "kb_hash": "sha256_hash_of_functions.txt"
}
```

#### **Knowledge Base (`partA/knowledge_base/functions.txt`)**

Contains function specifications in structured format:
```
## Function: calculate_order_total
### Description
Calculates the final total cost...
### Input
* **subtotal (float):** The sum of prices...
* **is_member (boolean):** Indicates if...
### Process
1. Initialize `discount_rate` to 0.0.
2. Check if `subtotal` is greater than 100.0.
   * If yes, set `discount_rate` to 0.10
...
### Output
* **final_total (float):** The final amount...
---
## Function: next_function
...
```

---

### Part B: Code Optimizer

#### **CodeOptimizer (`partB/optimizer.py`)**

**Purpose**: Analyzes and optimizes Python code using LLM guidance.

**Key Methods:**

1. **`__init__(model="o4-mini")`**
   - Initializes OpenAI client
   - Loads system prompt from PDF

2. **`_load_system_prompt() -> str`**
   - Reads `systemPrompt.pdf` using PyPDF2
   - Extracts text from all pages
   - Returns concatenated prompt

3. **`optimize_code(code) -> Dict`**
   - Sends code to OpenAI with optimization instructions
   - Strips markdown code fences from response
   - Returns dictionary with `original_code`, `optimized_code`, `success`, `error`

**System Prompt (`partB/systemPrompt.pdf`):**
- Instructs LLM to detect nested IF statements (4+ levels)
- Adds `WARNING:` comments to problematic patterns
- Suggests improvements (guard clauses, early returns, etc.)

---

## ⚙️ How It Works | Πώς Λειτουργεί

### Code Generation Flow (Part A) | Ροή Δημιουργίας Κώδικα (Μέρος Α)

**English:**

1. **User Input**: User types a natural language request (e.g., "create a function that checks cart total")

2. **RAG Retrieval**:
   - Query is embedded using OpenAI embeddings
   - Cosine similarity computed against knowledge base
   - Top 3 most relevant chunks retrieved

3. **System Prompt Construction**:
   - RAG context formatted with similarity scores
   - Instructions added to follow specifications if relevant (score > 0.5)

4. **LLM Function Calling**:
   - OpenAI API called with `tool_choice` forcing `respond` function
   - LLM returns structured JSON with `chat_reply`, `generated_code`, `cfg_dot`, `dfg_dot`

5. **Diagram Rendering**:
   - DOT strings converted to PNG using Graphviz
   - Files saved to `diagrams/` with timestamps

6. **Response Display**:
   - Streamlit displays chat reply, code, and diagrams in 3 columns

**Ελληνικά:**

1. **Είσοδος Χρήστη**: Ο χρήστης πληκτρολογεί ένα αίτημα σε φυσική γλώσσα (π.χ., "δημιούργησε μια συνάρτηση που ελέγχει το σύνολο του καλαθιού")

2. **Ανάκτηση RAG**:
   - Το ερώτημα ενσωματώνεται χρησιμοποιώντας embeddings του OpenAI
   - Υπολογίζεται η ομοιότητα συνημιτόνου με τη βάση γνώσης
   - Ανακτώνται τα 3 πιο σχετικά τμήματα

3. **Κατασκευή System Prompt**:
   - Το πλαίσιο RAG μορφοποιείται με βαθμολογίες ομοιότητας
   - Προστίθενται οδηγίες για ακολούθηση προδιαγραφών εάν είναι σχετικές (score > 0.5)

4. **Κλήση Συνάρτησης LLM**:
   - Καλείται το API του OpenAI με `tool_choice` που επιβάλλει τη συνάρτηση `respond`
   - Το LLM επιστρέφει δομημένο JSON με `chat_reply`, `generated_code`, `cfg_dot`, `dfg_dot`

5. **Απόδοση Διαγραμμάτων**:
   - Τα strings DOT μετατρέπονται σε PNG χρησιμοποιώντας Graphviz
   - Τα αρχεία αποθηκεύονται στο `diagrams/` με χρονικές σημάνσεις

6. **Προβολή Απάντησης**:
   - Το Streamlit εμφανίζει την απάντηση συνομιλίας, τον κώδικα και τα διαγράμματα σε 3 στήλες

### Code Optimization Flow (Part B) | Ροή Βελτιστοποίησης Κώδικα (Μέρος Β)

**English:**

1. **User Input**: User pastes code into text area

2. **Prompt Construction**:
   - System prompt loaded from PDF
   - User code appended to optimization request

3. **LLM Analysis**:
   - OpenAI analyzes code structure
   - Detects nested IF statements (4+ levels)
   - Suggests optimizations

4. **Response Processing**:
   - Markdown code fences removed
   - Optimized code displayed alongside original

**Ελληνικά:**

1. **Είσοδος Χρήστη**: Ο χρήστης επικολλά κώδικα στην περιοχή κειμένου

2. **Κατασκευή Prompt**:
   - Το system prompt φορτώνεται από PDF
   - Ο κώδικας του χρήστη προστίθεται στο αίτημα βελτιστοποίησης

3. **Ανάλυση LLM**:
   - Το OpenAI αναλύει τη δομή του κώδικα
   - Ανιχνεύει εμφωλευμένες δηλώσεις IF (4+ επίπεδα)
   - Προτείνει βελτιστοποιήσεις

4. **Επεξεργασία Απάντησης**:
   - Αφαιρούνται τα code fences markdown
   - Ο βελτιστοποιημένος κώδικας εμφανίζεται δίπλα στον αρχικό

---

## 🔧 Configuration | Διαμόρφωση

### Environment Variables (`.env`)
```bash
OPENAI_API_KEY=sk-...  # Your OpenAI API key
```

### Model Configuration
Change the model in `streamlit_app.py`:
```python
st.session_state.agent = LLMAgent(model="gpt-4")  # Default: o4-mini
st.session_state.optimizer = CodeOptimizer(model="gpt-4")
```

### RAG Configuration
Edit `partA/rag_system.py`:
```python
self.model = "text-embedding-3-large"  # Default: text-embedding-3-small
```

Change top-k results in `partA/llm_agent.py`:
```python
relevant = self.rag_system.retrieve_relevant_embeddings(user_message, top_k=5)  # Default: 3
```

### Logging
Adjust logging levels in respective files:
```python
logging.getLogger("openai").setLevel(logging.DEBUG)  # INFO, WARNING, ERROR
```

---

## 📝 Additional Notes | Επιπλέον Σημειώσεις

### Cached Embeddings | Cached Ενσωματώσεις

**English:**

- Embeddings are automatically cached in `partA/knowledge_base/embeddings.json`
- Cache is invalidated when `functions.txt` is modified (SHA256 hash check)
- Reduces API calls and improves response time

**Ελληνικά:**

- Οι ενσωματώσεις (embeddings) αποθηκεύονται αυτόματα στο `partA/knowledge_base/embeddings.json`
- Η cache ακυρώνεται όταν τροποποιείται το `functions.txt` (έλεγχος hash SHA256)
- Μειώνει τις κλήσεις API και βελτιώνει τον χρόνο απόκρισης

### Diagram Storage | Αποθήκευση Διαγραμμάτων

**English:**

- Diagrams saved to `diagrams/` (git-ignored)
- Timestamped filenames prevent overwrites: `cfg_20251205_143022.png`

**Ελληνικά:**

- Τα διαγράμματα αποθηκεύονται στο `diagrams/` (αγνοείται από git)
- Τα ονόματα αρχείων με χρονικές σημάνσεις αποτρέπουν αντικαταστάσεις: `cfg_20251205_143022.png`

### Sessions | Συνεδρίες

**English:**

- Conversation history stored in Streamlit session state (memory only)
- `sessions/` folder exists for potential persistence but is not currently used

**Ελληνικά:**

- Το ιστορικό συνομιλίας αποθηκεύεται στην κατάσταση συνεδρίας του Streamlit (μόνο στη μνήμη)
- Ο φάκελος `sessions/` υπάρχει για πιθανή διατήρηση αλλά δεν χρησιμοποιείται προς το παρόν

---

## 🛠️ Troubleshooting | Αντιμετώπιση Προβλημάτων

### "Graphviz executable not found"

**English:** Install system-level Graphviz (see Setup Instructions)

**Ελληνικά:** Εγκαταστήστε το Graphviz σε επίπεδο συστήματος (δείτε Οδηγίες Εγκατάστασης)

### "No embeddings.json found"

**English:** RAG system will automatically generate embeddings on first run

**Ελληνικά:** Το σύστημα RAG θα δημιουργήσει αυτόματα embeddings στην πρώτη εκτέλεση

### API Rate Limits | Όρια Ρυθμού API

**English:** Adjust request frequency or upgrade OpenAI plan

**Ελληνικά:** Προσαρμόστε τη συχνότητα αιτημάτων ή αναβαθμίστε το πλάνο OpenAI

### "Module not found" errors | Σφάλματα "Module not found"

**English:** Ensure virtual environment is activated and dependencies installed

**Ελληνικά:** Βεβαιωθείτε ότι το εικονικό περιβάλλον είναι ενεργοποιημένο και οι εξαρτήσεις εγκατεστημένες

---

## 📄 License

This project is for educational purposes.

---

## 🤝 Contributing

This is a course project. For questions, contact the repository owner.
