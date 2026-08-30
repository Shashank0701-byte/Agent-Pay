# AgentPay --- System Architecture

**Version:** 0.1\
**Status:** MVP Architecture

------------------------------------------------------------------------

## 1. Architectural Principle

The most important rule in AgentPay is:

> **AI agents never directly control payment-provider credentials.**

The agent interacts only with AgentPay.

``` text
┌─────────────────┐
│    AI Agent     │
└────────┬────────┘
         │
         │ Agent API Key
         ▼
┌─────────────────┐
│  AgentPay API   │
└────────┬────────┘
         │
         ├───────────────┐
         ▼               ▼
┌────────────────┐  ┌───────────────┐
│ Policy Engine  │  │ Payment Engine│
└───────┬────────┘  └───────┬───────┘
        │                   │
        ▼                   ▼
┌───────────────┐     ┌───────────┐
│ Approval       │     │ Razorpay  │
│ Service        │     └─────┬─────┘
└───────┬────────┘           │
        │                    │ Webhook
        └──────────┬─────────┘
                   ▼
            ┌──────────────┐
            │ PostgreSQL   │
            └──────────────┘
```

------------------------------------------------------------------------

## 2. High-Level Components

### 2.1 Agent Runtime

Responsible for:

-   LLM interaction
-   Tool calling
-   Task state
-   Payment request generation
-   Waiting for payment results
-   Continuing execution

The runtime can use any tool-calling-capable model.

------------------------------------------------------------------------

### 2.2 AgentPay API

Central entry point.

Responsibilities:

-   Authentication
-   Request validation
-   Agent management
-   Payment requests
-   Approval APIs
-   Payment status
-   Webhooks
-   Rate limiting

Recommended framework:

**FastAPI**

------------------------------------------------------------------------

### 2.3 Policy Engine

Pure business-logic layer.

Responsibilities:

-   Transaction amount checks
-   Monthly budget checks
-   Category checks
-   Merchant checks
-   Approval thresholds
-   Denial rules

The policy engine should be deterministic in the MVP.

------------------------------------------------------------------------

### 2.4 Payment Engine

Abstract payment-provider operations behind an internal interface.

Conceptually:

``` python
class PaymentProvider:
    def create_order(...):
        ...

    def verify_webhook(...):
        ...

    def get_payment(...):
        ...
```

Razorpay is the first implementation.

This keeps AgentPay provider-agnostic.

------------------------------------------------------------------------

### 2.5 Approval Service

Responsibilities:

-   Create approval requests
-   Track approval state
-   Expire approvals
-   Approve
-   Deny
-   Emit events

------------------------------------------------------------------------

### 2.6 Transaction Service

Owns the financial state machine.

Responsibilities:

-   Create internal transactions
-   Update payment status
-   Map provider IDs
-   Enforce idempotency
-   Record timestamps

------------------------------------------------------------------------

### 2.7 Audit Service

Records immutable-style business events.

Every important action should create an audit record.

------------------------------------------------------------------------

### 2.8 Dashboard

Next.js application.

Responsibilities:

-   Agent management
-   Approval UI
-   Transaction history
-   Policy configuration
-   Budget visualization
-   Live status

------------------------------------------------------------------------

### 2.9 PostgreSQL

Primary source of truth for:

-   Users
-   Agents
-   Policies
-   Wallet/budget data
-   Payment requests
-   Approvals
-   Transactions
-   Audit logs

------------------------------------------------------------------------

### 2.10 Redis

Use for:

-   Short-lived state
-   Background jobs
-   Rate limiting
-   Event coordination
-   Future agent execution queues

Redis is optional for the first vertical slice but recommended for the
architecture.

------------------------------------------------------------------------

## 3. Request Lifecycle

### Step 1 --- Agent authenticates

``` text
Authorization: Bearer <agent_api_key>
```

API key maps to an agent.

------------------------------------------------------------------------

### Step 2 --- Agent requests payment

``` http
POST /v1/payments/requests
```

AgentPay validates:

-   Agent identity
-   Amount
-   Currency
-   Merchant
-   Reason
-   Category
-   Idempotency key

------------------------------------------------------------------------

### Step 3 --- Policy evaluation

``` text
Payment Request
      ↓
Policy Engine
      ↓
┌──────────────┬───────────────┬──────────┐
│ AUTO_APPROVE │ HUMAN_APPROVAL│ DENY     │
└──────────────┴───────────────┴──────────┘
```

------------------------------------------------------------------------

### Step 4A --- Auto approval

Create provider payment/order and continue.

------------------------------------------------------------------------

### Step 4B --- Human approval

Create approval request.

Dashboard displays it.

User approves or denies.

------------------------------------------------------------------------

### Step 5 --- Provider execution

Payment Engine calls Razorpay.

Internal database stores:

``` text
internal_request_id
razorpay_order_id
razorpay_payment_id
```

------------------------------------------------------------------------

### Step 6 --- Webhook

Razorpay sends an event.

AgentPay:

1.  Validates signature.
2.  Checks event/idempotency.
3.  Maps provider IDs.
4.  Updates transaction state.
5.  Writes audit event.
6.  Signals agent runtime.

------------------------------------------------------------------------

### Step 7 --- Agent continuation

Agent queries or receives:

``` json
{
  "status": "paid",
  "transaction_id": "txn_123"
}
```

It continues its original task.

------------------------------------------------------------------------

## 4. Service Boundaries

Recommended logical separation:

``` text
API Layer
    ↓
Application Services
    ↓
Domain Logic
    ↓
Repositories
    ↓
Database
```

Example:

``` text
routes/payments.py
        ↓
services/payment_service.py
        ↓
services/policy_service.py
        ↓
repositories/payment_repository.py
        ↓
PostgreSQL
```

Do not put business logic directly inside route handlers.

------------------------------------------------------------------------

## 5. Database Relationships

``` text
User
 │
 └──< Agent
       │
       ├── Wallet/Budget
       │
       ├── Policy
       │
       ├── PaymentRequest
       │       │
       │       ├── Approval
       │       └── Transaction
       │
       └── AuditLog
```

------------------------------------------------------------------------

## 6. Payment State Machine

``` text
CREATED
   ↓
EVALUATING
   │
   ├───────────────┐
   ▼               ▼
DENIED       APPROVAL_REQUIRED
                   │
             ┌─────┴─────┐
             ▼           ▼
          DENIED      APPROVED
                         │
                         ▼
                     PROCESSING
                         │
                   ┌─────┴─────┐
                   ▼           ▼
                 PAID        FAILED
```

Possible terminal states:

``` text
PAID
DENIED
FAILED
EXPIRED
CANCELLED
```

------------------------------------------------------------------------

## 7. Idempotency

Every payment request must support an idempotency key.

Example:

``` http
Idempotency-Key: agent-123-task-456-payment-1
```

If the agent retries the request:

``` text
Request #1 → creates payment request
Request #2 → returns existing request
Request #3 → returns existing request
```

Never create multiple financial actions from a single logical request.

Webhook handling must also be idempotent.

------------------------------------------------------------------------

## 8. Security Architecture

### Agent credentials

Store only hashed API keys.

``` text
Raw API key
    ↓
Hash
    ↓
Database
```

The raw key should be shown only at creation/rotation time.

### Provider credentials

Razorpay credentials remain server-side.

``` text
Agent ✗
Frontend ✗
Database plaintext ✗

Backend secret store ✓
```

### Webhook security

Verify the provider's webhook signature before processing the event.

Never trust the webhook payload solely because it came to the correct
endpoint.

### Authorization

An agent may access only resources belonging to its owner.

------------------------------------------------------------------------

## 9. Reliability

### Database is source of truth

Do not rely on in-memory payment state.

### Webhooks are asynchronous

The system must tolerate:

-   duplicate webhook
-   delayed webhook
-   out-of-order events
-   webhook retry
-   provider timeout

### Event processing

Recommended pattern:

``` text
Webhook
  ↓
Verify
  ↓
Persist raw event / event ID
  ↓
Process once
  ↓
Update transaction
  ↓
Emit internal event
```

------------------------------------------------------------------------

## 10. Deployment Architecture

MVP:

``` text
                    Internet
                       │
                       ▼
                 ┌───────────┐
                 │ Next.js   │
                 └─────┬─────┘
                       │
                       ▼
                 ┌───────────┐
                 │ FastAPI   │
                 └─────┬─────┘
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
        PostgreSQL   Redis    Razorpay
```

Everything should be containerized.

Recommended containers:

``` text
agentpay-api
agentpay-worker
agentpay-web
postgres
redis
```

For the hackathon, Postgres and Redis can alternatively be managed
services.

------------------------------------------------------------------------

## 11. Observability

Minimum:

-   structured logs
-   request IDs
-   transaction IDs
-   agent IDs
-   error logs
-   webhook logs

Useful correlation:

``` text
request_id
agent_id
payment_request_id
transaction_id
provider_order_id
```

A single demo transaction should be traceable across the entire system.

------------------------------------------------------------------------

## 12. Recommended Repository Structure

``` text
agentpay/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── integrations/
│   │   │   └── razorpay/
│   │   └── main.py
│   ├── tests/
│   ├── alembic/
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   ├── components/
│   └── lib/
│
├── agent-sdk/
│   ├── agentpay/
│   └── tests/
│
├── worker/
│
├── docs/
│
├── docker-compose.yml
└── README.md
```

------------------------------------------------------------------------

## 13. Architectural Priorities

Priority order:

1.  Correct financial state transitions
2.  Secure authorization
3.  Webhook reliability
4.  Policy correctness
5.  Agent integration
6.  Dashboard UX
7.  Advanced autonomy

The payment path must be reliable before advanced AI features are added.
