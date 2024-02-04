import sqlite3
from sqlite3 import Error
import datetime


def init_db():
    try:
        conn = sqlite3.connect('chat_app.db')
        cursor = conn.cursor()

        # Create Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL,
            CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        # Create ChatSessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ChatSessions (
            ChatSessionID INTEGER PRIMARY KEY AUTOINCREMENT,
            ChatTitle TEXT DEFAULT 'New Chat',
            UserID INTEGER,
            LastMessageTimestamp TIMESTAMP,
            FOREIGN KEY(UserID) REFERENCES Users(UserID)
        );
        ''')
        # Create Messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Messages (
            MessageID INTEGER PRIMARY KEY AUTOINCREMENT,
            ChatSessionID INTEGER,
            MessageText TEXT NOT NULL,
            Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            SentByUser BOOLEAN NOT NULL CHECK (SentByUser IN (0, 1)),
            FOREIGN KEY(ChatSessionID) REFERENCES ChatSessions(ChatSessionID) ON DELETE CASCADE
        );
        ''')
        # Insert default user "ethan" if not exists
        cursor.execute('''
        INSERT OR IGNORE INTO Users (UserID, Username) VALUES (1, 'ethan');
        ''')
        conn.commit()
    except Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def reset_db():
    try:
        conn = sqlite3.connect('chat_app.db')
        cursor = conn.cursor()
        cursor.executescript('''
            DROP TABLE IF EXISTS Messages;
            DROP TABLE IF EXISTS ChatSessions;
            DROP TABLE IF EXISTS Users;
        ''')
        conn.commit()
        init_db()  # Re-initialize the database after reset
    except Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def start_new_chat(user_id): 
    try:
        conn = sqlite3.connect('chat_app.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO ChatSessions (UserID) VALUES (?);
        ''', (user_id,))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def load_chat(chat_session_id):
    try:
        conn = sqlite3.connect('chat_app.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT m.MessageID, m.MessageText, m.SentByUser, m.Timestamp, cs.ChatTitle 
            FROM Messages m 
            JOIN ChatSessions cs ON m.ChatSessionID = cs.ChatSessionID
            WHERE m.ChatSessionID = ? ORDER BY Timestamp;
        ''', (chat_session_id,))
        return cursor.fetchall()
    except Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def load_chats_for_sidebar():
    try:
        conn = sqlite3.connect('chat_app.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT ChatSessionID, ChatTitle, LastMessageTimestamp FROM ChatSessions ORDER BY LastMessageTimestamp DESC;
        ''')
        return cursor.fetchall()
    except Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

def update_chat_title(chat_session_id, new_title):
    try:
        conn = sqlite3.connect('chat_app.db')
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE ChatSessions SET ChatTitle = ? WHERE ChatSessionID = ?;
        ''', (new_title, chat_session_id))
        conn.commit()
    except Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def clear_user_history(user_id, excluded_chat_id):
    try:
        conn = sqlite3.connect('chat_app.db')
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM ChatSessions WHERE UserID = ? AND ChatSessionID <> ?;
        ''', (user_id, excluded_chat_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

def log_message(chat_session_id, message_text, sent_by_user):
    try:
        conn = sqlite3.connect('chat_app.db')
        cursor = conn.cursor()

        # Insert the new message into the Messages table
        cursor.execute('''
            INSERT INTO Messages (ChatSessionID, MessageText, SentByUser) VALUES (?, ?, ?);
        ''', (chat_session_id, message_text, sent_by_user))

        message_id = cursor.lastrowid
        # Update the LastMessageTimestamp in the ChatSessions table
        cursor.execute('''
            UPDATE ChatSessions 
            SET LastMessageTimestamp = ?
            WHERE ChatSessionID = ?;
        ''', (datetime.datetime.now(), chat_session_id))
        conn.commit()
        return message_id
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def load_message(message_id):
    try:
        conn = sqlite3.connect('chat_app.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT MessageText FROM Messages WHERE MessageID = ?;
        ''', (message_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"An error occurred at load_message: {e}")
    finally:
        if conn:
            conn.close()
    