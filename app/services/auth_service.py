import hashlib
import os
import hmac
import time
import base64
import json
from typing import Optional, Dict, Any
from app.config import SECRET_KEY
from app.database import db_session

def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}:{dk.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt, expected_hash = hashed_password.split(":")
        dk = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return hmac.compare_digest(dk.hex(), expected_hash)
    except Exception:
        return False

def create_access_token(user_id: int, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": int(time.time()) + (86400 * 7)  # 7 days
    }
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    sig = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{sig}"

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, sig = parts
        
        # Check signature
        expected_sig = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        
        # Pad base64
        padded = payload_b64 + "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode()).decode())
        
        if payload.get("exp", 0) < time.time():
            return None
        
        return payload
    except Exception:
        return None

def register_user(name: str, email: str, password: str) -> Dict[str, Any]:
    email_clean = email.strip().lower()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email_clean,))
        if cursor.fetchone():
            raise ValueError("An account with this email already exists.")
        
        pwd_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, current_streak, total_study_time, last_active_date) VALUES (?, ?, ?, 1, 0, date('now'))",
            (name.strip(), email_clean, pwd_hash)
        )
        user_id = cursor.lastrowid
        token = create_access_token(user_id, email_clean)
        return {
            "token": token,
            "user": {
                "id": user_id,
                "name": name.strip(),
                "email": email_clean,
                "current_streak": 1,
                "total_study_time": 0
            }
        }

def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    email_clean = email.strip().lower()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, password_hash, current_streak, total_study_time FROM users WHERE email = ?", (email_clean,))
        user = cursor.fetchone()
        if not user:
            raise ValueError("Invalid email or password.")
        
        if not verify_password(password, user["password_hash"]):
            raise ValueError("Invalid email or password.")
        
        # Update streak if needed
        cursor.execute("""
            UPDATE users 
            SET current_streak = CASE 
                WHEN last_active_date = date('now') THEN current_streak 
                WHEN last_active_date = date('now', '-1 day') THEN current_streak + 1 
                ELSE 1 
            END,
            last_active_date = date('now')
            WHERE id = ?
        """, (user["id"],))
        
        token = create_access_token(user["id"], email_clean)
        return {
            "token": token,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "current_streak": user["current_streak"] or 1,
                "total_study_time": user["total_study_time"] or 0
            }
        }

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, current_streak, total_study_time FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
