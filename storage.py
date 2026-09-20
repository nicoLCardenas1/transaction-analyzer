"""
storage.py
----------
Data structures and storage/retrieval functions for transaction records.

Section 4.3 requires data structures that can store valid transactions, 
access transaction details, and group transactions by account ID so the fraud 
rules can process them efficiently.

Two structures are used:

valid_transactions: a list of dictionaries, with one dictionary for each valid transaction. 
It keeps the transactions in the same order as they appear in the file.
transactions_by_account: a dictionary that links each account ID to a list of its transactions. 
This makes it easier and faster to find all transactions belonging to a specific account.

Advanced Feature 3 (Section 5.3, Advanced Transaction Storage and Management) 
adds a separate store for suspicious transactions and accounts. 
It also includes helper functions that allow the stored records to be searched, filtered, and updated.
"""

"""Turn a validated, stripped list of fields into a transaction dict."""
def build_transaction_record(line_number, fields):
    
    (timestamp, transaction_id, account_id, transaction_type,
     amount, location, status) = fields
    return {
        "line_number": line_number,
        "timestamp": timestamp,
        "transaction_id": transaction_id,
        "account_id": account_id,
        "transaction_type": transaction_type,
        "amount": float(amount),
        "location": location,
        "status": status,
    }

"""Add a validated transaction record to both storage structures."""
def store_transaction(record, valid_transactions, transactions_by_account):
    valid_transactions.append(record)
    transactions_by_account.setdefault(record["account_id"], []).append(record)

"""Return the transaction dictionary with this transaction_id, or None."""
def search_by_transaction_id(valid_transactions, transaction_id):
    for record in valid_transactions:
        if record["transaction_id"] == transaction_id:
            return record
    return None


"""Return the list of transactions for an account (empty list if none)."""
def search_by_account_id(transactions_by_account, account_id): 
    return transactions_by_account.get(account_id, [])


"""
Returns transactions that match the selected criteria. Any criteria set to None 
are ignored, allowing the function to filter by type, status, location, or 
a combination of them.
"""
def filter_transactions(valid_transactions, transaction_type=None, status=None, location=None):
    
    results = valid_transactions
    if transaction_type is not None:
        results = [r for r in results if r["transaction_type"] == transaction_type]
    if status is not None:
        results = [r for r in results if r["status"] == status]
    if location is not None:
        results = [r for r in results if r["location"] == location]
    return results


"""Stores suspicious transactions or accounts separately from valid transactions. 
The suspicious_store dictionary groups them by the rule that flagged them, such as 
high_value or repeated_declines"""

def store_suspicious(suspicious_store, category, item):
   
    suspicious_store.setdefault(category, []).append(item)
