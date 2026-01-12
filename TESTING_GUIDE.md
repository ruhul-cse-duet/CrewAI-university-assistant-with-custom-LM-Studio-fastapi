# 🧪 Complete Project Testing Guide

## ✅ Updated with Real Working DUET URLs

### 📋 Verified Working URLs (12 URLs):
```
✅ https://www.duet.ac.bd
✅ https://duet.ac.bd
✅ https://www.duet.ac.bd/admission
✅ https://www.duet.ac.bd/departments
✅ https://www.duet.ac.bd/academic-calender
✅ https://www.duet.ac.bd/about/history
✅ https://www.duet.ac.bd/department/cse
✅ https://www.duet.ac.bd/department/eee
✅ https://www.duet.ac.bd/department/me
✅ https://www.duet.ac.bd/office/central-library
✅ https://www.duet.ac.bd/notice/all-notices
✅ https://www.duet.ac.bd/event/conference
✅ https://www.duet.ac.bd/faculty/eee
```

---

## 🎯 Test Files Overview

### 1️⃣ **check_duet_urls.py** - URL Verification
Tests which DUET URLs are accessible and working.

```bash
python check_duet_urls.py
```

**Output:**
- ✅ List of working URLs
- ❌ List of broken URLs
- 📊 Summary with URL counts

---

### 2️⃣ **test_scraping_and_filtering.py** - Scraping Components
Tests individual components: URL filtering, scraping, storage.

```bash
python test_scraping_and_filtering.py
```

**Tests:**
- ✅ URL Filtering (5 URLs)
- ✅ Web Scraping (real content)
- ✅ Combined Filter + Scrape
- ✅ Data Storage (JSON + TXT)

**Output Files:**
```
scraped_data/
├── scraped_content.json
└── scraped_content.txt
```

---

### 3️⃣ **test_full_pipeline.py** - End-to-End RAG Pipeline
Tests the complete workflow from search to answer generation.

```bash
python test_full_pipeline.py
```

**Pipeline Steps:**
1. 🔍 **Search** - Google search for DUET info
2. 🔽 **Filter** - Keep only official DUET URLs  
3. 📥 **Scrape** - Extract content from pages
4. 💾 **Store** - Add to FAISS vector database
5. ❓ **Query** - Test similarity search
6. 🤖 **LLM** - Generate answers (if LM Studio running)

---

### 4️⃣ **test_lm_studio.py** - LLM Testing
Tests LM Studio connection and response generation.

```bash
pytest test_lm_studio.py -v
```

**Tests:**
- ✅ LM Studio server connection
- ✅ LLM initialization
- ✅ Simple prompts
- ✅ Bengali prompts
- ✅ University queries

---

## 🚀 Quick Start - Run All Tests

```bash
cd "E:\Data Science\ML_and_DL_project\NLP Project\university-ai-assistant-crewai-fastapi-lmstudio"

# Activate environment
conda activate RAG_University_Assistant_chatbot

# 1. Check URLs (verify working links)
python check_duet_urls.py

# 2. Test scraping components
python test_scraping_and_filtering.py

# 3. Test full RAG pipeline (RECOMMENDED)
python test_full_pipeline.py

# 4. Test LM Studio (if running)
pytest test_lm_studio.py -v
```

---

## ✅ Success Criteria

### For Users to Get Answers, These Must Work:

1. **Search** ✅ - Must find DUET URLs
2. **Filter** ✅ - Must keep official URLs only
3. **Scrape** ✅ - Must extract content
4. **Store** ✅ - Must save in FAISS
5. **Query** ✅ - Must retrieve relevant docs
6. **LLM** ⚠️ - Optional (needs LM Studio)

### Expected Final Output:

```
================================================================================
  📊 PIPELINE TEST SUMMARY
================================================================================

✅ PASSED: Search API
✅ PASSED: URL Filtering
✅ PASSED: Web Scraping
✅ PASSED: FAISS Storage
✅ PASSED: RAG Query
✅ PASSED: LLM Answer

Results: 6/6 steps passed

🎉 Pipeline working! Users can get answers from DUET data!
✅ Search → Filter → Scrape → Store → Query all working
✅ LLM answer generation also working
```

---

## 🔧 Troubleshooting

### If Search Fails:
- Check internet connection
- Check Google API key in .env

### If Scraping Fails:
- Run `python check_duet_urls.py` first
- Verify URLs are accessible
- Check firewall/proxy settings

### If FAISS Fails:
- Install: `pip install faiss-cpu sentence-transformers`
- Check embeddings model downloads

### If LLM Fails:
- Start LM Studio
- Load a model
- Start local server on port 1234

---

## 📊 What Each Test Does

| Test File | Purpose | Duration | Critical |
|-----------|---------|----------|----------|
| check_duet_urls.py | Verify URLs work | 30s | No |
| test_scraping_and_filtering.py | Test components | 20s | Yes |
| test_full_pipeline.py | **Test everything** | 60s | **YES** |
| test_lm_studio.py | Test LLM only | 30s | Optional |

---

## 🎯 For Production

Run this command to verify everything works:

```bash
python test_full_pipeline.py
```

If this passes with 5/6 or 6/6, **users can get answers!** ✅

LLM (6th step) is optional - RAG will work without it, but answers won't be generated.

---

## 📝 Notes

- All tests use **real verified DUET URLs**
- Brotli encoding issue **fixed**
- UTF-8 encoding **properly handled**
- Tests are **idempotent** (safe to run multiple times)
- Test data saved in `scraped_data/` folder

---

## 🆘 Support

If tests fail:
1. Check error messages carefully
2. Run individual component tests first
3. Verify all dependencies installed
4. Check .env configuration
5. Ensure internet connectivity

---

**Last Updated:** With real working DUET URLs
**Status:** ✅ All tests passing
**User Experience:** ✅ Users can get answers from DUET data
