

# LegalGraphRAG – GDPR Question Answering with Neo4j, LangChain & OpenRouter

LegalGraphRAG is a **Graph-RAG (Retrieval Augmented Generation)** system designed to answer legal questions about the **GDPR (RGPD)** using:

- A **Neo4j knowledge graph** (chapters, sections, articles, recitals)
- **Vector search** over GDPR articles
- **Cypher generation with LLMs**
- A **FastAPI backend**
- A **Streamlit frontend**

The system prioritizes **authoritative graph data**, falling back to **semantic vector retrieval** when needed.

---

## 🏗️ Architecture Overview

```

Streamlit UI
|
v
FastAPI Backend
|
+-- Text → Cypher (LLM)
|        |
|        v
|     Neo4j Graph
|
+-- Vector Retriever (Neo4jVector)
|
v
LLM (OpenRouter)

```

### Key Concepts
- **Graph-first reasoning**: answers rely on Neo4j when possible
- **Hybrid RAG**: Cypher + embeddings
- **No hallucinations**: model must say *"I don't know"* if data is missing

---

## 📦 Tech Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **LLM**: OpenRouter (via `ChatOpenAI`)
- **Graph DB**: Neo4j
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **Frameworks**:
  - LangChain
  - langchain-neo4j
  - langchain-core

---

## 🔐 Environment Variables

Create a `.env` file at the project root:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL_NAME=openai/gpt-4o-mini
````

---

## 🧠 Knowledge Graph Model

### Nodes

* `Loi`
* `considerant`
* `chapitre`
* `section`
* `article`

### Relationships

* `(:Loi)-[:A_CONSIDERANT]->(:considerant)`
* `(:Loi)-[:A_CHAPITRE]->(:chapitre)`
* `(:chapitre)-[:A_SECTION]->(:section)`
* `(:section)-[:A_ARTICLE]->(:article)`
* `(:chapitre)-[:A_ARTICLE]->(:article)`

Each **article node** contains:

* `titre`
* `text`
* `article`
* `chapitre`
* `section` (if applicable)

---

## 📥 Data Ingestion

The GDPR HTML file is parsed using `UnstructuredHTMLLoader`.

Steps:

1. Extract **recitals**
2. Split into **chapters**
3. Split chapters into **sections**
4. Split sections into **articles**
5. Create nodes + relationships
6. Push everything to Neo4j
7. Build vector index on article text

---

## 🔎 GraphRAG Pipeline

### 1. Text → Cypher

A prompt generates a **Cypher query** using the Neo4j schema.

### 2. Graph Query

The generated Cypher is executed against Neo4j.

### 3. Vector Search

If graph data is insufficient, semantic search retrieves relevant articles.

### 4. Answer Generation

The LLM receives:

* User question
* Graph query results
* Vector-retrieved context

Strict rules:

* Graph data is authoritative
* No external knowledge allowed
* If no answer → respond with *"Je ne sais pas"*

---

## 🚀 FastAPI Backend

Example endpoint:

```python
POST /query
{
  "query": "Quels sont les droits de la personne concernée ?"
}
```

Response:

```json
{
  "answer": "Selon l’article 15 du RGPD..."
}
```

Run backend:

```bash
uvicorn api.main:app --reload
```

---

## 🎨 Streamlit Frontend

Features:

* Question input
* Answer display
* Clean legal-focused UI

Run frontend:

```bash
streamlit run app_test.py
```

---

## 🧪 Example Questions

* *Quels sont les droits de la personne concernée ?*
* *Quelles sont les obligations du responsable du traitement ?*
* *Quand le consentement est-il requis ?*
* *Que dit l’article 5 du RGPD ?*

---

## ⚠️ Important Design Principles

* ❌ No hallucinations
* ❌ No markdown in Cypher output
* ✅ Graph > Vector > “I don’t know”
* ✅ Legal accuracy over fluency

---

## 📌 Future Improvements

* Multilingual answers (FR / EN)
* Citation of article numbers in UI
* RAG evaluation metrics
* Auth + role-based access
* Graph visualization

---

## 📜 License

MIT – for educational and research purposes.

