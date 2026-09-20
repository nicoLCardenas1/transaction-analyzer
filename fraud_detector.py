"""
fraud_detector.py

Implements the fraud-detection rules.

Rules 1-3 are the CORE rules required by Section 4.4. Rule 4 is ADVANCED 
FEATURE 2 - Time-Based Fraud Detection (Section 5.2). Each rule is its own
function, uses at least two transaction fields, and returns a list of
dictionaries describing what was flagged and why - this keeps the rules
independent, testable, and easy to explain in the report.
"""

from datetime import datetime, timedelta

HIGH_VALUE_THRESHOLD = 5000.00
REPEATED_DECLINE_THRESHOLD = 4
MULTIPLE_LOCATION_THRESHOLD = 3
TIME_WINDOW_DECLINE_THRESHOLD = 4
TIME_WINDOW_MINUTES = 30


def detect_high_value_transactions(valid_transactions, threshold=HIGH_VALUE_THRESHOLD):
    """
    Rule 1 - High-Value Transactions (Section 4.4).
    Flags any transaction that is APPROVED and has an amount > threshold(5000).
    Uses two fields: status and amount.
    """
    flagged = []
    for record in valid_transactions:
        if record["status"] == "APPROVED" and record["amount"] > threshold:
            flagged.append({
                "transaction_id": record["transaction_id"],
                "account_id": record["account_id"],
                "amount": record["amount"],
                "rule": "Rule 1 - High-Value Transaction",
                "reason": (f"Approved amount ${record['amount']:.2f} exceeded the "
                           f"${threshold:,.2f} threshold"),
            })
    return flagged


def detect_repeated_declines(transactions_by_account, threshold=REPEATED_DECLINE_THRESHOLD):
    """
    Rule 2 - Repeated Declined Transactions (Section 4.4).
    Flags an account with 4 or more DECLINED transactions, counted across
    the complete transaction file.
    """
    flagged = []
    for account_id, records in transactions_by_account.items():
        declined = [r for r in records if r["status"] == "DECLINED"]
        if len(declined) >= threshold:
            flagged.append({
                "account_id": account_id,
                "count": len(declined),
                "transaction_ids": [r["transaction_id"] for r in declined],
                "rule": "Rule 2 - Repeated Declined Transactions",
                "reason": f"Account had {len(declined)} declined transactions (threshold: {threshold})",
            })
    return flagged


def detect_multiple_locations(transactions_by_account, threshold=MULTIPLE_LOCATION_THRESHOLD):
    """
    Rule 3 - Multiple Locations (Section 4.4).
    Flags an account whose transactions occur in 3 or more different
    locations, counted across the complete transaction file.
    """
    flagged = []
    for account_id, records in transactions_by_account.items():
        locations = sorted({r["location"] for r in records})
        if len(locations) >= threshold:
            flagged.append({
                "account_id": account_id,
                "num_locations": len(locations),
                "locations": locations,
                "transaction_ids": [r["transaction_id"] for r in records],
                "rule": "Rule 3 - Multiple Locations",
                "reason": (f"Account had transactions in {len(locations)} different "
                           f"locations: {', '.join(locations)}"),
            })
    return flagged


def _parse_timestamp(record):
    return datetime.strptime(record["timestamp"], "%Y-%m-%d %H:%M:%S")


def detect_time_based_declines(transactions_by_account,
                                threshold=TIME_WINDOW_DECLINE_THRESHOLD,
                                window_minutes=TIME_WINDOW_MINUTES):
    """
    Rule 4 (Advanced Feature 2 - Time-Based Fraud Detection, Section 5.2).

    Flags an account when it has 4 or more DECLINED transactions within a rolling time window. 
    The default window is 30 minutes. Unlike Rule 2, which counts all declined transactions 
    in the whole file, Rule 4 only flags transactions that happen close together in time.

    This rule uses two fields: timestamp and status. It is implemented as a separate 
    function and is tested with both suspicious and normal data in test.py.

    """
    flagged = []
    for account_id, records in transactions_by_account.items():
        declined = sorted(
            (r for r in records if r["status"] == "DECLINED"),
            key=_parse_timestamp,
        )
        n = len(declined)
        for start in range(n):
            window_start = _parse_timestamp(declined[start])
            window_end = window_start + timedelta(minutes=window_minutes)
            window_records = [
                r for r in declined[start:]
                if _parse_timestamp(r) <= window_end
            ]
            if len(window_records) >= threshold:
                flagged.append({
                    "account_id": account_id,
                    "count": len(window_records),
                    "transaction_ids": [r["transaction_id"] for r in window_records],
                    "window_start": window_records[0]["timestamp"],
                    "window_end": window_records[-1]["timestamp"],
                    "rule": "Rule 4 - Time-Based Repeated Declines (Advanced)",
                    "reason": (f"Account had {len(window_records)} declined transactions "
                               f"between {window_records[0]['timestamp']} and "
                               f"{window_records[-1]['timestamp']} (within {window_minutes} minutes)"),
                })
                break  # one alert per account is enough; skip overlapping windows
    return flagged


def get_unique_suspicious_accounts(*flagged_lists):
    """
   Collect all suspicious account IDs from the different 
   rules and count each account only once, even if it triggers multiple rules.
    """
    accounts = set()
    for flagged in flagged_lists:
        for item in flagged:
            accounts.add(item["account_id"])
    return accounts
