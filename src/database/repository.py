
import sqlite3
import hashlib
from abc import ABC, abstractmethod
import os

DB_NAME = "bomberman.db"

class IScoreRepository(ABC):
    
    @abstractmethod
    def register_user(self, username, password, theme_preference="City"):
        pass

    @abstractmethod
    def login_user(self, username, password):
        pass

    @abstractmethod
    def save_score(self, user_id, score):
        pass

    @abstractmethod
    def fetch_top_scores(self, limit=10):
        pass

    @abstractmethod
    def close(self):
        pass


class SqliteRepository(IScoreRepository):
    def __init__(self, db_path=DB_NAME):
        self.db_path = db_path
        self._initialize_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                theme_preference TEXT DEFAULT 'City'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Stats (
                user_id INTEGER PRIMARY KEY,
                wins INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                best_score INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES Users(id)
            )
        ''')

        conn.commit()
        conn.close()

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, theme_preference="City"):
        conn = self._get_connection()
        cursor = conn.cursor()
        pwd_hash = self._hash_password(password)
        try:
            cursor.execute('''
                INSERT INTO Users (username, password_hash, theme_preference)
                VALUES (?, ?, ?)
            ''', (username, pwd_hash, theme_preference))
            
            user_id = cursor.lastrowid
            cursor.execute('''
                INSERT INTO Stats (user_id, wins, games_played, best_score)
                VALUES (?, 0, 0, 0)
            ''', (user_id,))
            
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def login_user(self, username, password):
        conn = self._get_connection()
        cursor = conn.cursor()
        pwd_hash = self._hash_password(password)

        cursor.execute('''
            SELECT id, username, theme_preference FROM Users 
            WHERE username = ? AND password_hash = ?
        ''', (username, pwd_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {'id': result[0], 'username': result[1], 'theme_preference': result[2]}
        return None

    def save_score(self, user_id, score):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT best_score FROM Stats WHERE user_id = ?', (user_id,))
        current_data = cursor.fetchone()
        if current_data:
            current_best = current_data[0]
            new_best = max(current_best, score)
            cursor.execute('''
                UPDATE Stats 
                SET games_played = games_played + 1,
                    best_score = ?
                WHERE user_id = ?
            ''', (new_best, user_id))
        conn.commit()
        conn.close()
   
    def update_wins(self, user_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE Stats SET wins = wins + 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

    def fetch_top_scores(self, limit=10):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.username, s.best_score, s.wins
            FROM Stats s
            JOIN Users u ON u.id = s.user_id
            ORDER BY s.best_score DESC
            LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    def close(self):
        pass
