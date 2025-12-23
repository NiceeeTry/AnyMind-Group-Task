# POS E-commerce Platform

A Point of Sale (POS) system built with FastAPI and GraphQL


## Tech Stack

- **FastAPI**
- **Strawberry GraphQL**: GraphQL library for Python
- **SQLAlchemy**: Async ORM for database operations
- **PostgreSQL**: Primary database
- **Docker**: Containerized deployment
- **Pytest**

## Prerequisites

- Docker and Docker Compose (recommended)
- Python 3.11+ (for local development)
- PostgreSQL 15+ (if running without Docker)

## Getting Started

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd AnyMind-Group-Task
```

2. Start the application:
```bash
docker-compose up --build
```

3. The API will be available at:
   - GraphQL endpoint: `http://localhost:8000/graphql`

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/pos_db"
export APP_NAME="POS E-commerce Platform"
```

3. Run the application:
```bash
python -m app.main
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Usage

### GraphQL Endpoint

Access the GraphQL playground at `http://localhost:8000/graphql` for interactive documentation and testing.

### Process Payment

```graphql
mutation {
  payment(input: {
    customerId: "customer123"
    price: "100.00"
    priceModifier: 0.95
    paymentMethod: CASH
    datetime: "2024-01-01T12:00:00Z"
  }) {
    ... on PaymentResult {
      finalPrice
      points
    }
    ... on PaymentError {
      message
    }
  }
}
```

**Payment Methods:**

| Payment Method | Value | Additional Requirements |
|----------------|-------|------------------------|
| Cash | `CASH` | None |
| Cash on Delivery | `CASH_ON_DELIVERY` | `courier` required |
| Visa | `VISA` | `last4` required |
| Mastercard | `MASTERCARD` | `last4` required |
| American Express | `AMEX` | `last4` required |
| JCB | `JCB` | `last4` required |
| LINE Pay | `LINE_PAY` | None |
| PayPay | `PAYPAY` | None |
| Points | `POINTS` | None |
| GrabPay | `GRAB_PAY` | None |
| Bank Transfer | `BANK_TRANSFER` | `bank`, `accountNumber` required |
| Cheque | `CHEQUE` | `bank`, `chequeNumber` required |

**Example with additional item (card payment):**
```graphql
mutation {
  payment(input: {
    customerId: "customer-001"
    price: "100.00"
    priceModifier: 0.95
    paymentMethod: VISA
    datetime: "2025-12-21T12:00:00Z"
    additionalItem: {
      last4: "1234"
    }
  }) {
    ... on PaymentResult {
      finalPrice
      points
    }
    ... on PaymentError {
      error
    }
  }
}
```

**Example with Cash on Delivery:**
```graphql
mutation {
  payment(input: {
    customerId: "customer123"
    price: "100.00"
    priceModifier: 1.0
    paymentMethod: CASH_ON_DELIVERY
    datetime: "2024-01-01T12:00:00Z"
    additionalItem: {
      courier: "YAMATO"
    }
  }) {
    ... on PaymentResult {
      finalPrice
      points
    }
    ... on PaymentError {
      error
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "payment": {
      "finalPrice": "95.00",
      "points": 95
    }
  }
}
```

### Get Sales Report

```graphql
query {
  sales(input: {
    startDatetime: "2024-01-01T00:00:00Z"
    endDatetime: "2024-01-01T23:59:59Z"
  }) {
    sales {
      datetime
      sales
      points
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "sales": {
      "sales": [
        {
          "datetime": "2024-01-01T12:00:00Z",
          "sales": "95.00",
          "points": 95
        }
      ]
    }
  }
}
```

### Health Check

```graphql
query {
  health
}
```

## Project Structure

```
task/
├── app/
│   ├── application/
│   │   ├── dto/
│   │   └── use_cases/
│   ├── domain/
│   │   ├── entities/
│   │   ├── repositories/
│   │   ├── services/
│   │   └── value_objects/
│   ├── infrastructure/
│   │   ├── config/
│   │   └── persistence/
│   ├── presentation/
│   │   └── graphql/
│   └── main.py
├── tests/
├── docker-compose.yml
├── Dockerfile 
└── requirements.txt
```

## Testing

Run the test suite:

```bash
pytest tests/
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg://postgres:postgres@db:5432/pos_db` |
| `APP_NAME` | Application name | `POS E-commerce Platform` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

## Database

The application uses PostgreSQL with the following main table:
- `transactions`: Stores payment transaction records

## Docker Services

- **app**: FastAPI application (port 8000)
- **db**: PostgreSQL database (port 5432)

