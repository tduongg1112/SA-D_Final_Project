# NovaMarket Microservices Workspace

NovaMarket is being evolved into a microservices-oriented architecture for the course project.

Current runtime services:

- `commerce-service` for storefront UI and the remaining consolidated customer-facing flow
- `product-service` for product APIs
- `cart-service` for cart APIs
- `ordering-service` for order APIs and checkout orchestration
- `payment-service` for payment APIs
- `shipping-service` for shipment APIs
- `ai-service` for recommendations and conversational shopping assistance
- `api-gateway` for routing, health aggregation, and gateway UI
- `postgres` with one logical database per business service

Repository structure:

- `services/commerce_service`
- `services/product_service`
- `services/cart_service`
- `services/ordering_service`
- `services/payment_service`
- `services/shipping_service`
- `services/ai_service`
- `services/api_gateway`
- `docs/`

Supporting architecture docs:

- [docs/DDD_Analysis.md](docs/DDD_Analysis.md)
- [docs/Microservices_Architecture.md](docs/Microservices_Architecture.md)
- [Plan.md](Plan.md)
- [UI_Plan.md](UI_Plan.md)

## Run with Docker

```bash
docker compose down -v
docker compose up --build
```

Database topology inside Postgres:

- `commerce_service`
- `product_service`
- `cart_service`
- `ordering_service`
- `payment_service`
- `shipping_service`

You can inspect the same Docker Postgres instance from DBeaver by connecting to `localhost:5432` with:

- user: `techstore`
- password: `techstore`
- database: choose one of the service databases above

Public entry points:

- Storefront through API Gateway: `http://localhost:8080`
- Gateway dashboard UI: `http://localhost:8080/gateway/`
- Commerce service directly: `http://localhost:8000`
- Product service directly: `http://localhost:8010/health`
- Ordering service directly: `http://localhost:8020/health`
- Cart service directly: `http://localhost:8030/health`
- Payment service directly: `http://localhost:8040/health`
- Shipping service directly: `http://localhost:8050/health`
- AI service health: `http://localhost:8001/health`

## Test the non-AI flow

Once the stack is running, the current recommended smoke path is:

1. Open `http://localhost:8080`
2. Browse the product catalog and add one or two products to cart
3. Open `/cart/` and submit checkout
4. Confirm the order success page shows payment and shipping state
5. Sign in as `staff` and open `/dashboard/`
6. Open `/gateway/` to verify the edge layer and service health

The storefront currently prioritizes the non-AI commerce flow. The AI service can remain idle while testing the rest of the project.

## Run services locally

### Commerce service

```bash
cd services/commerce_service
python3 manage.py migrate
python3 manage.py seed_demo
python3 manage.py runserver
```

### AI service

```bash
cd services/ai_service
uvicorn main:app --reload --port 8001
```

### Product service

```bash
cd services/product_service
python3 manage.py runserver 0.0.0.0:8010
```

### Ordering service

```bash
cd services/ordering_service
python3 manage.py runserver 0.0.0.0:8020
```

### Cart service

```bash
cd services/cart_service
python3 manage.py runserver 0.0.0.0:8030
```

### Payment service

```bash
cd services/payment_service
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8040
```

### Shipping service

```bash
cd services/shipping_service
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8050
```

### API Gateway

```bash
cd services/api_gateway
uvicorn app.main:app --reload --port 8080
```

## Demo accounts

- `admin` / `admin12345`
- `staff` / `staff12345`
- `customer` / `customer12345`
