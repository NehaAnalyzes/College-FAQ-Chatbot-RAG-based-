import streamlit as st
from rag_engine import RAGChatbot

# ========================================
# ADD YOUR GEMINI API KEY HERE
# ========================================
API_KEY = st.secrets["GEMINI_API_KEY"]

# ========================================

# Page configuration
st.set_page_config(
    page_title="College Chatbot",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS - Bigger heading and cleaner layout
st.markdown("""
<style>
    .main-header {
        font-size: 4rem !important;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem !important;
        font-weight: bold !important;
        line-height: 1.2 !important;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem !important;
    }
    .chat-container {
        max-width: 100% !important;
        margin: 0 auto !important;
    }
    .sidebar-header {
        font-size: 1.8rem !important;
        color: #1f77b4 !important;
    }
    .sidebar-text {
        font-size: 0.9rem !important;
    }
    .footer {
        text-align: center;
        color: #888;
        font-size: 0.8rem;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Header - Bigger and cleaner
st.markdown('<h1 class="main-header">🎓 College Chatbot</h1>', unsafe_allow_html=True)

# Initialize chatbot (cached so it only loads once)
@st.cache_resource
def load_chatbot():
    return RAGChatbot(API_KEY)

# ========================================
# INITIALIZE SESSION STATE FIRST
# ========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add welcome message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! 👋 Welcome to our college! I'm an AI assistant. I can help you with information about admissions, courses, fees, facilities, placements, and more. How can I assist you today?"
    })
# ========================================

# Main content area with bigger chat interface
col1, col2 = st.columns([3, 1])

with col1:
    # Display chat history in main area
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input in main area
    if prompt := st.chat_input("Ask me anything about the college..."):
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate bot response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    # Load chatbot
                    chatbot = load_chatbot()
                    
                    # Get response using RAG
                    response = chatbot.chat(prompt)
                    
                    # Display response
                    st.markdown(response)
                    
                    # Add to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}\n\nPlease check your API key is correct."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    st.markdown('</div>', unsafe_allow_html=True)

# Simple sidebar (only contact info and examples)
with col2:
    # Simplified sidebar
    st.markdown("""
    <div style="position: fixed; width: 250px; height: 100vh; overflow-y: auto;">
    """, unsafe_allow_html=True)
    
    st.markdown('<h3 class="sidebar-header">📞 Contact</h3>', unsafe_allow_html=True)
    st.info("""
    **Phone**: 1800-XXX-1234  
    **Email**: admissions@college.edu  
    **Website**: www.college.edu
    """)
    
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    
    st.markdown('<h4 style="color: #1f77b4; font-size: 1.2rem;">💡 Quick Questions</h4>', unsafe_allow_html=True)
    
    # Example questions as buttons (click to ask)
    if st.button("🎯 Admission Requirements", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "What are the admission requirements?"})
        st.rerun()
    
    if st.button("📖 Available Courses", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "What courses do you offer?"})
        st.rerun()
    
    if st.button("💰 Fees & Scholarships", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "How much is the tuition fee for B.Tech?"})
        st.rerun()
    
    if st.button("🏛️ Campus Facilities", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "What facilities does the campus have?"})
        st.rerun()
    
    if st.button("💼 Placements", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Tell me about placement records"})
        st.rerun()
    
    st.markdown('<div class="footer" style="position: absolute; bottom: 20px; width: 100%;">AI Chatbot | Capstone Project</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Remove the example questions expander since we have buttons now
# Footer at bottom
st.markdown('<div class="footer">AI-Powered College Chatbot | Capstone Project</div>', unsafe_allow_html=True)
