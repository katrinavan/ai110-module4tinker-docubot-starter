# DocuBot Model Card

This model card is a short reflection on your DocuBot system. Fill it out after you have implemented retrieval and experimented with all three modes:

1. Naive LLM over full docs  
2. Retrieval only  
3. RAG (retrieval plus LLM)

Use clear, honest descriptions. It is fine if your system is imperfect.

---

## 1. System Overview

**What is DocuBot trying to do?**  
Describe the overall goal in 2 to 3 sentences.

> DocuBot is designed to answer developer questions about a small documentation set. Its goal is to help a user find relevant information from the docs folder, either by retrieving raw snippets or by combining retrieval with an LLM to produce a clearer answer. The system is meant to show the difference between naive generation, retrieval only, and retrieval augmented generation.

**What inputs does DocuBot take?**  
For example: user question, docs in folder, environment variables.

> DocuBot takes a user question as input, along with the documentation files stored in the docs folder. It also uses environment variables such as `GEMINI_API_KEY` when LLM based features are enabled. In RAG mode, it uses both the question and the retrieved snippets as input to the model.

**What outputs does DocuBot produce?**

> DocuBot produces either a generated answer, retrieved text snippets, or a refusal message such as "I do not know based on these docs." The exact output depends on which mode is being used.

---

## 2. Retrieval Design

**How does your retrieval system work?**  
Describe your choices for indexing and scoring.

- How do you turn documents into an index?
- How do you score relevance for a query?
- How do you choose top snippets?

> My retrieval system first loads all markdown and text files from the docs folder. I split each document into smaller blank line separated sections so the system can return more focused text instead of an entire file. I built a simple inverted index that maps cleaned lowercase words to the filenames where they appear.  
>
> For scoring, I clean and lowercase the query words, then count how many query terms appear in each text section. Sections with more overlapping terms receive higher relevance scores. After scoring, I sort the sections by score in descending order and return the top scoring snippets.


**What tradeoffs did you make?**  
For example: speed vs precision, simplicity vs accuracy.

> I chose a very simple Python only retrieval system so it would be easy to understand and debug. This makes the system lightweight and readable, but less accurate than a more advanced retrieval method such as TF-IDF, BM25, or embeddings. Splitting documents into sections improved precision, but the scoring is still shallow because it mostly depends on keyword overlap rather than deeper meaning.

---

## 3. Use of the LLM (Gemini)

**When does DocuBot call the LLM and when does it not?**  
Briefly describe how each mode behaves.

- Naive LLM mode:
- Retrieval only mode:
- RAG mode:

> - **Naive LLM mode:** The system sends the question to the LLM in a very loose way and tries to answer using the full documentation corpus.  
> - **Retrieval only mode:** The system does not call the LLM at all. It only returns the top retrieved snippets from the docs.  
> - **RAG mode:** The system first retrieves relevant snippets, then sends only those snippets plus the question to the LLM to generate a grounded answer.

**What instructions do you give the LLM to keep it grounded?**  
Summarize the rules from your prompt. For example: only use snippets, say "I do not know" when needed, cite files.

> In RAG mode, the LLM is instructed to answer using only the retrieved snippets. It is told not to invent details, endpoints, or configuration values that are not supported by the provided text. If the snippets are not sufficient, it is instructed to say "I do not know based on the docs I have." The prompt also asks it to briefly mention which files it used.


---

## 4. Experiments and Comparisons

Run the **same set of queries** in all three modes. Fill in the table with short notes.

You can reuse or adapt the queries from `dataset.py`.

| Query | Naive LLM: helpful or harmful? | Retrieval only: helpful or harmful? | RAG: helpful or harmful? | Notes |
|------|---------------------------------|--------------------------------------|---------------------------|-------|
| Where is the auth token generated? | Helpful but somewhat risky | Helpful | Most helpful | Naive mode can sound correct but does not clearly show evidence. Retrieval only gives the relevant snippet. RAG gives a cleaner answer while staying grounded. |
| How do I connect to the database? | Helpful but vague | Helpful | Most helpful | Retrieval only shows the setup/database snippet, while RAG turns it into a clearer explanation. |
| Which endpoint lists all users? | Helpful but can overstate confidence | Helpful | Most helpful | Retrieval only is accurate but raw. RAG is easier to read and still grounded in the docs. |
| How does a client refresh an access token? | Helpful but weakly grounded | Helpful | Most helpful | This was a good example where RAG combined the snippet into a direct answer without returning too much text. |

**What patterns did you notice?**  

- When does naive LLM look impressive but untrustworthy?  
- When is retrieval only clearly better?  
- When is RAG clearly better than both?

> Naive LLM mode often looks the most polished because it writes in a fluent and confident style, but that also makes it easy to trust even when it is not clearly grounded in the docs. Retrieval only is clearly better when I want to verify exactly what evidence exists, because it shows the raw text directly. RAG is clearly better when the docs do contain an answer and I want both evidence and readability, since it combines focused retrieval with a more natural explanation.


---

## 5. Failure Cases and Guardrails

**Describe at least two concrete failure cases you observed.**  
For each one, say:

- What was the question?  
- What did the system do?  
- What should have happened instead?

> **Failure case 1:** I asked a vague or unsupported question about functionality not covered in the docs, such as payment or billing. Naive mode still tried to answer in a confident way, even though the documentation did not provide evidence. It should have refused or made the uncertainty much clearer instead of guessing.

> **Failure case 2:** In earlier retrieval only versions, the system returned whole documents instead of smaller sections. This buried the useful evidence inside a lot of irrelevant text and made it harder to interpret the result. It should have returned a smaller, more focused snippet, which is why I changed the retrieval unit to smaller sections.


**When should DocuBot say “I do not know based on the docs I have”?**  
Give at least two specific situations.

> DocuBot should say "I do not know based on the docs I have" when the query terms do not meaningfully match any retrieved sections. It should also refuse when the retrieved snippets are too weak, too generic, or too incomplete to support a confident answer. Another case is when the user asks about a feature or workflow that is simply not mentioned in the docs.


**What guardrails did you implement?**  
Examples: refusal rules, thresholds, limits on snippets, safe defaults.

> I added a guardrail in retrieval so the system returns no results when there are no useful matches. Because of that, the answering methods fall back to the refusal message instead of pretending to know. I also changed retrieval to use smaller text sections rather than whole files, which makes the returned evidence more focused and reduces the chance of hiding the important details inside irrelevant text.


---

## 6. Limitations and Future Improvements

**Current limitations**  
List at least three limitations of your DocuBot system.

1. The scoring is based on simple keyword overlap, so it can miss meaning when the wording is different.
2. The system does not understand synonyms, paraphrases, or deeper semantic relationships.
3. The retrieval index is very basic and only tracks filenames, not richer metadata such as section titles or positions.

**Future improvements**  
List two or three changes that would most improve reliability or usefulness.

1. Replace simple keyword counting with a stronger ranking method such as TF-IDF, BM25, or embeddings.
2. Improve chunking so snippets preserve better context without returning too much irrelevant text.
3. Add citation style formatting so answers more clearly show which snippets or files support them.


---

## 7. Responsible Use

**Where could this system cause real world harm if used carelessly?**  
Think about wrong answers, missing information, or over trusting the LLM.

> This system could cause harm if developers rely on it for important technical decisions without checking the source docs. A fluent but unsupported answer could lead someone to use the wrong endpoint, misunderstand authentication, or miss an important limitation in the documentation. It could also be risky if the system refuses too late and presents weak evidence as if it were enough.


**What instructions would you give real developers who want to use DocuBot safely?**  
Write 2 to 4 short bullet points.

- Always verify important answers against the original documentation.
- Treat fluent LLM outputs as drafts or hypotheses, not guaranteed facts.
- Prefer retrieval evidence when accuracy matters more than convenience.
- If the evidence is weak or missing, accept "I do not know" instead of guessing.

---
