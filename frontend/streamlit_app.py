import streamlit as st
import requests
import json
from datetime import datetime
import time
import os
import logging

logger = logging.getLogger(__name__)

# Page Configuration
st.set_page_config(
    page_title="🎓 University AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_URL = "http://127.0.0.1:8000"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

css_path = os.path.join(BASE_DIR, "style.css")

with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'api_status' not in st.session_state:
    st.session_state.api_status = 'unknown'

# Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🎓 University AI Assistant</h1>
    <p class="header-subtitle">আপনার প্রশ্ন করুন | Ask your questions</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📚 Quick Guide")

    st.markdown("#### Example Questions:")
    example_questions = {
        "🔔 Notice": [
            "আজকের নোটিশ কী?",
            "পরীক্ষার সময়সূচী কী?",
            "ফর্ম জমা দেওয়ার শেষ তারিখ কবে?"
        ],
        "👨‍🏫 Faculty": [
            "CSE বিভাগের শিক্ষক তালিকা",
            "Dr. Rahman এর যোগাযোগ নম্বর",
            "Faculty office hours"
        ],
        "📖 Library": [
            "লাইব্রেরির সময় কী?",
            "Library booking system",
            "New books this month"
        ]
    }

    for category, questions in example_questions.items():
        with st.expander(category):
            for q in questions:
                if st.button(q, key=f"example_{q}"):
                    st.session_state.user_input = q
                    st.rerun()

    st.markdown("---")

    # Language Selection
    language = st.selectbox(
        "🌐 Language / ভাষা",
        ["Bengali (বাংলা)", "English"],
        index=0
    )
    lang_code = "bn" if "Bengali" in language else "en"

    st.markdown("---")

    # Clear Chat
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # API Status (with better error handling and ETA)
    st.markdown("### 📡 System Status")
    try:
        start_check = time.time()
        response = requests.get(f"{API_URL}/health", timeout=60)
        check_time = time.time() - start_check
        
        if response.status_code == 200:
            data = response.json()
            if check_time > 2:
                st.markdown('<span class="status-badge status-success">✅ API Online (Slow)</span>', unsafe_allow_html=True)
                st.caption(f"Response time: {check_time:.2f}s")
            else:
                st.markdown('<span class="status-badge status-success">✅ API Online</span>', unsafe_allow_html=True)

            # Show stats
            faiss_stats = data.get('faiss_stats', {})
            st.metric("📊 Documents", faiss_stats.get('total_documents', 0))
            st.session_state.api_status = 'online'
        else:
            st.markdown('<span class="status-badge status-error">❌ API Error</span>', unsafe_allow_html=True)
            st.session_state.api_status = 'error'
    except requests.exceptions.Timeout:
        st.markdown('<span class="status-badge status-error">⏱️ API Slow</span>', unsafe_allow_html=True)
        st.caption("Health check timeout (>3s). API may be processing a request.")
        st.info("💡 **Tip**: If you just sent a query, wait for it to complete. First query may take 30-60s (model loading).")
        st.session_state.api_status = 'slow'
    except requests.exceptions.ConnectionError:
        st.markdown('<span class="status-badge status-error">❌ API Offline</span>', unsafe_allow_html=True)
        st.caption("Cannot connect to backend server.")
        st.info("💡 **Solution**: Make sure backend is running on http://127.0.0.1:8000")
        st.session_state.api_status = 'offline'
    except Exception as e:
        st.markdown('<span class="status-badge status-error">❌ API Error</span>', unsafe_allow_html=True)
        st.session_state.api_status = 'error'

    st.markdown("---")
    st.markdown("**Powered by:**")
    st.markdown("- CrewAI")
    st.markdown("- FastAPI")
    st.markdown("- LM Studio")
    st.markdown("- FAISS")

# Main Chat Interface
st.markdown("### 💬 Chat Interface")

# Display chat messages
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class='chat-message user-message'>
                <div class='message-header'>
                    👤 আপনি (You)
                </div>
                <div class='message-body'>
                    {message['content']}
                </div>
                <div class='message-meta'>
                    🕐 {message.get('timestamp', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='chat-message bot-message'>
                <div class='message-header'>
                    🤖 AI Assistant
                    {f"<span class='status-badge status-success'>{message.get('agent', '')}</span>" if message.get('agent') else ''}
                </div>
                <div class='message-body'>
                    {message['content']}
                </div>
                <div class='message-meta'>
                    🕐 {message.get('timestamp', '')} | 
                    ⚡ {message.get('processing_time', 'N/A')} | 
                    📄 {message.get('source', 'N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Input area - Fixed layout
st.markdown("---")
input_container = st.container()

with input_container:
    col1, col2 = st.columns([10, 2])
    
    with col1:
        user_input = st.text_input(
            "Type your question here / এখানে আপনার প্রশ্ন লিখুন",
            key="user_input_field",
            placeholder="উদাহরণ: আজকের নোটিশ কী? | Example: What's today's notice?",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Align button vertically
        send_button = st.button("📤 Send", type="primary", use_container_width=True)

# Process query
if send_button and user_input:
    if st.session_state.api_status == 'offline':
        st.error("❌ API is offline. Please start the backend server.")
    else:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

        # Show loading with progress and ETA
        progress_container = st.container()
        with progress_container:
            status_text = st.empty()
            progress_bar = st.progress(0)
            eta_text = st.empty()
            time_text = st.empty()
        
        try:
            # Call API with progress updates
            start_time = time.time()
            status_text.info("🔍 Initializing query processing...")
            progress_bar.progress(10)
            
            # Show initial ETA based on query type
            estimated_time = 120  # Default estimate
            if any(word in user_input.lower() for word in ['notice', 'নোটিশ', 'exam', 'পরীক্ষা']):
                estimated_time = 30
            elif any(word in user_input.lower() for word in ['faculty', 'teacher', 'শিক্ষক']):
                estimated_time = 90
            else:
                estimated_time = 300
            
            eta_text.caption(f"⏱️ Estimated time: {estimated_time}s (first query may take 60s for model loading)")
            
            # Make request
            response = requests.post(
                f"{API_URL}/query",
                json={"query": user_input, "language": lang_code},
                timeout=500
            )
            
            processing_time = time.time() - start_time
            progress_bar.progress(100)
            status_text.success("✅ Query completed!")
            eta_text.empty()
            time_text.empty()
            
            # Process response
            if response.status_code == 200:
                result = response.json()

                # Add bot message
                st.session_state.messages.append({
                    "role": "bot",
                    "content": result.get("answer", "No response"),
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "agent": result.get("agent", "unknown"),
                    "source": result.get("source", "unknown"),
                    "processing_time": f"{processing_time:.2f}s"
                })

                # Show success with timing info
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.success("✅ Answer generated successfully!")
                with col2:
                    st.metric("⏱️ Time", f"{processing_time:.1f}s")
                
                # Clear progress indicators
                progress_container.empty()

            else:
                progress_container.empty()
                st.error(f"❌ API Error: {response.status_code}")

        except requests.exceptions.Timeout:
            progress_container.empty()
            elapsed = time.time() - start_time if 'start_time' in locals() else 0
            st.error(f"⏱️ Request timeout after {elapsed:.1f}s (max 200s).")
            st.markdown("**Possible reasons:**")
            st.markdown("- First query is loading models (30-60s)")
            st.markdown("- Complex query requiring extensive processing")
            st.markdown("- LM Studio is slow or not responding")
            st.markdown("**Solutions:**")
            st.markdown("- Wait a bit longer for first query")
            st.markdown("- Try a simpler question")
            st.markdown("- Check LM Studio is running properly")
        except requests.exceptions.ConnectionError:
            progress_container.empty()
            st.error("❌ Cannot connect to API. Please check if backend server is running.")
            st.info("💡 **Backend should be running on http://127.0.0.1:8000**")
            st.info("Run: `cd backend && python app.py`")
        except Exception as e:
            progress_container.empty()
            st.error(f"❌ Error: {str(e)}")
            if hasattr(logger, 'error'):
                logger.error(f"Frontend error: {str(e)}")

        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p style='margin: 0;'>
        <strong>🎓 University AI Assistant v2.0</strong>
    </p>
    <p style='margin: 0.5rem 0; font-size: 0.9rem;'>
        Powered by AI • Built with ❤️ for Students
    </p>
    <p style='margin: 0; font-size: 0.8rem; opacity: 0.7;'>
        CrewAI | FastAPI | LM Studio | FAISS | Streamlit
    </p>
</div>
""", unsafe_allow_html=True)

# streamlit run .\frontend\streamlit_app.py