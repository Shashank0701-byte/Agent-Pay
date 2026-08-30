# AgentPay --- API Specification

**Version:** v1\
**Base URL:** `/api/v1`

------------------------------------------------------------------------

## 1. API Conventions

### Authentication

Agent APIs:

``` http
Authorization: Bearer <agent_api_key>
```

Dashboard APIs should use user/session authentication.

### Content Type

``` http
Content-Type: application/json
```

### IDs

Use opaque IDs.

Examples:

``` text
usr_xxx
agt_xxx
pay_xxx
apr_xxx
txn_xxx
```

### Timestamps

Use UTC ISO-8601 timestamps.

------------------------------------------------------------------------

# 2. Agent APIs

## POST `/agents`

Create an agent.

### Request

``` json
{
  "name": "DevOps Agent"
}
```

### Response

``` json
{
  "id": "agt_123",
  "name": "DevOps Agent",
  "status": "active",
  "api_key": "ap_live_xxx",
  "created_at": "2026-08-31T00:00:00Z"
}
```

The API key should be returned only at creation/rotation time.

------------------------------------------------------------------------

## GET `/agents`

List user's agents.

### Response

``` json
{
  "data": [
    {
      "id": "agt_123",
      "name": "DevOps Agent",
      "status": "active",
      "created_at": "2026-08-31T00:00:00Z"
    }
  ]
}
```

------------------------------------------------------------------------

## GET `/agents/{agent_id}`

Get agent details.

------------------------------------------------------------------------

## PATCH `/agents/{agent_id}`

Update agent.

``` json
{
  "name": "Production DevOps Agent",
  "status": "active"
}
```

------------------------------------------------------------------------

## POST `/agents/{agent_id}/rotate-key`

Rotate the API key.

### Response

``` json
{
  "api_key": "ap_live_new_key"
}
```

Old credentials become invalid according to the configured rotation
policy.

------------------------------------------------------------------------

# 3. Policy APIs

## GET `/agents/{agent_id}/policy`

Get spending policy.

### Response

``` json
{
  "agent_id": "agt_123",
  "monthly_limit": 10000,
  "auto_approve_limit": 500,
  "max_transaction": 2000,
  "allowed_categories": [
    "software",
    "cloud",
    "api"
  ],
  "blocked_categories": [
    "gambling",
    "crypto"
  ]
}
```

------------------------------------------------------------------------

## PUT `/agents/{agent_id}/policy`

Replace policy.

### Request

``` json
{
  "monthly_limit": 10000,
  "auto_approve_limit": 500,
  "max_transaction": 2000,
  "allowed_categories": [
    "software",
    "cloud",
    "api"
  ],
  "blocked_categories": [
    "gambling",
    "crypto"
  ]
}
```

------------------------------------------------------------------------

# 4. Payment Request APIs

## POST `/payments/requests`

Create a payment request.

### Authentication

Agent API key.

### Headers

``` http
Authorization: Bearer <agent_api_key>
Idempotency-Key: <unique-key>
```

### Request

``` json
{
  "amount": 1500,
  "currency": "INR",
  "merchant": "Supabase",
  "reason": "Production PostgreSQL database",
  "category": "software",
  "metadata": {
    "task_id": "deploy_123"
  }
}
```

### Validation

-   amount must be positive
-   currency must be supported
-   merchant is required
-   reason is required
-   category must be valid
-   idempotency key is required

### Possible response --- auto-approved

``` json
{
  "id": "pay_123",
  "status": "approved",
  "decision": "auto_approved",
  "amount": 300,
  "currency": "INR"
}
```

### Possible response --- human approval

``` json
{
  "id": "pay_123",
  "status": "approval_required",
  "decision": "human_approval",
  "amount": 1500,
  "currency": "INR",
  "approval_id": "apr_123"
}
```

### Possible response --- denied

``` json
{
  "id": "pay_123",
  "status": "denied",
  "decision": "denied",
  "reason": "Amount exceeds maximum transaction limit"
}
```

------------------------------------------------------------------------

## GET `/payments/requests/{payment_id}`

Get payment request status.

### Response

``` json
{
  "id": "pay_123",
  "agent_id": "agt_123",
  "amount": 1500,
  "currency": "INR",
  "merchant": "Supabase",
  "reason": "Production PostgreSQL database",
  "status": "paid",
  "decision": "human_approval",
  "transaction_id": "txn_123",
  "created_at": "2026-08-31T00:00:00Z",
  "updated_at": "2026-08-31T00:02:00Z"
}
```

------------------------------------------------------------------------

## POST `/payments/requests/{payment_id}/cancel`

Cancel a cancellable request.

### Response

``` json
{
  "id": "pay_123",
  "status": "cancelled"
}
```

------------------------------------------------------------------------

# 5. Approval APIs

## GET `/approvals`

List pending approvals.

### Query parameters

``` text
status=pending
agent_id=agt_123
```

### Response

``` json
{
  "data": [
    {
      "id": "apr_123",
      "payment_id": "pay_123",
      "agent_id": "agt_123",
      "amount": 1500,
      "currency": "INR",
      "merchant": "Supabase",
      "reason": "Production database",
      "status": "pending"
    }
  ]
}
```

------------------------------------------------------------------------

## GET `/approvals/{approval_id}`

Get approval details.

------------------------------------------------------------------------

## POST `/approvals/{approval_id}/approve`

Approve a payment request.

### Response

``` json
{
  "approval_id": "apr_123",
  "payment_id": "pay_123",
  "status": "approved"
}
```

This action must be authorized for the owner of the agent.

------------------------------------------------------------------------

## POST `/approvals/{approval_id}/deny`

Deny a payment request.

### Request

``` json
{
  "reason": "Not required"
}
```

------------------------------------------------------------------------

# 6. Transaction APIs

## GET `/transactions`

List transactions.

### Query parameters

``` text
agent_id
status
from
to
limit
cursor
```

### Response

``` json
{
  "data": [
    {
      "id": "txn_123",
      "payment_id": "pay_123",
      "agent_id": "agt_123",
      "merchant": "Supabase",
      "amount": 1500,
      "currency": "INR",
      "status": "paid",
      "razorpay_payment_id": "pay_provider_123",
      "created_at": "2026-08-31T00:00:00Z"
    }
  ]
}
```

------------------------------------------------------------------------

## GET `/transactions/{transaction_id}`

Return transaction details.

------------------------------------------------------------------------

# 7. Budget APIs

## GET `/agents/{agent_id}/budget`

### Response

``` json
{
  "monthly_limit": 10000,
  "spent": 2300,
  "remaining": 7700,
  "currency": "INR"
}
```

------------------------------------------------------------------------

# 8. Webhook API

## POST `/webhooks/razorpay`

This endpoint is called by Razorpay.

### Processing requirements

1.  Read raw request body.
2.  Verify webhook signature.
3.  Extract provider event ID.
4.  Check whether event was already processed.
5.  Persist event.
6.  Update internal transaction state.
7.  Write audit log.
8.  Signal agent runtime.
9.  Return successful response.

### Important

Webhook processing must be idempotent.

------------------------------------------------------------------------

# 9. Agent Runtime APIs

## GET `/agent/payments/{payment_id}/wait`

Optional long-polling interface for the SDK.

The SDK can also poll:

``` http
GET /payments/requests/{payment_id}
```

A future version can use WebSockets or server-sent events.

------------------------------------------------------------------------

# 10. Error Format

All errors should follow:

``` json
{
  "error": {
    "code": "PAYMENT_LIMIT_EXCEEDED",
    "message": "Payment exceeds the agent's maximum transaction limit",
    "request_id": "req_123"
  }
}
```

------------------------------------------------------------------------

# 11. Error Codes

Recommended initial codes:

``` text
UNAUTHORIZED
FORBIDDEN
AGENT_NOT_FOUND
AGENT_DISABLED

INVALID_AMOUNT
INVALID_CURRENCY
INVALID_CATEGORY

PAYMENT_NOT_FOUND
PAYMENT_ALREADY_PROCESSED
PAYMENT_NOT_CANCELLABLE

BUDGET_EXCEEDED
TRANSACTION_LIMIT_EXCEEDED
CATEGORY_BLOCKED

APPROVAL_NOT_FOUND
APPROVAL_EXPIRED
APPROVAL_ALREADY_RESOLVED

RAZORPAY_ERROR
WEBHOOK_SIGNATURE_INVALID
WEBHOOK_ALREADY_PROCESSED

IDEMPOTENCY_CONFLICT
RATE_LIMITED
INTERNAL_ERROR
```

------------------------------------------------------------------------

# 12. SDK-Level Interface

The first SDK can expose:

``` python
from agentpay import AgentPay

client = AgentPay(api_key="...")

payment = client.request_payment(
    amount=1500,
    currency="INR",
    merchant="Supabase",
    reason="Production database",
    category="software"
)

result = client.wait_for_payment(payment.id)

if result.status == "paid":
    continue_task()
```

The SDK should hide HTTP details from the agent.

------------------------------------------------------------------------

# 13. Example Agent Tool Definitions

An LLM agent can be given tools conceptually like:

``` text
request_payment
check_payment_status
search_products
```

### request_payment

``` json
{
  "name": "request_payment",
  "description": "Request an authorized payment through AgentPay.",
  "parameters": {
    "amount": "number",
    "currency": "string",
    "merchant": "string",
    "reason": "string",
    "category": "string"
  }
}
```

The model does not receive:

-   Razorpay secrets
-   database credentials
-   provider authentication secrets

------------------------------------------------------------------------

# 14. API Versioning

All public APIs should start with:

``` text
/api/v1
```

Avoid breaking changes inside v1.

Future:

``` text
/api/v2
```

------------------------------------------------------------------------

# 15. API Development Order

Implement in this order:

1.  Agent creation
2.  Agent authentication
3.  Policy read/write
4.  Payment request
5.  Policy evaluation
6.  Approval endpoints
7.  Transaction endpoints
8.  Mock payment provider
9.  Razorpay provider
10. Webhook
11. SDK
12. Agent runtime
