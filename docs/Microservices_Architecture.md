# Microservices Architecture: TechStore

## Target structure

The target implementation follows a standard microservices layout:

```text
services/
  api_gateway/
  commerce_service/
  catalog_service/
  cart_service/
  ordering_service/
  payment_service/
  shipping_service/
  ai_service/
docs/
infra/
```

## Why this shape

This project needs to satisfy both academic and engineering goals:

- it must clearly demonstrate microservices architecture,
- it must preserve a workable implementation path,
- and it must remain understandable enough for a final report and demo.

Because of that, the public runtime shape is already service-oriented:

- `api-gateway` is the single public entry point
- `commerce-service` serves the storefront, cart flow, and remaining consolidated business logic
- `catalog-service` serves catalog APIs
- `cart-service` serves cart APIs
- `ordering-service` serves order APIs
- `payment-service` serves payment APIs
- `shipping-service` serves shipment APIs
- `ai-service` handles recommendation and conversational assistance
- `db` stores the commerce state

## Service responsibilities

## 1. API Gateway

Responsibilities:

- single public entry point
- route matching and forwarding
- service registry
- health aggregation
- request correlation and logging
- gateway UI for architecture visibility during demo

Public paths:

- `/` -> proxied storefront
- `/products/*` -> proxied storefront routes
- `/cart/*` -> proxied storefront routes
- `/orders/*` -> proxied storefront routes
- `/dashboard/*` -> proxied storefront routes
- `/api/catalog/*` -> catalog-facing API exposed by catalog service
- `/api/cart/*` -> cart-facing API exposed by cart service
- `/api/orders/*` -> ordering-facing API exposed by ordering service
- `/api/payments/*` -> payment-facing API exposed by payment service
- `/api/shipping/*` -> shipment-facing API exposed by shipping service
- `/api/ai/*` -> AI service
- `/gateway/` -> gateway dashboard UI
- `/gateway/health` -> aggregated health response

## 2. Commerce Service

Responsibilities:

- storefront UI
- remaining consolidated customer-facing flows
- checkout initiation from the web experience
- staff dashboard

Notes:

- This service still contains storefront concerns and transitional integration logic.
- Business ownership is being moved out to dedicated services incrementally.

## 3. AI Service

Responsibilities:

- product recommendation
- conversational shopping assistant
- lightweight knowledge retrieval

Notes:

- It is independent from the commerce runtime.
- It can evolve into a richer RAG or ML service without changing the public gateway contract.

## 4. Catalog Service

Responsibilities:

- dedicated catalog API runtime
- product read model exposure
- category and product listing endpoints

Notes:

- This is the first extracted business service from the former consolidated commerce runtime.

## 5. Ordering Service

Responsibilities:

- dedicated order API runtime
- checkout orchestration for order creation
- order detail read model exposure

Notes:

- Payment and shipping are now external collaborators reached over HTTP.

## 6. Payment Service

Responsibilities:

- dedicated payment API runtime
- create and query payment records
- expose payment status by order identifier

## 7. Shipping Service

Responsibilities:

- dedicated shipping API runtime
- create and query shipment records
- expose shipment status and tracking code by order identifier

## API Gateway behavior

The gateway must be more than a static reverse proxy.

Required behaviors:

- maintain a service registry
- proxy requests by route prefix
- preserve method, query string, and body
- strip hop-by-hop headers
- add request correlation metadata
- expose a health dashboard
- provide an operator-facing UI for service visibility

## Internal communication

Current communication style:

- synchronous HTTP between gateway and services
- synchronous HTTP from gateway to AI service
- synchronous HTTP from gateway to business services
- synchronous HTTP from ordering to payment and shipping services

Future-compatible extension points:

- event publication from ordering to payment/shipping
- outbox pattern for reliable state propagation
- centralized auth token validation at the gateway layer

## Runtime topology

```text
Browser
  -> API Gateway
      -> Commerce Service
      -> Catalog Service
      -> Cart Service
      -> Ordering Service
      -> Payment Service
      -> Shipping Service
      -> AI Service
      -> Database
```

## Evolution path

The next architectural evolution after the current phase is:

1. move storefront cart state consumption fully behind `cart-service`
2. reduce shared database coupling between extracted runtimes
3. introduce async events where transaction boundaries become cross-service
4. extract identity and access into an independent runtime

## Demo value

This architecture is intentionally suitable for presentation:

- the storefront remains usable
- the gateway is visible and demonstrable
- the AI service is clearly separated
- the service topology can be explained with confidence
