# Banking API - README
Here's a detailed README content for your project, explaining the setup, testing, and design decisions, as well as the organization of the codebase. This README is structured to give a clear understanding of the project, how to set it up, how it works, and where further improvements can be made.

## Running the Application

You can run the FastAPI application locally by using Uvicorn:

```bash
uvicorn app.main:app --reload
```

This starts the application at `http://127.0.0.1:8000/`.
You can access the interactive API documentation at:

```
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
```

### All APIs
![base_api.png](images%2Fbase_api.png)

### Transfer API
![transfer_api.png](images%2Ftransfer_api.png)
## Testing

To run the tests for the project, use pytest:
run from base directory of bank_api
```bash
pytest tests\test_routes.py 
```

This will run the test suite and check for functionality in your routes, such as creating users, creating accounts, transferring money, and reading transaction history.

## Todos:

-   **Locale handling:** Learn locale from the URL or user configuration. Load default strings if locale is missing.
-   **Dynamic Configuration:** Investigate if values from `config.py` should be moved to the database. This is especially useful when configurations need to change dynamically, and to support better scalability (e.g., Kubernetes).
-   **Support for Larger Numbers:** Move `account_id` to support larger numbers for scalability.
-   **Unique Usernames:** Currently, users with the same name are allowed. In the future, there should be unique checks for usernames/emails, especially once authentication is added.
-   **Improved API Responses:** Enhance return values for POST requests, especially for the transfer endpoint, which could return a `transaction_id` or additional useful information.

## Design

The design of this application is based on standard practices for building an API with FastAPI and SQLAlchemy, while also leaving room for scalability and improvement. Below is an overview of the file structure and the design decisions made.

### File Structure

-   `locales/`: Stores localization files (e.g., `en.json`, `es.json`) for supporting multiple languages in the app.
-   `__init__.py`: Makes the folder a Python package and initializes necessary components.
-   `auth.py`: Contains any authentication logic (not implemented yet, but could be for JWT or OAuth).
-   `config.py`: Stores configuration variables like the database connection string and other app-specific settings.
-   `crud.py`: Contains the functions that perform operations on the database (creating users, accounts, transferring money, etc.).
-   `database.py`: Manages the database connection and session lifecycle.
-   `localization.py`: Handles loading and parsing of the localization files (like `locales/en.json`).
-   `main.py`: The main entry point for the FastAPI app. It defines routes like creating users, creating accounts, transferring money, and reading transaction history.
-   `models.py`: Defines the SQLAlchemy models for the database (User, Account, Transaction).
-   `schemas.py`: Defines Pydantic models (currently not implemented).

### Few files explanation for expansion possibilities

#### `main.py`:
This file sets up the FastAPI app and handles routing. Routes for creating users, accounts, transferring money, and retrieving users and accounts are defined here. It includes business logic, request validation, and interacts with the database via CRUD functions.

**Potential improvements:** As the app scales, these routes can be refactored into separate microservices (e.g., one for updates, one for reads) to enhance performance.

#### `crud.py`:
The `crud.py` file contains functions that interact with the database to perform the actual business logic (e.g., creating users and accounts, transferring money).

**Potential improvements:** Each function could be split into a dedicated service for scaling. For example, the `transfer_money` function could be its own microservice, which can be scaled independently based on load and could handle transactional rollbacks.

### Design Considerations

#### Monolith vs. Microservices:
This app is currently a monolith, where all CRUD operations and routes are handled within a single application. This is fine for smaller applications.

**Future Scaling:** For scaling, we could consider breaking the app into microservices based on resource usage. For example:
-   A "read" service for fetching users, accounts, and transaction history.
-   A "write" service for creating accounts, users, and transferring money.
-   The "update" service could be dedicated to high-throughput operations, especially if account transfers or balance updates become more frequent.

#### Data Architecture:
-   **Normalization:** Currently, the database schema is normalized, with separate tables for users, accounts, and transactions. This design can be easily extended.
-   **Scalability:** If the app needs to scale, the current design allows for horizontal scaling, with each service (e.g., accounts, transactions) being deployed independently.

#### Performance Considerations:
-   **Caching:** For reads (e.g., account details, transaction history), caching can be introduced to reduce load on the database.
-   **Database Optimization:** Indexing frequently queried columns (like `user_id` in accounts, and `account_id` in transactions) can speed up queries.

#### Containerization:
-   **Docker:** The app can be containerized using Docker to make it easy to deploy on cloud platforms like AWS, Azure, or GCP.
-   **Kubernetes:** For scaling the application, especially if split into microservices, Kubernetes can be used to manage and scale containers based on load.


### Testing Scenarios

Currently, the testing for various scenarios (edge cases, error handling, etc.) is not fully implemented due to time constraints. However, the code base has been structured so that additional tests can be added easily. The main focus was to test API routes and basic CRUD functionality. Future improvements could involve:

-   Writing comprehensive tests for all scenarios, including invalid data inputs and edge cases (e.g., transferring funds from an account with insufficient balance, invalid user IDs, etc.).
-   Using mocking to isolate individual components (like database calls) in unit tests.

### Design and Scaling Future Considerations:

If this app grows, microservices could be used for each of the key features:
-   **Create/update service:** This can handle user creation and account updates (with transactional guarantees).
-   **Read service:** This could handle user and account reads, potentially with caching for performance.
-   **Transfer service:** A dedicated service for handling money transfers, with enhanced failure recovery and transactional rollback.

### Dockerization (Future Considerations)

To containerize the app and make it scalable using Docker and Kubernetes:

-   Create a `Dockerfile` to build an image for the app.
-   Use Docker Compose for managing multi-container setups (if you have separate services like databases, etc.).
-   **Kubernetes:** When you need to scale, you can deploy the app to a Kubernetes cluster and let Kubernetes manage container scaling based on traffic.



## Setup

### Create Database:
Create the database `bankAppDB` in your MySQL server:

```sql
CREATE DATABASE bankAppDB;
```

### Manual SQL Table Setup:
Use the created database and set up the necessary tables for users, accounts, and transactions:

```sql
USE bankAppDB;

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
```





