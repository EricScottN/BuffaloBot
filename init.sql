CREATE TABLE IF NOT EXISTS roles (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
);
CREATE TABLE IF NOT EXISTS categories (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
);
CREATE TABLE IF NOT EXISTS channels (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
);
CREATE TABLE IF NOT EXISTS members (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS role_members (
    role_id BIGINT REFERENCES roles(id),
    member_id BIGINT REFERENCES members(id),
    PRIMARY KEY (role_id, member_id)
);