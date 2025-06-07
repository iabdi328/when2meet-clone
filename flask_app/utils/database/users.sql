-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    creator_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Invites table (handles both registered users and external emails)
CREATE TABLE IF NOT EXISTS invites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    user_id INTEGER,    
    email TEXT,        
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT one_of_user_or_email CHECK (
        (user_id IS NOT NULL AND email IS NULL) OR 
        (user_id IS NULL AND email IS NOT NULL)
    )
);

-- Availabilities table (stores availability per slot per user)
CREATE TABLE IF NOT EXISTS availabilities (
    user_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    date TEXT NOT NULL,       
    time TEXT NOT NULL,      
    status TEXT NOT NULL CHECK (status IN ('available', 'maybe', 'unavailable')),
    PRIMARY KEY (user_id, event_id, date, time),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);
