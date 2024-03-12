-- "SELECT id, email, password_hash, role, first_name, last_name, created_at FROM users WHERE email = ?"
-- created_at datetime
CREATE TABLE IF NOT EXISTS users (
  id INT8 PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
