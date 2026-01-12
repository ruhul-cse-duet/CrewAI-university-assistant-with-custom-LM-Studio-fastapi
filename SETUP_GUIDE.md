# 🚀 Quick Setup Guide for Beginners

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment

Create a `.env` file in the project root with:

```env
# REQUIRED: Your university domain
UNIVERSITY_DOMAIN=duet.ac.bd

# REQUIRED: LM Studio URL (default is fine if running locally)
LM_STUDIO_BASE_URL=http://localhost:1234/v1
```

That's it! The system will handle everything else automatically.

## Step 3: Start LM Studio

1. Download and install LM Studio from https://lmstudio.ai/
2. Load a model (recommended: Qwen 2.5 7B or Llama 3.2 3B)
3. Start the local server on port 1234
4. Verify: Open http://localhost:1234/v1/models in browser

## Step 4: Run the Application

### Option A: Quick Start (Recommended)
```bash
python start.py
```

### Option B: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run streamlit_app.py
```

## Step 5: Access the Application

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## How It Works

1. **User asks a question** (Bengali or English)
2. **System identifies the topic** (Notice/Faculty/Library/etc.)
3. **Searches university website** based on the question
4. **Scrapes relevant pages** (one-time per question for speed)
5. **Stores in FAISS** vector database
6. **Finds relevant information** using semantic search
7. **Generates answer** using LM Studio LLM
8. **Returns response** in the same language as the question

## Features

✅ **Bilingual Support**: Bengali and English  
✅ **Smart Scraping**: Only scrapes when needed  
✅ **Fast Responses**: Cached results for similar questions  
✅ **Multiple Agents**: Handles different types of questions  
✅ **Beautiful UI**: Modern, responsive interface  

## Troubleshooting

### Issue: LM Studio not connecting
- Make sure LM Studio is running
- Check port 1234 is not blocked
- Verify model is loaded in LM Studio

### Issue: No search results
- Check internet connection
- Verify UNIVERSITY_DOMAIN is correct
- Try adding SERPER_API_KEY in .env (optional)

### Issue: Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.10+ required)

## Need Help?

Check the main README.md for detailed documentation.

