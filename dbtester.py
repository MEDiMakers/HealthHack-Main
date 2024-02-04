import database
import sqlite3
import datetime

def test_init_db():
    print("Testing init_db()...")
    try:
        database.init_db()
        print("init_db() executed successfully.")
        print_users_table()
    except sqlite3.Error as e:
        print(f"Error during init_db(): {e}\n")

def test_reset_db():
    print("Testing reset_db()...")
    try:
        database.reset_db()
        print("reset_db() executed successfully.")
        print_users_table()
    except sqlite3.Error as e:
        print(f"Error during reset_db(): {e}\n")

def print_users_table(): #this is a helper function
    try:
        conn = sqlite3.connect('chat_app.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users")
        users = cursor.fetchall()
        conn.close()
        print("Users Table:")
        for user in users:
            print(user)
    except sqlite3.Error as e:
        print(f"Error fetching users: {e}")
    print()


def test_start_new_chat():
    print("Testing start_new_chat()...")
    user_id = 1  # Assuming user with ID 1 exists
    chat_session_id = database.start_new_chat(user_id)
    print(f"New chat session started with ID: {chat_session_id}\n")

def test_load_chat(chat_session_id):
    print("Testing load_chat()...")
    chat = database.load_chat(chat_session_id)
    print(f"Loaded chat session: {chat}\n")

def test_load_chats_for_sidebar():
    print("Testing load_chats_for_sidebar()...")
    chats = database.load_chats_for_sidebar()
    print("Chats loaded for sidebar:")
    for chat in chats:
        print(chat)
    print()

def test_log_message(chat_session_id, message):
    print("Testing log_message()...")
    database.log_message(chat_session_id, message, True)
    print("Message logged successfully.\n")

def test_rename_chats(chat_session_id, new_title):
    print("Testing update_chat_title()...")
    oldtitle = database.load_chat(chat_session_id)[0][3]
    print(f"chat name before update: {oldtitle}")
    database.update_chat_title(chat_session_id, new_title)
    chat = database.load_chat(chat_session_id)
    print(f"chat name updated to: {chat[0][3]}.\n")

if __name__ == "__main__":
    test_init_db()
    test_reset_db()
    test_start_new_chat()
    test_start_new_chat()
    test_load_chat(1)
    test_log_message(1, "Hello, world!")
    test_load_chat(1)
    test_start_new_chat()
    test_load_chat(3)
    test_log_message(3, "this is chat number 3!")
    test_load_chats_for_sidebar()
    test_rename_chats(3, "Chat Title (updated!)")
    test_reset_db()
    test_load_chats_for_sidebar() # chats have reset.


