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
CREATE INDEX IF NOT EXISTS users_email_idx ON users(email);
CREATE INDEX IF NOT EXISTS users_role_idx ON users(role);

CREATE TABLE IF NOT EXISTS user_preferences (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  allow_faq BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS messages (
  id SERIAL PRIMARY KEY,
  from_user_id INTEGER NOT NULL REFERENCES users(id),
  to_user_id INTEGER NOT NULL REFERENCES users(id),
  is_read BOOLEAN NOT NULL DEFAULT FALSE,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS messages_from_idx ON messages(from_user_id);
CREATE INDEX IF NOT EXISTS messages_to_idx ON messages(to_user_id);
CREATE INDEX IF NOT EXISTS messages_from_to_idx ON messages(from_user_id, to_user_id);
CREATE INDEX IF NOT EXISTS messages_from_to_ts_idx ON messages(from_user_id, to_user_id, created_at);

CREATE TABLE IF NOT EXISTS chat_sessions (
  id SERIAL PRIMARY KEY,
  user_1_id INTEGER NOT NULL REFERENCES users(id),
  user_2_id INTEGER NOT NULL REFERENCES users(id),
  allow_ml BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS chat_sessions_user_1_created_at_idx ON chat_sessions(user_1_id, created_at);
CREATE INDEX IF NOT EXISTS chat_sessions_user_2_created_at_idx ON chat_sessions(user_2_id, created_at);
CREATE INDEX IF NOT EXISTS chat_sessions_user_1_user_2_idx ON chat_sessions(user_1_id, user_2_id);

-- INIT DATA
---- Operator pseudo-user
INSERT INTO USERS (id, email, password_hash, role, first_name)
VALUES (0, 'operator@testingcbr.idk', '', 'operator', 'Оператор');

-- MOCK DATA
---- Mock users
-- password0
INSERT INTO USERS (email, password_hash, role, first_name, last_name)
VALUES ('user0@test.com', '$2a$12$y/IvWuYPgymiy2I8ZlaAluBFiqNFvuHiiBCHN4R56Y0nJubisJu/u', 'user', 'Имя-0', 'Фамилия-0');

-- password1
INSERT INTO USERS (email, password_hash, role, first_name, last_name)
VALUES ('user1@test.com', '$2a$12$US.mibTTxcXxSJWQBR4H8O9ILikL/.2fzHDSqgnM5ja0yiU1v7jWK', 'user', 'Имя-1', 'Фамилия-1');

-- password2
INSERT INTO USERS (email, password_hash, role, first_name, last_name)
VALUES ('user2@test.com', '$2a$12$KJadZpT8WuUX/ht2QBrSAuqeQkJNve38IpFukwRwg53uNFcjr6vkC', 'user', 'Имя-2', 'Фамилия-2');

-- password3
INSERT INTO USERS (email, password_hash, role, first_name, last_name)
VALUES ('user3@test.com', '$2a$12$EJlUeZPlQ/dZQ2GSFHuLAuPyeY96UeRiOWGkqMPQtHba0c/3gyIbO', 'user', 'Имя-3', 'Фамилия-3');

-- operator4
INSERT INTO USERS (email, password_hash, role, first_name, last_name)
VALUES ('operator4@test.com' '$2a$12$x5rNeDoVa1CuNFC3eVmK8.ZKvjWgmhORPjsMzmThCQGz72svV0/Ge', 'operator', 'Оля', 'Операторова');

---- Mock messages
INSERT INTO messages (from_user_id, to_user_id, content, created_at)
VALUES (1, 0, 'Привет, оператор!', '2024-02-11 22:00:00');
INSERT INTO messages (from_user_id, to_user_id, content, created_at)
VALUES (0, 1, 'Добрый день, пользователь! Как могу помочь?', '2024-02-11 22:00:05');
INSERT INTO messages (from_user_id, to_user_id, content, created_at)
VALUES (1, 0, 'Мне нужна помощь с чем-то', '2024-02-11 22:00:10');
INSERT INTO messages (from_user_id, to_user_id, content, created_at)
VALUES (0, 1, 'Конечно, чем могу помочь?', '2024-02-11 22:00:15');

INSERT INTO messages (from_user_id, to_user_id, content, created_at)
VALUES (2, 0, 'Что там с курсом валют?', '2024-02-11 22:00:20');
INSERT INTO messages (from_user_id, to_user_id, content, created_at)
VALUES (0, 2, 'Курс валют на сегодня: 1 USD = 512 RUB', '2024-02-11 22:00:25');
INSERT INTO messages (from_user_id, to_user_id, content, created_at)
VALUES (2, 0, 'Спасибо!', '2024-02-11 22:00:30');
INSERT INTO messages (from_user_id, to_user_id, content, created_at)
VALUES (0, 2, 'Пожалуйста!', '2024-02-11 22:00:35');

INSERT INTO messages (from_user_id, to_user_id, content, created_at)
VALUES (2, 1, 'Привет, пользователь!', '2024-02-11 22:00:40');
INSERT INTO messages (from_user_id, to_user_id, content, created_at)
VALUES (1, 2, 'Добрый день, чел! Как могу помочь?', '2024-02-11 22:00:45');
INSERT INTO messages (from_user_id, to_user_id, content, created_at)
VALUES (2, 1, 'Мне нужна помощь с чем-то', '2024-02-11 22:00:50');
INSERT INTO messages (from_user_id, to_user_id, content, created_at)
VALUES (1, 2, 'Конечно, чем могу помочь?', '2024-02-11 22:00:55');

