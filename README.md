# Simple Swap API

A simple and efficient cryptocurrency exchange application, designed with clean architecture and domain-driven patterns.

## 🏗️ Architecture

### Hexagonal Architecture (Ports & Adapters)

The application follows **Hexagonal Architecture** principles, organizing code in concentric layers:

-   **Domain Layer**: Core business logic and entities (pure, no external dependencies)
-   **Application Layer**: Use cases and orchestration of business operations
-   **Infrastructure Layer**: External concerns (databases, APIs, frameworks)

**Benefits**: Domain logic is technology-agnostic. You can swap databases, APIs, or frameworks without touching business rules.

### Domain-Driven Design (DDD)

The codebase implements **Domain-Driven Design** patterns:

-   **Entities**: Objects with unique identity (User, Transfer)
-   **Value Objects**: Immutable objects without identity (Money, Currency)
-   **Domain Services**: Business logic that doesn't belong to specific entities
-   **Aggregates**: Groups of entities treated as a unit

**Benefits**: Code reflects business language and concepts, making it more understandable and maintainable.

### Ledger Pattern

All financial operations are recorded in an immutable ledger system for traceability and audit compliance.

### Note on Repository Pattern

The repository pattern is omitted across all modules for simplicity - entities directly use database sessions. This can be improved in future iterations for better abstraction.

## 🔄 Swap System Architecture

### Current Implementation

The swap functionality is implemented using the **Strategy Pattern** to handle different types of currency exchanges:

-   **FiatToFiatStrategy**: Handles exchanges between fiat currencies (USD ↔ ARS)
-   **CryptoToCryptoStrategy**: Handles exchanges between crypto currencies (BTC ↔ ETH)
-   **CryptoToFiatStrategy**: Handles exchanges between crypto and fiat currencies (BTC ↔ ARS)

### Fee Service

Another architectural consideration is implementing a dedicated fee calculation service:

**Potential Architecture:**

```
source/transfer/domain/services/
└── fee_service/
    ├── __init__.py
    ├── fee_strategy_interface.py
    ├── percentage_fee_strategy.py
    ├── fixed_fee_strategy.py
    └── fee_strategy_factory.py
```

**Features:**

-   **Operation-based fees**: Different fee structures for SWAP, DEPOSIT, WITHDRAWAL
-   **User tier-based fees**: VIP users with reduced fees
-   **Dynamic fees**: Based on market conditions or volume

### Trade-offs

The current simplified implementation prioritizes:

-   **Quick development**: Faster time to market
-   **Business validation**: Test core functionality before architectural investment

Future refactoring should consider the above patterns as the business requirements become more defined.

## 📦 Installation and Usage

### Prerequisites

-   Docker
-   Docker Compose

### Launch the Application

1. **Clone the repository**

    ```bash
    git clone [<repository-url>](https://github.com/mcapparelli/ss-api)
    cd ss-api
    ```

2. **Launch with Docker Compose**

    ```bash
    cd .local
    docker compose up
    ```

3. **Verify it's working**

    ```bash
    curl http://localhost:8000/health
    ```

4. **Access documentation**
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc

### Environment Variables

The application uses the following environment variables (configured in docker-compose.yml):

-   `DATABASE_URL`: PostgreSQL connection
-   `ENV`: Execution environment (DEV/STG/PROD)

## 📚 Main Endpoints

### API

-   `POST /users` - Create new user with initial balances
-   `POST /swaps` - Create cryptocurrency swap
-   `POST /deposits` - Register deposit

## 🔧 Development

### Run Tests

```bash
docker compose exec api python -m pytest
```

### Run Specific Tests

```bash
docker compose exec api python source/user/domain/entities/user_balance/user_balance_entity_test.py
```

### View Logs

```bash
docker compose logs -f api
```

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
