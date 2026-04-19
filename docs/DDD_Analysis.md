# DDD Analysis: NovaMarket Multi-category E-commerce

## Goal

This document formalizes the domain decomposition for `NovaMarket` while the codebase is being split into increasingly independent microservices.

The main objective is to make service boundaries defensible from a Domain-Driven Design perspective, not from a purely technical or UI-driven perspective.

## Core domain

The core business capability of `NovaMarket` is:

- discovering products,
- selecting the right products,
- converting interest into a valid order,
- orchestrating payment and shipping,
- augmenting the buying journey with AI recommendations.

The core domain is therefore not "website pages" or "product types". It is the end-to-end commerce flow.

## Subdomains

### Core subdomains

- `Product`
  - owns product discovery and product information
  - drives search, listing, detail views, featured products

- `Cart`
  - owns a customer's active shopping selection
  - prepares the transition from browsing to checkout

- `Ordering`
  - owns order creation and lifecycle
  - is the source of truth for purchase intent becoming a confirmed transaction

### Supporting subdomains

- `Identity & Access`
  - owns users, roles, authentication, staff access, customer identity

- `Payment`
  - owns payment status and payment confirmation records
  - should not own the order itself

- `Shipping`
  - owns shipment preparation and delivery status
  - depends on a valid order but remains a separate responsibility

- `AI Assistant`
  - owns recommendation and conversational guidance
  - should read product knowledge, not mutate transactional state

### Generic subdomains

- `Gateway / Edge`
  - request routing
  - request tracing
  - service aggregation and public API exposure

- `Observability / Platform`
  - logs, metrics, health checks, deployment concerns

## Bounded contexts

## 1. Identity Context

Responsibilities:

- user authentication
- role assignment
- access rules for `Admin`, `Staff`, `Customer`
- staff dashboard access

Key entities:

- `User`
- `Role`
- `Session` or `Auth Token`

Boundaries:

- does not own orders
- does not own products
- provides identity claims to other services

## 2. Product Context

Responsibilities:

- categories
- products
- product brand and description
- stock visibility snapshot
- featured products

Key entities:

- `Category`
- `Product`

Boundaries:

- does not own cart state
- does not own order confirmation
- exposes read models for browsing and recommendation

## 3. Cart Context

Responsibilities:

- active shopping cart
- line items
- quantity adjustments
- running subtotal

Key entities:

- `Cart`
- `CartItem`

Boundaries:

- cart is temporary and mutable
- once checkout succeeds, order becomes the long-lived transactional record

## 4. Ordering Context

Responsibilities:

- checkout
- order creation
- order lifecycle
- order line snapshot

Key entities:

- `Order`
- `OrderItem`

Boundaries:

- owns the confirmed purchase record
- delegates payment state to `Payment`
- delegates shipment state to `Shipping`

## 5. Payment Context

Responsibilities:

- payment attempts
- payment confirmation
- payment provider reference

Key entities:

- `PaymentRecord`

Boundaries:

- tied to an order
- does not rewrite order ownership

## 6. Shipping Context

Responsibilities:

- shipping address
- delivery method
- shipment state

Key entities:

- `Shipment`

Boundaries:

- depends on order existence
- should not own commercial pricing logic

## 7. AI Assistant Context

Responsibilities:

- recommendation
- guided discovery
- lightweight RAG or rule-based matching
- product knowledge interpretation

Key entities:

- `Prompt`
- `RecommendationResult`
- `KnowledgeEntry`

Boundaries:

- reads catalog knowledge
- does not directly write into cart, order, payment, or shipping

## Context map

### Upstream / downstream relationships

- `Product` -> upstream to `Cart`, `Ordering`, `AI Assistant`
- `Cart` -> upstream to `Ordering`
- `Ordering` -> upstream to `Payment`, `Shipping`
- `Identity` -> upstream to `Dashboard`, `Ordering`, `Gateway`
- `AI Assistant` -> downstream from `Product`
- `Gateway` -> edge layer in front of all public service interactions

### Relationship summary

- `Product` provides canonical product read models.
- `Cart` consumes catalog references but owns only cart state.
- `Ordering` consumes cart output and creates immutable order line snapshots.
- `Payment` and `Shipping` attach operational states to an order.
- `Gateway` exposes a stable public surface and hides service topology.

## Service mapping

The target microservice mapping is:

- `identity-service`
- `product-service`
- `cart-service`
- `ordering-service`
- `payment-service`
- `shipping-service`
- `ai-service`
- `api-gateway`
- optional `web-storefront`

## Practical implementation note

The current codebase already exposes `product-service`, `cart-service`, `ordering-service`, `payment-service`, `shipping-service`, `ai-service`, and `api-gateway`, while the storefront experience still lives in a consolidated Django runtime.

This means:

- the code can keep moving now,
- the report can describe the real decomposition already visible in runtime,
- and the current implementation now enforces database-per-service boundaries without redesigning the domain from scratch.
