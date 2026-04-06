# DocuBot

DocuBot is a small documentation assistant that helps answer developer questions about a codebase.  
It can operate in three different modes:

1. **Naive LLM mode**  
   Sends the entire documentation corpus to a Gemini model and asks it to answer the question.

2. **Retrieval only mode**  
   Uses a simple indexing and scoring system to retrieve relevant snippets without calling an LLM.

3. **RAG mode (Retrieval Augmented Generation)**  
   Retrieves relevant snippets, then asks Gemini to answer using only those snippets.

The docs folder contains realistic developer documents (API reference, authentication notes, database notes), but these files are **just text**. They support retrieval experiments and do not require students to set up any backend systems.

---

## Setup

### 1. Install Python dependencies

    pip install -r requirements.txt

### 2. Configure environment variables

Copy the example file:

    cp .env.example .env

Then edit `.env` to include your Gemini API key:

    GEMINI_API_KEY=your_api_key_here

If you do not set a Gemini key, you can still run retrieval only mode.

---

## Running DocuBot

Start the program:

    python main.py

Choose a mode:

- **1**: Naive LLM (Gemini reads the full docs)  
- **2**: Retrieval only (no LLM)  
- **3**: RAG (retrieval + Gemini)

You can use built in sample queries or type your own.

---

## Running Retrieval Evaluation (optional)

    python evaluation.py

This prints simple retrieval hit rates for sample queries.

---

## Modifying the Project

You will primarily work in:

- `docubot.py`  
  Implement or improve the retrieval index, scoring, and snippet selection.

- `llm_client.py`  
  Adjust the prompts and behavior of LLM responses.

- `dataset.py`  
  Add or change sample queries for testing.

---

## Requirements

- Python 3.9+
- A Gemini API key for LLM features (only needed for modes 1 and 3)
- No database, no server setup, no external services besides LLM calls

## SUMMARY
This project helps students understand the core idea behind retrieval augmented generation by showing that a chatbot should not just generate answers, but first search for relevant evidence in the docs. A key concept students needed to understand was how retrieval works as a pipeline: building an index, scoring relevance, and returning the best matching text before answering. Students may struggle with deciding what unit of text to retrieve, since returning whole documents is easier to code but often gives noisy and unfocused results. AI was helpful for brainstorming simple indexing and chunking strategies, explaining how functions connected together, and suggesting ways to refactor the retrieval logic. However, AI could also be misleading when it suggested code that worked mechanically but did not match the assignment’s goals, or when it made the retrieval system more complicated than necessary. One way I would guide a student without giving the answer is by asking them to trace what happens to a question step by step, from query to scoring to returned snippet, and then identify where the result becomes too broad or unsupported. That keeps the focus on reasoning through the system instead of copying a solution.
