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
    git clone https://github.com/mcapparelli/ss-api
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
-   `POST /swap` - Create currency swap
-   `POST /deposit` - Register deposit

## 🚀 API Usage Examples

### 1. Create a User

Creates a new user with initial balances for all supported currencies (ARS, USD, BTC, ETH).

```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe"
  }'
```

**Response:**

```json
{
	"id": "c538ff42-d559-4ab8-bcb3-1c5d243176a2",
	"name": "John Doe",
	"balance": [
		{ "currency": "ARS", "amount": 0.0 },
		{ "currency": "USD", "amount": 0.0 },
		{ "currency": "BTC", "amount": 0.0 },
		{ "currency": "ETH", "amount": 0.0 }
	]
}
```

### 2. Make a Deposit

Adds funds to a user's balance for a specific currency.

```bash
curl -X POST "http://localhost:8000/deposit" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "amount": "1000.50",
    "currency": "USD"
  }'
```

**Response:**

```json
{
	"id": "987fcdeb-51a2-43d5-b789-123456789abc",
	"type": "DEPOSIT",
	"user_id": "123e4567-e89b-12d3-a456-426614174000",
	"status": "CONFIRMED",
	"created_at": "2024-01-15T10:30:45.123456"
}
```

### 3. Perform a Swap

Exchange one currency for another using real-time exchange rates.

#### Fiat to Crypto (USD → BTC)

```bash
curl -X POST "http://localhost:8000/swap" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "amount": "100",
    "currency": "USD",
    "target_currency": "BTC"
  }'
```

#### Crypto to Crypto (BTC → ETH)

```bash
curl -X POST "http://localhost:8000/swap" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "amount": "0.001",
    "currency": "BTC",
    "target_currency": "ETH"
  }'
```

#### Fiat to Fiat (USD → ARS)

```bash
curl -X POST "http://localhost:8000/swap" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "amount": "50",
    "currency": "USD",
    "target_currency": "ARS"
  }'
```

**Response:**

```json
{
	"id": "ref-456789",
	"type": "SWAP",
	"status": "CONFIRMED",
	"amount": "0.00234567",
	"currency": "BTC",
	"created_at": "2024-01-15T11:15:30.654321"
}
```

### 4. View Transaction History

Get the transaction history for a specific user.

```bash
curl -X GET "http://localhost:8000/user/123e4567-e89b-12d3-a456-426614174000/history"
```

### Supported Currencies

-   **Fiat**: `ARS` (Argentine Peso), `USD` (US Dollar)
-   **Crypto**: `BTC` (Bitcoin), `ETH` (Ethereum)

### Complete Workflow Example

```bash
# 1. Create user
USER_RESPONSE=$(curl -s -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}')

USER_ID=$(echo $USER_RESPONSE | jq -r '.id')

# 2. Deposit USD
curl -X POST "http://localhost:8000/deposit" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"amount\": \"500\",
    \"currency\": \"USD\"
  }"

# 3. Swap USD to BTC
curl -X POST "http://localhost:8000/swap" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"amount\": \"100\",
    \"currency\": \"USD\",
    \"target_currency\": \"BTC\"
  }"

# 4. Check transaction history
curl -X GET "http://localhost:8000/user/$USER_ID/history"
```

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
