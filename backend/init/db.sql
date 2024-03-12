-- "SELECT id, email, password_hash, role, first_name, last_name, created_at FROM users WHERE email = ?"
-- created_at datetime

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  avatar_url TEXT,
  role TEXT NOT NULL DEFAULT 'user',  -- 'user' or 'operator'
  first_name TEXT NOT NULL,
  last_name TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
