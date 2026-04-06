"""
Core DocuBot class responsible for:
- Loading documents from the docs/ folder
- Building a simple retrieval index (Phase 1)
- Retrieving relevant snippets (Phase 1)
- Supporting retrieval only answers
- Supporting RAG answers when paired with Gemini (Phase 2)
"""

import os
import glob


class DocuBot:
    def __init__(self, docs_folder="docs", llm_client=None):
        """
        docs_folder: directory containing project documentation files
        llm_client: optional Gemini client for LLM based answers
        """
        self.docs_folder = docs_folder
        self.llm_client = llm_client

        # Load documents into memory
        self.documents = self.load_documents()  # List of (filename, text)

        # Build a retrieval index
        self.index = self.build_index(self.documents)

    # -----------------------------------------------------------
    # Document Loading
    # -----------------------------------------------------------

    def load_documents(self):
        """
        Loads all .md and .txt files inside docs_folder.
        Returns a list of tuples: (filename, text)
        """
        docs = []
        pattern = os.path.join(self.docs_folder, "*.*")
        for path in glob.glob(pattern):
            if path.endswith(".md") or path.endswith(".txt"):
                with open(path, "r", encoding="utf8") as f:
                    text = f.read()
                filename = os.path.basename(path)
                docs.append((filename, text))
        return docs

    # -----------------------------------------------------------
    # Helper Methods
    # -----------------------------------------------------------

    def clean_token(self, token):
        """
        Lowercase a token and strip simple punctuation.
        """
        return token.lower().strip(".,!?()[]{}:;\"'`")

    def split_into_sections(self, text):
        """
        Split a document into smaller retrieval units.
        This version uses blank-line-separated chunks.
        """
        raw_sections = text.split("\n\n")
        sections = []

        for section in raw_sections:
            cleaned = section.strip()
            if cleaned:
                sections.append(cleaned)

        return sections

    # -----------------------------------------------------------
    # Index Construction
    # -----------------------------------------------------------

    def build_index(self, documents):
        """
        Build a tiny inverted index mapping lowercase words to the documents
        they appear in.

        Example structure:
        {
            "token": ["AUTH.md", "API_REFERENCE.md"],
            "database": ["DATABASE.md"]
        }
        """
        index = {}

        for filename, text in documents:
            sections = self.split_into_sections(text)

            for section in sections:
                words = section.split()

                for word in words:
                    cleaned_word = self.clean_token(word)

                    if cleaned_word:
                        if cleaned_word not in index:
                            index[cleaned_word] = []

                        if filename not in index[cleaned_word]:
                            index[cleaned_word].append(filename)

        return index

    # -----------------------------------------------------------
    # Scoring and Retrieval
    # -----------------------------------------------------------

    def score_document(self, query, text):
        """
        Return a simple relevance score for how well the text matches the query.

        Baseline:
        - Convert query into lowercase words
        - Count how many appear in the text
        - Return the count as the score
        """
        score = 0
        text_lower = text.lower()
        query_words = query.lower().split()

        for word in query_words:
            cleaned_word = self.clean_token(word)
            if cleaned_word and cleaned_word in text_lower:
                score += 1

        return score

    def retrieve(self, query, top_k=3):
        """
        Use the index and scoring function to select top_k relevant text sections.

        Return a list of (filename, text_section) sorted by score descending.
        """
        query_words = query.lower().split()
        candidate_files = set()

        for word in query_words:
            cleaned_word = self.clean_token(word)
            if cleaned_word in self.index:
                for filename in self.index[cleaned_word]:
                    candidate_files.add(filename)

        scored_sections = []

        for filename, text in self.documents:
            if filename not in candidate_files:
                continue

            sections = self.split_into_sections(text)

            for section in sections:
                score = self.score_document(query, section)

                if score > 0:
                    scored_sections.append((score, filename, section))

        scored_sections.sort(key=lambda x: x[0], reverse=True)

        # Guardrail: if nothing useful was found, return no results
        if not scored_sections:
            return []

        # Optional stronger guardrail:
        # if the best score is too weak, refuse
        best_score = scored_sections[0][0]
        if best_score < 1:
            return []

        top_results = scored_sections[:top_k]
        return [(filename, section) for score, filename, section in top_results]

    # -----------------------------------------------------------
    # Answering Modes
    # -----------------------------------------------------------

    def answer_retrieval_only(self, query, top_k=3):
        """
        Retrieval only mode.
        Returns raw snippets and filenames with no LLM involved.
        """
        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        formatted = []
        for filename, text in snippets:
            formatted.append(f"[{filename}]\n{text}\n")

        return "\n---\n".join(formatted)

    def answer_rag(self, query, top_k=3):
        """
        RAG mode.
        Uses retrieval to select snippets, then asks Gemini
        to generate an answer using only those snippets.
        """
        if self.llm_client is None:
            raise RuntimeError(
                "RAG mode requires an LLM client. Provide a GeminiClient instance."
            )

        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        return self.llm_client.answer_from_snippets(query, snippets)

    # -----------------------------------------------------------
    # Bonus Helper: concatenated docs for naive generation mode
    # -----------------------------------------------------------

    def full_corpus_text(self):
        """
        Returns all documents concatenated into a single string.
        This is used in Phase 0 for naive generation baselines.
        """
        return "\n\n".join(text for _, text in self.documents)