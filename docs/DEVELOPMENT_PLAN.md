# AgentPay --- Development Plan

**Version:** 0.1\
**Objective:** Build a working hackathon-ready Agentic Commerce
platform.

------------------------------------------------------------------------

# 1. Development Philosophy

Do not build the entire platform before testing the core loop.

The project should be developed as a sequence of vertical slices.

The most important milestone is:

``` text
Agent
 ↓
Payment Request
 ↓
Policy
 ↓
Approval
 ↓
Razorpay
 ↓
Webhook
 ↓
Transaction
 ↓
Agent Resumes
```

Every phase should leave the repository in a runnable state.

------------------------------------------------------------------------

# 2. Milestones

``` text
M0  Architecture
 ↓
M1  Backend foundation
 ↓
M2  Agent identity
 ↓
M3  Payment engine
 ↓
M4  Policy engine
 ↓
M5  Approval system
 ↓
M6  Razorpay integration
 ↓
M7  Webhooks + reliability
 ↓
M8  Agent SDK/runtime
 ↓
M9  Dashboard
 ↓
M10 Autonomous purchasing
 ↓
M11 Demo + submission
```

------------------------------------------------------------------------

# 3. M0 --- Architecture and Repository Setup

### Tasks

-   [ ] Create repository
-   [ ] Create README
-   [ ] Add PRD
-   [ ] Add architecture document
-   [ ] Add API specification
-   [ ] Add development plan
-   [ ] Decide Python version
-   [ ] Decide Node.js version
-   [ ] Define environment variables
-   [ ] Define branch strategy
-   [ ] Create issue/task labels

### Definition of done

A new developer can clone the repository and understand the intended
system.

------------------------------------------------------------------------

# 4. M1 --- Backend Foundation

### Stack

-   Python
-   FastAPI
-   PostgreSQL
-   SQLAlchemy
-   Alembic
-   Pydantic
-   Pytest
-   Docker

### Tasks

-   [ ] Initialize FastAPI
-   [ ] Add health endpoint
-   [ ] Add configuration management
-   [ ] Connect PostgreSQL
-   [ ] Configure SQLAlchemy
-   [ ] Configure Alembic
-   [ ] Create base model
-   [ ] Add structured logging
-   [ ] Add request ID middleware
-   [ ] Add error handling
-   [ ] Add Dockerfile
-   [ ] Add docker-compose
-   [ ] Add CI pipeline

### Definition of done

``` http
GET /health
```

returns a healthy response and the API can connect to PostgreSQL.

------------------------------------------------------------------------

# 5. M2 --- Agent Identity

### Database

Implement:

``` text
users
agents
```

### Tasks

-   [ ] Create user model
-   [ ] Create agent model
-   [ ] Create agent API key generation
-   [ ] Hash API keys
-   [ ] Agent authentication middleware
-   [ ] Agent CRUD
-   [ ] Agent enable/disable
-   [ ] Key rotation

### Tests

-   [ ] Valid API key
-   [ ] Invalid API key
-   [ ] Disabled agent
-   [ ] Missing key
-   [ ] Agent ownership isolation

### Definition of done

An agent can authenticate against AgentPay.

------------------------------------------------------------------------

# 6. M3 --- Budget and Policy Models

Implement:

``` text
wallet/budget
policy
```

### Tasks

-   [ ] Monthly spending limit
-   [ ] Auto-approval threshold
-   [ ] Maximum transaction
-   [ ] Allowed categories
-   [ ] Blocked categories
-   [ ] Current-period spending calculation
-   [ ] Policy CRUD

### Definition of done

A policy can be configured for an agent.

Example:

``` text
Monthly: ₹10,000
Auto: ₹500
Max: ₹2,000
```

------------------------------------------------------------------------

# 7. M4 --- Payment Request Engine

Implement:

``` text
payment_requests
transactions
```

### Tasks

-   [ ] Payment request schema
-   [ ] Payment request service
-   [ ] Input validation
-   [ ] Idempotency
-   [ ] Initial state machine
-   [ ] Transaction creation
-   [ ] Budget check
-   [ ] Merchant metadata
-   [ ] Category handling

### API

``` http
POST /api/v1/payments/requests
GET /api/v1/payments/requests/{id}
```

### Definition of done

An authenticated agent can request a payment and receive a deterministic
decision.

------------------------------------------------------------------------

# 8. M5 --- Policy Engine

Implement deterministic policy evaluation.

### Decision function

``` text
request
   ↓
blocked category?
   ├── yes → DENY
   ↓ no
over max transaction?
   ├── yes → DENY
   ↓ no
over monthly budget?
   ├── yes → DENY
   ↓ no
under auto-approve limit?
   ├── yes → AUTO_APPROVE
   ↓ no
HUMAN_APPROVAL
```

### Tasks

-   [ ] Implement evaluator
-   [ ] Add policy service
-   [ ] Record policy decision
-   [ ] Record decision reason
-   [ ] Unit tests

### Required tests

``` text
₹300 → AUTO_APPROVE
₹500 → AUTO_APPROVE
₹501 → HUMAN_APPROVAL
₹2,001 → DENY
Blocked category → DENY
Budget exceeded → DENY
```

### Definition of done

Policy behavior is deterministic and covered by tests.

------------------------------------------------------------------------

# 9. M6 --- Approval System

Implement:

``` text
approvals
```

### Tasks

-   [ ] Create approval record
-   [ ] Pending approval API
-   [ ] Approve endpoint
-   [ ] Deny endpoint
-   [ ] Approval expiration
-   [ ] Prevent double approval
-   [ ] Authorization checks
-   [ ] Audit events

### Definition of done

A human can approve or deny a payment request.

------------------------------------------------------------------------

# 10. M7 --- Mock Payment Provider

Before Razorpay, build:

``` python
MockPaymentProvider
```

It should support:

``` text
create_order()
capture()
fail()
```

### Why

This lets us test the complete internal payment system without depending
on an external provider.

### Flow

``` text
Payment Request
 ↓
Policy
 ↓
Approval
 ↓
Mock Provider
 ↓
Transaction
```

### Definition of done

The complete payment lifecycle works locally.

------------------------------------------------------------------------

# 11. M8 --- Razorpay Integration

Only now integrate the real payment provider.

### Tasks

-   [ ] Razorpay credentials configuration
-   [ ] Provider abstraction
-   [ ] Razorpay implementation
-   [ ] Order creation
-   [ ] Checkout integration
-   [ ] Internal/provider ID mapping
-   [ ] Payment status handling
-   [ ] Error handling

### Security

Never expose server-side provider secrets to:

-   Agent
-   Browser
-   Frontend bundle
-   Logs

### Definition of done

A user can approve a payment and complete it through Razorpay
test/sandbox infrastructure.

------------------------------------------------------------------------

# 12. M9 --- Webhook Reliability

### Tasks

-   [ ] Webhook endpoint
-   [ ] Raw body capture
-   [ ] Signature verification
-   [ ] Provider event ID storage
-   [ ] Duplicate event detection
-   [ ] Transaction update
-   [ ] Audit event
-   [ ] Agent notification
-   [ ] Retry-safe processing

### Test cases

``` text
Valid webhook
Invalid signature
Duplicate webhook
Unknown payment
Delayed webhook
Repeated webhook
```

### Definition of done

A captured payment reliably becomes:

``` text
PAID
```

inside AgentPay.

------------------------------------------------------------------------

# 13. M10 --- Agent SDK

Build a minimal Python SDK.

### Interface

``` python
client = AgentPay(api_key="...")

payment = client.request_payment(
    amount=1500,
    currency="INR",
    merchant="Supabase",
    reason="Production database",
    category="software"
)

payment = client.wait_for_payment(payment.id)
```

### Tasks

-   [ ] HTTP client
-   [ ] Authentication
-   [ ] Payment request
-   [ ] Payment status
-   [ ] Polling/wait helper
-   [ ] Error types
-   [ ] README examples

### Definition of done

A standalone demo agent can use AgentPay without knowing the internal
API.

------------------------------------------------------------------------

# 14. M11 --- Agent Runtime

Create the first real AI workflow.

### Agent tools

``` text
search_products()
request_payment()
check_payment_status()
```

### Demo agent

The agent receives:

> "Deploy my application."

It discovers a dependency and requests payment.

### Agent state

``` text
RUNNING
WAITING_FOR_PAYMENT
PAYMENT_SUCCESS
PAYMENT_FAILED
COMPLETED
```

### Definition of done

The agent pauses on payment approval and automatically resumes after
payment.

------------------------------------------------------------------------

# 15. M12 --- Dashboard

Use:

-   Next.js
-   TypeScript
-   Tailwind
-   shadcn/ui

### Pages

``` text
/
 /agents
 /approvals
 /transactions
 /policies
```

### Priority

#### P0

-   Approval screen
-   Transaction status
-   Agent status

#### P1

-   Dashboard overview
-   Budget visualization
-   Agent configuration

#### P2

-   Advanced analytics
-   Charts
-   Filters

------------------------------------------------------------------------

# 16. M13 --- Autonomous Commerce

Only after the core system works.

Add a controlled demo catalog.

Example:

``` text
Supabase Pro
₹1,500

Better Uptime
₹500

Resend
₹800
```

Agent gets:

> "Set up the infrastructure for my application under ₹3,000/month."

Agent:

``` text
Analyze requirements
      ↓
Search catalog
      ↓
Compare products
      ↓
Select products
      ↓
Calculate total
      ↓
Request payment
      ↓
Approval
      ↓
Razorpay
```

### Definition of done

Agent makes a commercially meaningful decision before asking for
payment.

------------------------------------------------------------------------

# 17. M14 --- Security Hardening

### Required

-   [ ] Hash API keys
-   [ ] Encrypt sensitive configuration
-   [ ] Strict authorization
-   [ ] Webhook verification
-   [ ] Idempotency
-   [ ] Rate limiting
-   [ ] Input validation
-   [ ] SQL injection protection through ORM/parameterization
-   [ ] No secrets in Git
-   [ ] No secrets in frontend
-   [ ] Audit logs
-   [ ] Secure CORS configuration

### Threat scenarios

Test:

``` text
Agent attempts > budget
Agent attempts blocked category
Agent replays request
Agent replays webhook
User accesses another agent
Agent accesses another agent
Duplicate payment request
Expired approval
```

------------------------------------------------------------------------

# 18. M15 --- Testing

### Unit tests

Focus on:

-   Policy engine
-   State machine
-   Budget calculation
-   Idempotency
-   Authentication
-   Authorization

### Integration tests

Test:

``` text
API → DB
API → Policy
API → Payment Provider
Webhook → DB
```

### End-to-end

One complete test:

``` text
Create agent
 ↓
Configure policy
 ↓
Agent requests ₹1,500
 ↓
Approval required
 ↓
Approve
 ↓
Payment
 ↓
Webhook
 ↓
PAID
```

------------------------------------------------------------------------

# 19. M16 --- Observability

Add:

``` text
request_id
agent_id
payment_id
transaction_id
provider_id
```

Every important log should include enough context to trace one
transaction.

Example:

``` text
[request=req_123]
[agent=agt_123]
[payment=pay_123]
[transaction=txn_123]

payment.captured
```

------------------------------------------------------------------------

# 20. M17 --- Demo Engineering

The hackathon demo should use a deterministic scenario.

### Demo setup

Agent:

``` text
DevOps Agent
```

Policy:

``` text
Monthly limit: ₹10,000
Auto approve: ₹500
Maximum transaction: ₹2,000
```

Catalog:

``` text
Supabase Pro       ₹1,500
Better Uptime      ₹500
Resend             ₹800
```

### Demo command

``` text
"Deploy my application."
```

### Expected flow

``` text
Agent starts
 ↓
Agent identifies database requirement
 ↓
Searches catalog
 ↓
Selects Supabase
 ↓
Requests ₹1,500
 ↓
Policy says approval required
 ↓
Dashboard displays request
 ↓
Human approves
 ↓
Razorpay checkout
 ↓
Payment succeeds
 ↓
Webhook received
 ↓
Agent resumes
 ↓
Agent completes task
```

------------------------------------------------------------------------

# 21. M18 --- Pitch Preparation

The pitch should focus on the problem, not implementation details.

### Suggested narrative

#### 1. Problem

> Agents can think, but they can't safely transact.

#### 2. Example

> Our DevOps agent needs a paid database to finish deployment.

#### 3. Solution

> AgentPay gives the agent a programmable financial interface.

#### 4. Safety

> The agent never receives payment credentials. Policies determine what
> it can spend.

#### 5. Demo

Show the entire transaction.

#### 6. Vision

> Every autonomous agent will eventually need a safe way to participate
> in commerce.

------------------------------------------------------------------------

# 22. Team Task Split

If working as a team:

### Backend Engineer

Own:

``` text
FastAPI
Database
Policy engine
Payment engine
Razorpay
Webhooks
```

### Frontend Engineer

Own:

``` text
Dashboard
Approval UI
Transactions
Policies
Agent status
```

### AI/Agent Engineer

Own:

``` text
Agent runtime
Tool calling
SDK
Product discovery
Agent state
```

### DevOps / Integration

Own:

``` text
Docker
CI/CD
Environment management
Deployment
Logging
Monitoring
```

One person can own multiple areas for a small team.

------------------------------------------------------------------------

# 23. Priority Labels

### P0 --- Must have

``` text
Agent authentication
Payment request
Policy engine
Approval
Razorpay
Webhook
Transaction ledger
Agent status
```

### P1 --- Should have

``` text
Dashboard
SDK
Product catalog
Budget analytics
Audit log UI
```

### P2 --- Nice to have

``` text
Agent-to-agent commerce
Negotiation
Multiple providers
Advanced risk scoring
Recurring purchases
```

------------------------------------------------------------------------

# 24. What We Should Build First

Do NOT begin with the frontend.

The first implementation sequence should be:

``` text
1. Repository
2. FastAPI
3. PostgreSQL
4. User/Agent models
5. Agent API key authentication
6. Policy model
7. Payment request model
8. Policy engine
9. Approval model
10. Mock payment provider
11. Complete mock transaction
12. Razorpay integration
13. Webhook
14. SDK
15. Agent
16. Dashboard
17. Autonomous catalog
18. Polish
```

------------------------------------------------------------------------

# 25. First Vertical Slice

The first major target should be:

``` text
curl
 ↓
AgentPay API
 ↓
Policy Engine
 ↓
HUMAN_APPROVAL
 ↓
Approval API
 ↓
Mock Payment Provider
 ↓
PAID
```

Then replace the mock provider:

``` text
Mock Payment Provider
        ↓
     Razorpay
```

This prevents the project from becoming an untestable collection of
unfinished components.

------------------------------------------------------------------------

# 26. Final Definition of Done

AgentPay is hackathon-ready when:

-   [ ] An AI agent can authenticate.
-   [ ] Agent can request a payment.
-   [ ] Policy engine can approve/deny/escalate.
-   [ ] Human can approve.
-   [ ] Razorpay can process the approved payment.
-   [ ] Webhook is verified.
-   [ ] Transaction becomes PAID.
-   [ ] Agent receives payment result.
-   [ ] Agent resumes its task.
-   [ ] Dashboard shows the complete lifecycle.
-   [ ] Audit trail exists.
-   [ ] Demo can be repeated reliably.
-   [ ] README explains setup and architecture.
-   [ ] Deployment is accessible.
-   [ ] 5-minute pitch is rehearsed.

------------------------------------------------------------------------

# 27. Post-MVP Ideas

After submission:

### Agent-to-agent commerce

``` text
Buyer Agent
    ↕
Merchant Agent
    ↕
AgentPay
```

### Autonomous procurement

``` text
Requirement
 ↓
Search
 ↓
Compare
 ↓
Negotiate
 ↓
Purchase
```

### Organization-level controls

``` text
Company
 ├── Engineering Agent
 ├── Marketing Agent
 └── Finance Agent
```

Each gets different policies and budgets.

### Risk engine

Add contextual risk scoring:

``` text
Amount
Merchant
Category
Frequency
Agent history
Time
Budget utilization
```

### Agent financial identity

Long-term:

> Give autonomous agents a programmable economic identity without giving
> them unrestricted access to human finances.
