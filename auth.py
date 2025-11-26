import streamlit as st
import sqlite3
import hashlib
import uuid
from datetime import datetime
from contextlib import contextmanager

# ==========================================================
# DATABASE CONFIGURATION
# ==========================================================
DB_FILE = "app_database.db"

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# ==========================================================
# DATABASE INITIALIZATION
# ==========================================================
def init_auth_database():
    """Initialize authentication tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
        """)
        
        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """)
        
        # Create user_chats table (for chatbot)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_chats (
                chat_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_current INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """)
        
        # Create user_messages table (for chatbot)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (chat_id) REFERENCES user_chats (chat_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_chats_user_id 
            ON user_chats(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_messages_chat_id 
            ON user_messages(chat_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_messages_user_id 
            ON user_messages(user_id)
        """)
        
        conn.commit()

# ==========================================================
# PASSWORD HASHING
# ==========================================================
def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == password_hash

# ==========================================================
# USER MANAGEMENT
# ==========================================================
def create_user(username: str, password: str, email: str = None) -> tuple[bool, str]:
    """Create a new user account"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            user_id = str(uuid.uuid4())
            password_hash = hash_password(password)
            created_at = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO users (user_id, username, password_hash, email, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, password_hash, email, created_at))
            
            conn.commit()
            return True, "Account created successfully!"
            
    except sqlite3.IntegrityError:
        return False, "Username or email already exists"
    except Exception as e:
        return False, f"Error creating account: {str(e)}"

def authenticate_user(username: str, password: str) -> tuple[bool, str, str]:
    """Authenticate user and return success status, user_id, and username"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, username, password_hash 
                FROM users 
                WHERE username = ?
            """, (username,))
            
            user = cursor.fetchone()
            
            if user and verify_password(password, user['password_hash']):
                # Update last login
                cursor.execute("""
                    UPDATE users 
                    SET last_login = ? 
                    WHERE user_id = ?
                """, (datetime.now().isoformat(), user['user_id']))
                conn.commit()
                
                return True, user['user_id'], user['username']
            else:
                return False, "", ""
                
    except Exception as e:
        return False, "", ""

# ==========================================================
# SESSION MANAGEMENT
# ==========================================================
def create_session(user_id: str) -> str:
    """Create a new session for user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        session_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        expires_at = datetime.now().isoformat()  # Can add expiration logic
        
        cursor.execute("""
            INSERT INTO sessions (session_id, user_id, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        """, (session_id, user_id, created_at, expires_at))
        
        conn.commit()
        return session_id

def validate_session(session_id: str) -> tuple[bool, str]:
    """Validate session and return user_id if valid"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id FROM sessions 
                WHERE session_id = ?
            """, (session_id,))
            
            session = cursor.fetchone()
            
            if session:
                return True, session['user_id']
            else:
                return False, ""
                
    except Exception:
        return False, ""

def delete_session(session_id: str):
    """Delete a session (logout)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()

# ==========================================================
# AUTHENTICATION HELPERS
# ==========================================================
def require_authentication():
    """
    Check if user is authenticated. If not, redirect to login page.
    Returns: tuple(user_id, username)
    """
    # Initialize database
    init_auth_database()
    
    # Check if user is logged in
    if 'session_id' not in st.session_state or 'user_id' not in st.session_state:
        st.switch_page("Login.py")
        st.stop()
    
    # Validate session
    is_valid, user_id = validate_session(st.session_state.session_id)
    
    if not is_valid or user_id != st.session_state.user_id:
        # Invalid session, clear and redirect
        st.session_state.clear()
        st.switch_page("Login.py")
        st.stop()
    
    return st.session_state.user_id, st.session_state.username

def logout_user():
    """Logout current user"""
    if 'session_id' in st.session_state:
        delete_session(st.session_state.session_id)
    st.session_state.clear()

def is_authenticated() -> bool:
    """Check if user is currently authenticated"""
    if 'session_id' not in st.session_state or 'user_id' not in st.session_state:
        return False
    
    is_valid, _ = validate_session(st.session_state.session_id)
    return is_valid