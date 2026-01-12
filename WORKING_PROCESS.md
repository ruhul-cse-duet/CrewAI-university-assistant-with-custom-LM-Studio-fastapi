# 🎓 University AI Assistant - Complete Working Process

## 📋 Project Overview

এই project একটি **University AI Assistant** যা students/teachers-দের questions-এর answer দেয় university website থেকে information collect করে।

---

## 🏗️ Architecture Overview

```
User (Student/Teacher)
    ↓
Frontend (Streamlit UI)
    ↓
Backend API (FastAPI)
    ↓
Query Router → Search → Scrape → FAISS → LLM → Response
```

---

## 🔄 Complete Workflow (Step by Step)

### **Step 1: User Asks Question (Frontend)**

**File:** `frontend/streamlit_app.py`

1. User Streamlit UI-তে question type করে
2. Language select করে (Bengali/English)
3. "Send" button press করে

**Code Flow:**
```python
# User input
user_input = "আজকের নোটিশ কী?"

# API call
response = requests.post(
    "http://127.0.0.1:8000/query",
    json={"query": user_input, "language": "bn"},
    timeout=200
)
```

---

### **Step 2: Backend Receives Request**

**File:** `backend/app.py`

1. FastAPI `/query` endpoint request receive করে
2. Rate limiting check করে
3. QueryRouter-এ request forward করে

**Code Flow:**
```python
@app.post("/query")
async def process_query(query_request: QueryRequest):
    # Async processing (non-blocking)
    result = await asyncio.wait_for(
        query_router.route_query(...),
        timeout=180
    )
    return result
```

---

### **Step 3: Query Router - Agent Selection**

**File:** `backend/router.py`

**3.1 Agent Classification:**
- Query analyze করে কোন agent use করবে
- Keywords match করে:
  - `notice/নোটিশ` → Notice Agent
  - `faculty/শিক্ষক` → Faculty Agent
  - `library/লাইব্রেরি` → Library Agent
  - etc.

**Code:**
```python
def _select_agent(self, query: str) -> str:
    # Keyword matching
    if 'notice' in query.lower():
        return 'notice'
    elif 'faculty' in query.lower():
        return 'faculty'
    # ...
```

**3.2 FAISS Cache Check:**
- আগে scraped data আছে কিনা check করে
- Similarity score > 0.8 হলে cached result use করে (fast!)

```python
cached_results = self.faiss_store.search(query, top_k=3)
if cached_results[0]['score'] > 0.8:
    # Use cache - very fast!
    return cached_answer
```

---

### **Step 4: Web Search (If Cache Miss)**

**File:** `backend/router.py` → `backend/tools/search_api.py`

**4.1 Search Query Enhancement:**
```python
# Original: "আজকের নোটিশ"
# Enhanced: "DUET আজকের নোটিশ notice announcement"
enhanced_query = f"{UNIVERSITY_NAME} {query} {agent_keywords}"
```

**4.2 Search API (Priority Order):**
1. **Serper API** (if API key available)
2. **Google Custom Search** (fallback)
3. **DuckDuckGo** (free, no API key needed)

**Code:**
```python
# Search with site restriction
results = search_api.search_university(
    query,
    site_restrict="buet.ac.bd"  # Only official domain
)
```

**4.3 URL Filtering:**
- শুধু official university domain-এর URLs keep করে
- PDF, images, videos filter out করে

```python
filtered = url_filter.filter_search_results(search_results)
# Only: buet.ac.bd, www.buet.ac.bd, etc.
```

---

### **Step 5: Web Scraping**

**File:** `backend/tools/scraper.py`

**5.1 Content Extraction:**
- Top 5 URLs scrape করে
- HTML parse করে
- Clean text extract করে

**Process:**
```python
for url in filtered_urls[:5]:
    doc = scraper.scrape_url(url)
    # Returns: {url, title, content, date}
```

**5.2 Text Cleaning:**
- Scripts, styles remove করে
- Bengali + English text keep করে
- Extra whitespace clean করে

**Time Limit:** Max 30 seconds total scraping

---

### **Step 6: FAISS Vector Store**

**File:** `backend/tools/faiss_store.py` → `backend/tools/embeddings.py`

**6.1 Embedding Generation:**
- Scraped content-কে embeddings-এ convert করে
- **Model:** `paraphrase-multilingual-mpnet-base-v2` (HuggingFace)
- Bengali + English support করে

```python
# Generate embeddings
embeddings = embedding_generator.generate(scraped_content)
# Shape: [num_docs, 768] (768-dimensional vectors)
```

**6.2 Store in FAISS:**
- Embeddings FAISS index-এ store করে
- Metadata (URL, title, date) save করে
- Future queries-এর জন্য cache হিসেবে use হবে

```python
faiss_store.add_documents(scraped_docs)
# Index updated, ready for semantic search
```

**6.3 Semantic Search:**
- User query-এর embedding generate করে
- FAISS-এ similarity search করে
- Top 3 most relevant results return করে

```python
results = faiss_store.search(
    user_query,
    top_k=3,
    threshold=0.5  # Minimum similarity
)
```

---

### **Step 7: LLM Answer Generation**

**File:** `backend/router.py` → `backend/llm.py`

**7.1 Context Preparation:**
- Search results format করে context হিসেবে
- Bengali/English prompt তৈরি করে

**Bengali Prompt:**
```
তুমি একজন বিশ্ববিদ্যালয়ের সহায়ক AI। নিচের তথ্যের উপর ভিত্তি করে প্রশ্নের উত্তর দাও।

প্রশ্ন: {user_query}

তথ্য:
{context_from_search}

উত্তর:
```

**7.2 LM Studio API Call:**
- Local LM Studio server-এ request send করে
- Model: User-এর configured model (default: lfm2-1.2b)
- Temperature: 0.3 (consistent answers)

```python
response = requests.post(
    "http://localhost:1234/v1/chat/completions",
    json={
        "model": "lmstudio-community/liquid/lfm2-1.2b",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 512
    },
    timeout=60
)
```

**7.3 Response Extraction:**
- LLM response extract করে
- Clean করে return করে

---

### **Step 8: Response to User**

**File:** `backend/app.py` → `frontend/streamlit_app.py`

**8.1 Backend Response:**
```json
{
    "success": true,
    "answer": "আজকের নোটিশগুলো হলো...",
    "agent": "notice",
    "source": "fresh",
    "processing_time_ms": 25340.5,
    "results": [...]
}
```

**8.2 Frontend Display:**
- Answer chat interface-এ show করে
- Processing time display করে
- Agent type এবং source show করে

---

## 🔧 Key Components Explained

### **1. Configuration (`backend/config.py`)**

**Required in `.env`:**
```env
UNIVERSITY_DOMAIN=buet.ac.bd
LM_STUDIO_BASE_URL=http://localhost:1234/v1
```

**Auto-managed:**
- University name (extracted from domain)
- Official domains list
- Embedding model (HuggingFace multilingual)
- All other settings

---

### **2. Embedding System (`backend/tools/embeddings.py`)**

**Model:** `paraphrase-multilingual-mpnet-base-v2`
- **Dimension:** 768
- **Languages:** Bengali + English
- **Lazy Loading:** Model load হয় first use-এ (not at startup)

**Why Multilingual?**
- Bengali questions handle করতে পারে
- English questions handle করতে পারে
- Mixed language support

---

### **3. FAISS Vector Store (`backend/tools/faiss_store.py`)**

**Purpose:**
- Scraped content store করে vector format-এ
- Fast semantic search enable করে
- Cache হিসেবে কাজ করে (similar questions fast answer)

**How it works:**
1. Documents → Embeddings (768-dim vectors)
2. Store in FAISS index
3. Query → Query embedding
4. Similarity search → Top K results

**Benefits:**
- First query: Slow (scraping + embedding)
- Similar queries: Fast (cache hit)

---

### **4. Search System (`backend/tools/search_api.py`)**

**Priority:**
1. **Serper API** (best, requires API key)
2. **Google Custom Search** (requires API key)
3. **DuckDuckGo** (free, no key needed)

**Site Restriction:**
- Only searches within university domain
- Example: `site:buet.ac.bd notice`

---

### **5. URL Filter (`backend/tools/url_filter.py`)**

**Filters:**
- ✅ Official domains only
- ✅ HTML/text content
- ❌ PDFs, images, videos
- ❌ External websites

**Example:**
```
Input: 10 search results
Output: 5 official URLs
```

---

### **6. Web Scraper (`backend/tools/scraper.py`)**

**Process:**
1. Fetch HTML
2. Parse with BeautifulSoup
3. Remove scripts, styles, nav, footer
4. Extract main content
5. Clean text (Bengali + English)
6. Return: {url, title, content, date}

**Timeout:** 10 seconds per URL
**Max Total:** 30 seconds for all URLs

---

### **7. LLM Integration (`backend/llm.py`)**

**LM Studio Setup:**
1. Download LM Studio
2. Load model (e.g., lfm2-1.2b)
3. Start server on port 1234
4. API compatible with OpenAI format

**Request Format:**
```json
{
    "model": "lmstudio-community/liquid/lfm2-1.2b",
    "messages": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}
    ],
    "temperature": 0.3,
    "max_tokens": 512
}
```

---

## 📊 Performance Flow

### **First Query (Cold Start)**
```
User Question
    ↓ (0s)
Agent Selection
    ↓ (0.1s)
Web Search
    ↓ (5-10s)
URL Filtering
    ↓ (0.1s)
Scraping (5 URLs)
    ↓ (10-15s)
Embedding Generation (Model Loading)
    ↓ (10-20s) ⚠️ First time only!
FAISS Storage
    ↓ (0.5s)
Semantic Search
    ↓ (0.1s)
LLM Generation
    ↓ (5-15s)
Response
    ↓
Total: 30-60 seconds
```

### **Subsequent Queries (Warm)**
```
User Question
    ↓ (0s)
Agent Selection
    ↓ (0.1s)
FAISS Cache Check
    ↓ (0.5s) ✅ Cache Hit!
LLM Generation
    ↓ (5-15s)
Response
    ↓
Total: 5-15 seconds (much faster!)
```

---

## 🎯 Example: Complete Flow

### **User Question:** "আজকের নোটিশ কী?"

**Step 1:** Frontend sends to `/query`

**Step 2:** Router selects "notice" agent

**Step 3:** FAISS cache empty (first query)

**Step 4:** Search web:
```
Query: "DUET আজকের নোটিশ notice announcement"
Site: buet.ac.bd
Results: 5 URLs found
```

**Step 5:** Filter URLs:
```
5 URLs → 3 official URLs
```

**Step 6:** Scrape:
```
URL 1: https://buet.ac.bd/notices/2024/notice1.html
  → Title: "Exam Schedule"
  → Content: "পরীক্ষার সময়সূচী..."

URL 2: https://buet.ac.bd/notices/2024/notice2.html
  → Title: "Form Submission"
  → Content: "ফর্ম জমা দেওয়ার..."

URL 3: https://buet.ac.bd/notices/2024/notice3.html
  → Title: "Holiday Notice"
  → Content: "ছুটির ঘোষণা..."
```

**Step 7:** Generate Embeddings:
```
3 documents → 3 embeddings (768-dim each)
Store in FAISS index
```

**Step 8:** Semantic Search:
```
Query embedding → Search in FAISS
Top 3 results with similarity scores:
  - Result 1: 0.92 (Exam Schedule)
  - Result 2: 0.85 (Form Submission)
  - Result 3: 0.78 (Holiday Notice)
```

**Step 9:** LLM Generation:
```
Context: [3 search results]
Prompt: "Answer based on this context..."
LLM Response: "আজকের নোটিশগুলো হলো:
1. পরীক্ষার সময়সূচী প্রকাশিত হয়েছে...
2. ফর্ম জমা দেওয়ার শেষ তারিখ...
3. আগামী সপ্তাহে ছুটি..."
```

**Step 10:** Response to User:
```
✅ Answer generated successfully!
⏱️ Time: 35.2s
Agent: notice
Source: fresh
```

---

## 🔄 Caching Strategy

### **FAISS Cache:**
- Scraped content permanently stored
- Similar questions → Fast answers
- No re-scraping needed

### **When Cache is Used:**
- Similarity score > 0.8
- Same domain content
- Recent scraping (< 24 hours)

### **When Cache is Bypassed:**
- New topic
- Low similarity (< 0.8)
- Cache expired

---

## 🚀 Optimization Features

### **1. Lazy Loading:**
- Embedding model loads on first use
- Fast startup (2-3 seconds)
- First query slower (model loading)

### **2. Async Processing:**
- Non-blocking API
- Multiple requests handled
- Timeout protection (180s)

### **3. Smart Scraping:**
- Only scrapes when needed
- Time limits (30s max)
- Error handling per URL

### **4. Domain Filtering:**
- Only official sources
- Faster processing
- More accurate results

---

## 📝 File Structure

```
project/
├── backend/
│   ├── app.py              # FastAPI main application
│   ├── router.py           # Query routing logic
│   ├── config.py           # Configuration
│   ├── llm.py              # LM Studio integration
│   ├── agents/             # Agent definitions
│   ├── tools/
│   │   ├── search_api.py   # Web search
│   │   ├── scraper.py      # Web scraping
│   │   ├── url_filter.py   # URL filtering
│   │   ├── embeddings.py   # Embedding generation
│   │   └── faiss_store.py  # Vector store
│   └── tasks/              # Task definitions
├── frontend/
│   ├── streamlit_app.py    # UI interface
│   └── style.css           # Styling
├── data/
│   └── faiss_index/        # Stored embeddings
└── .env                    # Configuration
```

---

## 🎓 Summary

**Complete Flow:**
1. **User** asks question in UI
2. **Frontend** sends to backend API
3. **Router** selects agent and checks cache
4. **Search** finds relevant URLs
5. **Scrape** extracts content
6. **Embed** converts to vectors
7. **Store** in FAISS for future
8. **Search** semantically in FAISS
9. **LLM** generates answer
10. **Response** sent back to user

**Key Features:**
- ✅ Bilingual (Bengali + English)
- ✅ Smart caching (FAISS)
- ✅ Official sources only
- ✅ Fast responses (after first query)
- ✅ Local LLM (LM Studio)
- ✅ No external API costs

---

**Made with ❤️ for University Students**

