# setup
create database bankAppDB;

# sql table setup
use bankAppDB;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    balance FLOAT DEFAULT 0,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    amount FLOAT NOT NULL,
    from_account_id INT,
    to_account_id INT,
    FOREIGN KEY (from_account_id) REFERENCES accounts(id),
    FOREIGN KEY (to_account_id) REFERENCES accounts(id)
);



# cmds
http://127.0.0.1:8000/docs


# for testing
pytest





# Todos:
## learn locale from url or user config. load default strings if locale missing.
## seek if config.py values should be moved to db. Better when config can be changed dynamically and load-balancer/K8s used.
## move account_id to larger numbers support.
## currently allows two users with same name. Unique username/email check, especially once auth is added.

