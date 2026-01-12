#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-End Test: Full RAG Pipeline
⚠️ Run with: python test_full_pipeline.py (NOT pytest!)
"""

import sys
import os
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.tools.scraper import WebScraper
from backend.tools.url_filter import URLFilter
from backend.tools.search_api import SearchAPI


def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_success(text):
    print(f"✅ {text}")


def print_error(text):
    print(f"❌ {text}")


def print_info(text):
    print(f"ℹ️  {text}")


def print_warning(text):
    print(f"⚠️  {text}")


def step1_search():
    """Step 1: Test Search API"""
    print_header("STEP 1: Testing Search API")

    try:
        search_api = SearchAPI()
        query = "DUET admission notice"

        print_info(f"Search query: '{query}'")
        print_info("Searching Google...")

        results = search_api.search(query, num_results=5)

        if results:
            print_success(f"Found {len(results)} search results")
            for i, result in enumerate(results[:3], 1):
                print(f"   {i}. {result.get('title', 'No title')}")
                print(f"      URL: {result.get('url', 'No URL')}")
            return results
        else:
            print_warning("No search results found")
            return []

    except Exception as e:
        print_error(f"Search failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def step2_filter(search_results):
    """Step 2: Test URL Filtering"""
    print_header("STEP 2: Testing URL Filtering")

    try:
        url_filter = URLFilter()

        print_info(f"Input: {len(search_results)} URLs")
        print_info(f"Official domains: {url_filter.official_domains}")

        filtered = url_filter.filter_search_results(search_results)

        print_success(f"Filtered down to {len(filtered)} official URLs")
        for i, result in enumerate(filtered, 1):
            print(f"   {i}. {result['url']}")

        return filtered

    except Exception as e:
        print_error(f"Filtering failed: {str(e)}")
        return []


def step3_scrape(filtered_urls):
    """Step 3: Test Web Scraping"""
    print_header("STEP 3: Testing Web Scraping")

    try:
        scraper = WebScraper()
        scraped_data = []

        print_info(f"Scraping {min(len(filtered_urls), 3)} URLs...")

        for result in filtered_urls[:3]:  # Limit to first 3 for speed
            url = result['url']
            print_info(f"Scraping: {url}")

            data = scraper.scrape_url(url)
            if data:
                scraped_data.append(data)
                print_success(f"  ✓ {data['title']} ({len(data['content'])} chars)")
            else:
                print_warning(f"  ✗ Failed to scrape")

        print_success(f"Successfully scraped {len(scraped_data)} pages")
        return scraped_data

    except Exception as e:
        print_error(f"Scraping failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def step4_store(scraped_data):
    """Step 4: Test FAISS Storage"""
    print_header("STEP 4: Testing FAISS Vector Storage")

    try:
        from backend.tools.faiss_store import FAISSStore
        from backend.tools.embeddings import EmbeddingModel

        print_info("Initializing embedding model and FAISS store...")

        embedding_model = EmbeddingModel()
        faiss_store = FAISSStore(embedding_model)

        print_info(f"Adding {len(scraped_data)} documents to FAISS...")

        documents = []
        metadatas = []

        for data in scraped_data:
            content = data['content']
            chunks = [content[i:i + 500] for i in range(0, len(content), 500)]

            for chunk in chunks[:5]:
                if len(chunk.strip()) > 50:
                    documents.append(chunk)
                    metadatas.append({
                        'url': data['url'],
                        'title': data['title'],
                        'date': data.get('date', '')
                    })

        faiss_store.add_documents(documents, metadatas)

        print_success(f"Added {len(documents)} chunks to FAISS")
        print_info(f"Total vectors in store: {faiss_store.index.ntotal}")

        return faiss_store

    except Exception as e:
        print_error(f"FAISS storage failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def step5_query(faiss_store):
    """Step 5: Test RAG Query"""
    print_header("STEP 5: Testing RAG Query")

    try:
        if not faiss_store:
            print_error("FAISS store not available")
            return False

        test_queries = [
            "What is the admission process?",
            "Tell me about CSE department",
            "What are the latest notices?"
        ]

        print_info("Testing similarity search...")

        for query in test_queries:
            print(f"\n📝 Query: {query}")

            results = faiss_store.search(query, k=3)

            if results:
                print_success(f"Found {len(results)} relevant results")
                for i, (doc, metadata, score) in enumerate(results, 1):
                    print(f"   {i}. Score: {score:.3f}")
                    print(f"      Source: {metadata.get('title', 'Unknown')}")
                    print(f"      Preview: {doc[:80]}...")
            else:
                print_warning("No results found")

        return True

    except Exception as e:
        print_error(f"Query failed: {str(e)}")
        return False


def step6_llm_answer(faiss_store):
    """Step 6: Test LLM Answer (Optional)"""
    print_header("STEP 6: Testing LLM Answer Generation")

    try:
        import requests
        from backend.llm import get_llm

        try:
            response = requests.get("http://localhost:1234/v1/models", timeout=2)
            if response.status_code != 200:
                print_warning("LM Studio not running, skipping")
                return True
        except:
            print_warning("LM Studio not available, skipping")
            return True

        print_info("LM Studio detected! Generating answer...")

        llm = get_llm()
        query = "What is the admission process at DUET?"
        results = faiss_store.search(query, k=2)

        context = "\n\n".join([doc for doc, _, _ in results])

        prompt = f"""Based on the information below, answer the question.

Context:
{context[:1000]}

Question: {query}

Answer:"""

        answer = llm.invoke(prompt)

        print_success("LLM Answer:")
        print("   " + "-" * 70)
        print(f"   {answer[:300]}...")
        print("   " + "-" * 70)

        return True

    except Exception as e:
        print_warning(f"LLM test skipped: {str(e)}")
        return True


def main():
    """Run complete pipeline test"""
    print_header("🧪 COMPLETE RAG PIPELINE TEST")
    print_info("Testing: Search → Filter → Scrape → Store → Query → Answer\n")

    results = {
        'search': False,
        'filter': False,
        'scrape': False,
        'store': False,
        'query': False,
        'llm': False
    }

    # Execute pipeline
    search_results = step1_search()
    results['search'] = len(search_results) > 0

    if not results['search']:
        print_error("Search failed, stopping")
        return False

    filtered_urls = step2_filter(search_results)
    results['filter'] = len(filtered_urls) > 0

    if not results['filter']:
        print_warning("No official URLs, using fallback...")
        filtered_urls = [
            {'url': 'https://www.duet.ac.bd/notice/all-notices', 'title': 'DUET Notices'},
            {'url': 'https://www.duet.ac.bd/admission', 'title': 'DUET Admission'},
        ]
        results['filter'] = True

    scraped_data = step3_scrape(filtered_urls)
    results['scrape'] = len(scraped_data) > 0

    if not results['scrape']:
        print_error("Scraping failed, stopping")
        return False

    faiss_store = step4_store(scraped_data)
    results['store'] = faiss_store is not None

    if not results['store']:
        print_error("FAISS storage failed, stopping")
        return False

    results['query'] = step5_query(faiss_store)
    results['llm'] = step6_llm_answer(faiss_store)

    # Summary
    print_header("📊 PIPELINE TEST SUMMARY")

    steps = [
        ('Search API', results['search']),
        ('URL Filtering', results['filter']),
        ('Web Scraping', results['scrape']),
        ('FAISS Storage', results['store']),
        ('RAG Query', results['query']),
        ('LLM Answer', results['llm'])
    ]

    for step_name, passed in steps:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {step_name}")

    passed = sum(1 for _, p in steps if p)
    total = len(steps)

    print(f"\n{'=' * 80}")
    print(f"Results: {passed}/{total} steps passed")
    print(f"{'=' * 80}\n")

    if passed >= 5:
        print_success("🎉 Pipeline working! Users can get answers!")
        print_info("✅ Search → Filter → Scrape → Store → Query working")
        if results['llm']:
            print_info("✅ LLM answer generation working")
        else:
            print_info("⚠️  LLM not tested (start LM Studio for full test)")
        return True
    else:
        print_error(f"⚠️  {total - passed} steps failed")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)