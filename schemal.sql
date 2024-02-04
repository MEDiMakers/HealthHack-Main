CREATE TABLE IF NOT EXISTS Users (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ChatSessions (
    ChatSessionID INTEGER PRIMARY KEY AUTOINCREMENT,
    ChatTitle TEXT DEFAULT 'New Chat',
    UserID INTEGER,
    LastMessageTimestamp TIMESTAMP,
    FOREIGN KEY(UserID) REFERENCES Users(UserID)
);

CREATE TABLE IF NOT EXISTS Messages (
    MessageID INTEGER PRIMARY KEY AUTOINCREMENT,
    ChatSessionID INTEGER,
    MessageText TEXT NOT NULL,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    SentByUser BOOLEAN NOT NULL CHECK (SentByUser IN (0, 1)),
    FOREIGN KEY(ChatSessionID) REFERENCES ChatSessions(ChatSessionID)
);

-- Schema details
-- Users: UserID, Username, CreatedAt
-- ChatSessions: ChatSessionID, UserID, IsActive(not needed?), LastMessageTimestamp
-- Messages: MessageID, ChatSessionID, MessageText, Timestamp, SentByUser
