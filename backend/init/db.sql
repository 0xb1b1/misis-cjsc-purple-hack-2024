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
CREATE INDEX users_email_idx ON users(email);
CREATE INDEX users_role_idx ON users(role);

-- Operator pseudo-user
INSERT INTO USERS (id, email, password_hash, role, first_name)
VALUES (0, 'operator@testingcbr.id', '', 'operator', '??');


CREATE TABLE IF NOT EXISTS messages (
  id SERIAL PRIMARY KEY,
  from_user_id INTEGER NOT NULL REFERENCES users(id),
  to_user_id INTEGER NOT NULL REFERENCES users(id),
  is_read BOOLEAN NOT NULL DEFAULT FALSE,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX messages_from_idx ON messages(from_user_id);
CREATE INDEX messages_to_idx ON messages(to_user_id);
CREATE INDEX messages_from_to_idx ON messages(from_user_id, to_user_id);
CREATE INDEX messages_from_to_ts_idx ON messages(from_user_id, to_user_id, created_at);
