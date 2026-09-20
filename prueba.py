transacciones = [
    {"transaction_id": "T1001", "account_id": "A10025", "amount": 850.00, "status": "APPROVED"},
    {"transaction_id": "T1002", "account_id": "A10025", "amount": 6500.00, "status": "APPROVED"},
    {"transaction_id": "T1003", "account_id": "A10025", "amount": 9000.00, "status": "DECLINED"},
]

HIGH_VALUE_THRESHOLD = 5000.00

flagged = []
for record in transacciones:
    if record["status"] == "APPROVED" and record["amount"] > HIGH_VALUE_THRESHOLD:
        flagged.append({
            "transaction_id": record["transaction_id"],
            "account_id": record["account_id"],
            "amount": record["amount"],
            "rule": "Rule 1 - High-Value Transaction",
            "reason": f"Approved amount ${record['amount']:.2f} exceeded the ${HIGH_VALUE_THRESHOLD:,.2f} threshold",
        })

print(flagged)