import streamlit as st
import sqlite3
from groq import Groq
from datetime import datetime

# ================================
# YOUR API KEY
# ================================
API_KEY = " "

# ================================
# PAGE SETTINGS
# This configures the browser tab and layout
# ================================
st.set_page_config(
    page_title="TechStore AI Assistant",
    page_icon="🤖",
    layout="centered"
)

# ================================
# CUSTOM CSS - This makes it look beautiful
# This is regular CSS that styles our app
# ================================
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #1a1a2e;
    }
    
    /* Chat message styling */
    .user-message {
        background-color: #0f3460;
        color: #e2e8f0;
        padding: 12px 16px;
        border-radius: 12px 0px 12px 12px;
        margin: 8px 0;
        margin-left: 20%;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .bot-message {
        background-color: #16213e;
        color: #cbd5e1;
        padding: 12px 16px;
        border-radius: 0px 12px 12px 12px;
        margin: 8px 0;
        margin-right: 20%;
        font-size: 14px;
        line-height: 1.5;
        border-left: 3px solid #3b82f6;
    }
    
    /* Header */
    .header {
        background-color: #16213e;
        padding: 16px 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 0.5px solid rgba(255,255,255,0.1);
        display: flex;
        align-items: center;
    }
    
    .online-badge {
        color: #4ade80;
        font-size: 12px;
    }
    
    /* Input box */
    .stTextInput input {
        background-color: #16213e !important;
        color: #e2e8f0 !important;
        border: 0.5px solid #334155 !important;
        border-radius: 20px !important;
        padding: 10px 16px !important;
    }
    
    /* Button */
    .stButton button {
        background-color: #3b82f6 !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 8px 24px !important;
        font-weight: 500 !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #16213e !important;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================================
# DATABASE FUNCTIONS
# Same as before - saves conversations
# ================================
def init_db():
    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_message(role, message):
    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (role, message, timestamp) VALUES (?, ?, ?)",
        (role, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def load_history():
    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role, message, timestamp FROM conversations ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

# ================================
# BUSINESS INFO
# ================================
BUSINESS_INFO = """
You are a helpful assistant for a business called "TechStore Pakistan".
Products:
- Laptop: Rs. 80,000 (Core i5, 8GB RAM, 256GB SSD)
- Gaming PC: Rs. 150,000 (Core i7, 16GB RAM, 1TB SSD)
- Mouse: Rs. 1,500
- Keyboard: Rs. 2,500
- Headphones: Rs. 3,000
Services:
- Free delivery in Islamabad and Rawalpindi
- 7 day return policy
- 1 year warranty on all products
Working Hours: Monday to Saturday, 10am to 8pm
Location: Blue Area, Islamabad
Contact: 0300-1234567
Always be polite and helpful.
"""

# ================================
# AI FUNCTION
# ================================
client = Groq(api_key=API_KEY)

def get_ai_response(message, chat_history):
    messages = [{"role": "system", "content": BUSINESS_INFO}]
    for human_msg, ai_msg in chat_history:
        messages.append({"role": "user", "content": human_msg})
        messages.append({"role": "assistant", "content": ai_msg})
    messages.append({"role": "user", "content": message})
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content

# ================================
# INITIALIZE
# ================================
init_db()

# Session state keeps chat history while app is running
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ================================
# UI LAYOUT
# ================================

# Header
st.markdown("""
<div class="header">
    <span style="font-size:24px; margin-right:12px">🤖</span>
    <div>
        <div style="color:#e2e8f0; font-weight:500; font-size:16px">TechStore AI Assistant</div>
        <div class="online-badge">● Online</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["💬 Chat", "📋 History"])

with tab1:
    # Display chat messages
    for human_msg, ai_msg in st.session_state.chat_history:
        st.markdown(f'<div class="user-message">👤 {human_msg}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bot-message">🤖 {ai_msg}</div>', unsafe_allow_html=True)
    
    # Input area
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "message",
            placeholder="Ask about products, prices, delivery...",
            label_visibility="collapsed",
            key="user_input"
        )
    
    with col2:
        send_clicked = st.button("Send ➤")
    
    # Handle message
    if send_clicked and user_input:
        with st.spinner("Thinking..."):
            response = get_ai_response(user_input, st.session_state.chat_history)
            st.session_state.chat_history.append((user_input, response))
            save_message("user", user_input)
            save_message("assistant", response)
        st.rerun()
    
    # Clear button
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

with tab2:
    st.markdown("<h3 style='color:#e2e8f0'>Conversation History</h3>", unsafe_allow_html=True)
    
    if st.button("Load History"):
        rows = load_history()
        if not rows:
            st.info("No history yet.")
        else:
            for role, message, timestamp in rows:
                if role == "user":
                    st.markdown(f'<div class="user-message">👤 [{timestamp}] {message}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bot-message">🤖 [{timestamp}] {message}</div>', unsafe_allow_html=True)