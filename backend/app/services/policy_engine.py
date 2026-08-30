def evaluate_payment(policy: dict, amount: int, category: str) -> dict:
    blocked = set(policy.get("blocked_categories", []))
    allowed = set(policy.get("allowed_categories", []))
    auto_limit = int(policy.get("auto_approve_limit", 500))
    max_transaction = int(policy.get("max_transaction", 2000))

    if category in blocked:
        return {"status": "denied", "decision": "denied", "reason": "blocked_category"}

    if amount > max_transaction:
        return {"status": "denied", "decision": "denied", "reason": "max_transaction_exceeded"}

    if category not in allowed:
        return {"status": "denied", "decision": "denied", "reason": "category_not_allowed"}

    if amount <= auto_limit:
        return {"status": "approved", "decision": "auto_approved", "reason": "within_auto_approve"}

    return {"status": "approval_required", "decision": "human_approval", "reason": "manual_review_required"}
