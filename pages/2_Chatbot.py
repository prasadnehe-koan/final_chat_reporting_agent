
import streamlit as st
import requests
import json
from datetime import datetime
import uuid
import sqlite3
from contextlib import contextmanager
from auth import require_authentication, logout_user

# ==========================================================
# AUTHENTICATION CHECK
# ==========================================================
user_id, username = require_authentication()

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Chat with AI about your procurement data",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# CONFIGURATION
# ==========================================================
DATABRICKS_INSTANCE = st.secrets.get('DATABRICKS_INSTANCE')
DATABRICKS_TOKEN = st.secrets.get('DB_token')
NOTEBOOK_PATH = st.secrets.get('NOTEBOOK_PATH')
VOLUME_PATH = st.secrets.get('VOLUME_PATH')
CLUSTER_ID = st.secrets.get('CLUSTER_ID')
CHATBOT_ENDPOINT=st.secrets.get('CHATBOT_ENDPOINT')

# SQLite database file
DB_FILE = "app_database.db"

# ==========================================================
# DATABASE FUNCTIONS
# ==========================================================
@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def initialize_database():
    """Create tables if they don't exist and handle migrations"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create user_chats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_chats (
                chat_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_current INTEGER DEFAULT 0,
                last_accessed TEXT
            )
        """)
        
        # Create user_messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (chat_id) REFERENCES user_chats(chat_id)
            )
        """)
        
        # Migration: Add last_accessed column if it doesn't exist
        try:
            cursor.execute("SELECT last_accessed FROM user_chats LIMIT 1")
        except sqlite3.OperationalError:
            # Column doesn't exist, add it
            print("Adding last_accessed column to user_chats table...")
            cursor.execute("""
                ALTER TABLE user_chats 
                ADD COLUMN last_accessed TEXT
            """)
            # Set default value for existing rows
            cursor.execute("""
                UPDATE user_chats 
                SET last_accessed = created_at 
                WHERE last_accessed IS NULL
            """)
            conn.commit()
            print("Migration completed successfully!")
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_chats_user_id 
            ON user_chats(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_messages_chat_user 
            ON user_messages(chat_id, user_id)
        """)
        
        conn.commit()

# Initialize database on startup
initialize_database()

def save_chat_to_db(user_id, chat_id, title, created_at, is_current=False):
    """Save or update a chat in the database for specific user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # If this is the current chat, unset all others for this user
        if is_current:
            cursor.execute(
                "UPDATE user_chats SET is_current = 0 WHERE user_id = ?", 
                (user_id,)
            )
        
        # Update last_accessed timestamp
        last_accessed = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_chats 
            (chat_id, user_id, title, created_at, is_current, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chat_id, user_id, title, created_at.isoformat(), 1 if is_current else 0, last_accessed))
        
        conn.commit()

def save_message_to_db(user_id, chat_id, role, content):
    """Save a message to the database for specific user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_messages (chat_id, user_id, role, content, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (chat_id, user_id, role, content, datetime.now().isoformat()))
        
        # Update last_accessed for this chat
        cursor.execute("""
            UPDATE user_chats 
            SET last_accessed = ? 
            WHERE chat_id = ? AND user_id = ?
        """, (datetime.now().isoformat(), chat_id, user_id))
        
        conn.commit()

def load_chats_from_db(user_id):
    """Load all chats for specific user from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM user_chats WHERE user_id = ? ORDER BY created_at DESC", 
            (user_id,)
        )
        rows = cursor.fetchall()
        
        chats = {}
        current_chat_id = None
        
        for row in rows:
            chat_id = row['chat_id']
            chats[chat_id] = {
                'title': row['title'],
                'created_at': datetime.fromisoformat(row['created_at']),
                'messages': []
            }
            
            # The chat marked as is_current is the one user was viewing
            if row['is_current']:
                current_chat_id = chat_id
        
        return chats, current_chat_id

def load_messages_for_chat(user_id, chat_id):
    """Load all messages for a specific chat and user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, content FROM user_messages 
            WHERE chat_id = ? AND user_id = ?
            ORDER BY message_id ASC
        """, (chat_id, user_id))
        rows = cursor.fetchall()
        
        return [{'role': row['role'], 'content': row['content']} for row in rows]

def delete_chat_from_db(user_id, chat_id):
    """Delete a chat and all its messages for specific user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM user_messages WHERE chat_id = ? AND user_id = ?", 
            (chat_id, user_id)
        )
        cursor.execute(
            "DELETE FROM user_chats WHERE chat_id = ? AND user_id = ?", 
            (chat_id, user_id)
        )
        conn.commit()

def clear_chat_messages_db(user_id, chat_id):
    """Clear all messages for a specific chat and user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM user_messages WHERE chat_id = ? AND user_id = ?", 
            (chat_id, user_id)
        )
        conn.commit()

def clear_all_data_db(user_id):
    """Clear all chats and messages for specific user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_messages WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM user_chats WHERE user_id = ?", (user_id,))
        conn.commit()

def set_current_chat_db(user_id, chat_id):
    """Set a chat as the current active chat for specific user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Unset all current chats for this user
        cursor.execute("UPDATE user_chats SET is_current = 0 WHERE user_id = ?", (user_id,))
        # Set the new current chat
        cursor.execute(
            "UPDATE user_chats SET is_current = 1, last_accessed = ? WHERE chat_id = ? AND user_id = ?", 
            (datetime.now().isoformat(), chat_id, user_id)
        )
        conn.commit()

def get_chat_message_count(user_id, chat_id):
    """Get the number of messages in a chat"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as count FROM user_messages 
            WHERE chat_id = ? AND user_id = ?
        """, (chat_id, user_id))
        result = cursor.fetchone()
        return result['count'] if result else 0

# ==========================================================
# INITIALIZE SESSION STATE WITH FULL PERSISTENCE
# ==========================================================
# Track current user to detect user changes
if 'current_user_id' not in st.session_state or st.session_state.current_user_id != user_id:
    # User has changed - clear all session state
    keys_to_clear = [k for k in st.session_state.keys() if k.startswith('chats_') or 
                     k in ['current_chat_id', 'awaiting_response', 'editing_chat_id', 'show_confirm']]
    for key in keys_to_clear:
        del st.session_state[key]
    st.session_state.current_user_id = user_id

session_key = f'chats_{user_id}'

# Load user's data from database if not in session
if session_key not in st.session_state:
    loaded_chats, loaded_chat_id = load_chats_from_db(user_id)
    
    if loaded_chats:
        # Load messages for each chat to maintain full context
        for chat_id in loaded_chats.keys():
            loaded_chats[chat_id]['messages'] = load_messages_for_chat(user_id, chat_id)
        
        st.session_state[session_key] = loaded_chats
        
        # Restore the exact chat user was viewing before logout
        if loaded_chat_id:
            st.session_state.current_chat_id = loaded_chat_id
        else:
            # Fallback to most recent chat
            st.session_state.current_chat_id = list(loaded_chats.keys())[0]
            set_current_chat_db(user_id, st.session_state.current_chat_id)
    else:
        # First time user - create initial chat
        initial_id = str(uuid.uuid4())
        st.session_state[session_key] = {
            initial_id: {
                "title": "New Chat",
                "messages": [],
                "created_at": datetime.now()
            }
        }
        st.session_state.current_chat_id = initial_id
        save_chat_to_db(user_id, initial_id, "New Chat", datetime.now(), is_current=True)

if 'awaiting_response' not in st.session_state:
    st.session_state.awaiting_response = False

if 'editing_chat_id' not in st.session_state:
    st.session_state.editing_chat_id = None

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def get_current_chat():
    """Get the current active chat"""
    chat = st.session_state[session_key].get(st.session_state.current_chat_id)
    if not chat:
        # Fallback - should not happen, but handle gracefully
        return {
            "title": "New Chat",
            "messages": [],
            "created_at": datetime.now()
        }
    return chat

def create_new_chat():
    """Create a new chat session"""
    new_id = str(uuid.uuid4())
    st.session_state[session_key][new_id] = {
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.now()
    }
    st.session_state.current_chat_id = new_id
    st.session_state.awaiting_response = False
    save_chat_to_db(user_id, new_id, "New Chat", datetime.now(), is_current=True)

def delete_chat(chat_id):
    """Delete a chat session"""
    if chat_id in st.session_state[session_key]:
        del st.session_state[session_key][chat_id]
        delete_chat_from_db(user_id, chat_id)
        
        # If deleting current chat, switch to another or create new
        if chat_id == st.session_state.current_chat_id:
            if st.session_state[session_key]:
                new_current = list(st.session_state[session_key].keys())[0]
                st.session_state.current_chat_id = new_current
                set_current_chat_db(user_id, new_current)
            else:
                create_new_chat()

def switch_chat(chat_id):
    """Switch to a different chat - maintains separate context per chat"""
    old_chat_id = st.session_state.current_chat_id
    st.session_state.current_chat_id = chat_id
    st.session_state.awaiting_response = False
    
    # Mark this chat as current in DB so it's restored on next login
    set_current_chat_db(user_id, chat_id)
    
    # Debug logging
    print(f"[Context Switch] User {user_id}: {old_chat_id} → {chat_id}")

def update_chat_title(chat_id, first_message):
    """Auto-generate chat title from first user message"""
    title = first_message[:50] + ("..." if len(first_message) > 50 else "")
    st.session_state[session_key][chat_id]["title"] = title
    save_chat_to_db(
        user_id,
        chat_id, 
        title, 
        st.session_state[session_key][chat_id]["created_at"],
        is_current=(chat_id == st.session_state.current_chat_id)
    )

def rename_chat(chat_id, new_title):
    """Rename a chat session"""
    if new_title and new_title.strip():
        st.session_state[session_key][chat_id]["title"] = new_title.strip()
        save_chat_to_db(
            user_id,
            chat_id,
            new_title.strip(),
            st.session_state[session_key][chat_id]["created_at"],
            is_current=(chat_id == st.session_state.current_chat_id)
        )

def chat_with_bot(conversation_history, chat_id):
    """Send ONLY current chat's conversation history to chatbot
    
    Args:
        conversation_history: List of messages from CURRENT chat only
        chat_id: ID of the current active chat for logging/debugging
    
    Returns:
        Bot response string
    """
    if not DATABRICKS_TOKEN or not CHATBOT_ENDPOINT:
        return "⚠️ Error: Chatbot is not configured. Please contact your administrator."
    
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Build input array from CURRENT chat's conversation history ONLY
    input_messages = []
    for msg in conversation_history:
        input_messages.append({
            "status": None,
            "content": msg["content"],
            "role": msg["role"],
            "type": "message"
        })

    payload = {
        "input": input_messages
    }
    
    # Debug logging (optional - can remove in production)
    print(f"[Chat: {chat_id}] Sending {len(input_messages)} messages to chatbot")

    try:
        response = requests.post(CHATBOT_ENDPOINT, headers=headers, json=payload, timeout=300)
        if response.status_code != 200:
            return f"❌ Error: {response.status_code} - {response.text}"

        texts = []
        raw = response.text.strip()
        
        # Handle NDJSON
        if '\n' in raw:
            for line in raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if data.get("type") == "response.output_item.done":
                        item = data.get("item", {})
                        for content in item.get("content", []):
                            if content.get("type") == "output_text":
                                texts.append(content.get("text", ""))
                except json.JSONDecodeError:
                    continue
        else:
            try:
                data = json.loads(raw)
                if isinstance(data, dict) and "output" in data:
                    for msg in data["output"]:
                        for content in msg.get("content", []):
                            if content.get("type") == "output_text":
                                texts.append(content.get("text", ""))
            except Exception:
                pass

        result = "\n\n---\n\n".join(texts) if texts else "⚠️ No response received from chatbot."
        return result

    except requests.exceptions.Timeout:
        return "⏱️ Error: Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "🔌 Error: Cannot connect to chatbot service. Please check your connection."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==========================================================
# STYLING
# ==========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .user-info-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding: 0.75rem 1rem;
        background: rgba(102,126,234,0.1);
        border: 1px solid #667eea;
        border-radius: 8px;
    }
    
    .user-info {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
        color: #667eea;
        font-weight: 600;
    }
    
    .sidebar-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: var(--text-color);
    }
    
    .stChatMessage {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.75rem;
    }
    
    .stButton button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        text-align: left !important;
    }
    
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Active chat styling - more prominent */
    .stButton button:disabled {
        opacity: 1 !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: 2px solid #667eea !important;
    }
    
    [data-testid="stSidebar"] .stButton button {
        font-size: 0.85rem !important;
    }
    
    [data-testid="stSidebar"] [data-testid="column"] {
        padding: 0 0.15rem !important;
    }
    
    .chat-context-info {
        background: rgba(102, 126, 234, 0.05);
        border-left: 3px solid #667eea;
        padding: 0.5rem 1rem;
        margin-bottom: 1rem;
        border-radius: 4px;
        font-size: 0.85rem;
        color: var(--text-color);
    }
    
    .header-logo {
        height: 100%;
        max-height: 80px;
        width: auto;
        object-fit: contain;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# USER INFO BAR
# ==========================================================
col1, col2 = st.columns([6, 1])
with col1:
    current_chat = get_current_chat()
    st.markdown(f"""
    <div class="user-info">
        👤 Logged in as: <strong>{username}</strong>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("🚪 Logout", key="logout_btn", type="secondary", use_container_width=True):
        # Save current state before logout
        set_current_chat_db(user_id, st.session_state.current_chat_id)
        # Clear session state
        keys_to_clear = list(st.session_state.keys())
        for key in keys_to_clear:
            del st.session_state[key]
        logout_user()
        st.switch_page("Login.py")

# ==========================================================
# SIDEBAR - CHAT HISTORY
# ==========================================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">💬 Chat History</div>', unsafe_allow_html=True)
    
    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        create_new_chat()
        st.rerun()
    
    st.markdown("---")
    
    # Display all chats
    sorted_chats = sorted(
        st.session_state[session_key].items(), 
        key=lambda x: x[1]["created_at"], 
        reverse=True
    )
    
    for chat_id, chat_data in sorted_chats:
        is_active = chat_id == st.session_state.current_chat_id
        
        if st.session_state.editing_chat_id == chat_id:
            col1, col2 = st.columns([4, 1])
            with col1:
                with st.form(key=f"form_{chat_id}", clear_on_submit=False):
                    new_title = st.text_input(
                        "Rename",
                        value=chat_data['title'],
                        key=f"rename_{chat_id}",
                        label_visibility="collapsed"
                    )
                    submitted = st.form_submit_button("💾", use_container_width=True)
                    
                    if submitted:
                        rename_chat(chat_id, new_title)
                        st.session_state.editing_chat_id = None
                        st.rerun()
            
            with col2:
                if st.button("✕", key=f"cancel_{chat_id}", use_container_width=True):
                    st.session_state.editing_chat_id = None
                    st.rerun()
        else:
            col1, col2, col3 = st.columns([7, 1.2, 1.2])
            
            with col1:
                # Truncate title if too long
                max_title_length = 30
                display_title = chat_data['title']
                if len(display_title) > max_title_length:
                    display_title = display_title[:max_title_length] + "..."
                
                button_label = f"{'📌 ' if is_active else '💬 '}{display_title}"
                if st.button(button_label, key=f"chat_{chat_id}", use_container_width=True, disabled=is_active):
                    switch_chat(chat_id)
                    st.rerun()
            
            with col2:
                if st.button("✏️", key=f"edit_{chat_id}", use_container_width=True):
                    st.session_state.editing_chat_id = chat_id
                    st.rerun()
            
            with col3:
                if len(st.session_state[session_key]) > 1:
                    if st.button("🗑️", key=f"delete_{chat_id}", use_container_width=True):
                        if st.session_state.editing_chat_id == chat_id:
                            st.session_state.editing_chat_id = None
                        delete_chat(chat_id)
                        st.rerun()
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear All", use_container_width=True, type="secondary"):
            st.session_state.show_confirm = True
    
    if st.session_state.get('show_confirm', False):
        with col2:
            if st.button("✅ Confirm", use_container_width=True, type="primary"):
                st.session_state[session_key] = {}
                clear_all_data_db(user_id)
                create_new_chat()
                st.session_state.show_confirm = False
                st.rerun()
    
    st.markdown(f"""
    <div style="font-size: 0.75rem; color: var(--secondary-text-color); text-align: center; padding: 0.5rem; margin-top: 0.5rem;">
        👤 {username}
    </div>
    """, unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================
# Logo URL - Change this to your actual logo URL
LOGO_URL = "https://media.licdn.com/dms/image/v2/C4E0BAQGtXskL4EvJmA/company-logo_200_200/company-logo_200_200/0/1632401962756/koantek_logo?e=2147483647&v=beta&t=D4GLT1Pu2vvxLR1iKZZbUJWN7K_uaPSF0T1mZl6Le-o"

current_chat = get_current_chat()

st.markdown(f"""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.25rem 1.5rem; border-radius: 10px; margin-bottom: 1.25rem; display: flex; justify-content: space-between; align-items: center;">
    <div style="flex: 1;">
        <h1 style="color: white; font-size: 1.5rem; font-weight: 700; margin: 0;">💬 {current_chat['title']}</h1>
        <p style="color: rgba(255,255,255,0.95); font-size: 0.875rem; margin: 0.25rem 0 0 0;">Chat with AI about your procurement data</p>
    </div>
    <img src="{LOGO_URL}" class="header-logo" alt="Koantek Logo" onerror="this.style.display='none'">
</div>
""", unsafe_allow_html=True)

# ==========================================================
# CHATBOT UI
# ==========================================================
chat_container = st.container(height=500)

with chat_container:
    if not current_chat["messages"]:
        st.info("👋 Start a conversation by typing a message below!")
    else:
        for msg in current_chat["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    if st.session_state.awaiting_response:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # CRITICAL: Pass ONLY current chat's messages, not all user's messages
                current_chat_messages = current_chat["messages"]
                bot_response = chat_with_bot(current_chat_messages, st.session_state.current_chat_id)
        
        current_chat["messages"].append({
            "role": "assistant",
            "content": bot_response
        })
        
        # Save to database immediately
        save_message_to_db(user_id, st.session_state.current_chat_id, "assistant", bot_response)
        
        st.session_state.awaiting_response = False
        st.rerun()

# Fixed input area
col1, col2 = st.columns([9, 1])

with col1:
    prompt = st.chat_input("Type your message here...", disabled=st.session_state.awaiting_response)

with col2:
    if st.button("🗑️", key="clear_chat_btn", type="secondary", disabled=len(current_chat["messages"]) == 0):
        current_chat["messages"] = []
        current_chat["title"] = "New Chat"
        clear_chat_messages_db(user_id, st.session_state.current_chat_id)
        save_chat_to_db(user_id, st.session_state.current_chat_id, "New Chat", current_chat["created_at"], is_current=True)
        st.rerun()

if prompt:
    # Auto-generate title from first message
    if len(current_chat["messages"]) == 0:
        update_chat_title(st.session_state.current_chat_id, prompt)
    
    # Add user message to chat
    current_chat["messages"].append({"role": "user", "content": prompt})
    
    # Save to database immediately
    save_message_to_db(user_id, st.session_state.current_chat_id, "user", prompt)
    
    # Trigger bot response
    st.session_state.awaiting_response = True
    st.rerun()

# ==========================================================
# FOOTER
# ==========================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; font-size: 0.8rem; padding: 0.75rem; color: var(--secondary-text-color);">
    Powered by Koantek
</div>
""", unsafe_allow_html=True)
