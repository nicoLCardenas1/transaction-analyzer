"""
main.py

ICT703 Programming - Assessment Task 2
Bank Transaction Fraud Detection System

is the main file of the program. It connects the different parts of the system, 
including reading the transaction file, validating and storing the data, 
detecting fraud, and generating reports.


Implements:
   (Sections 4.1-4.5): read the transaction file, validate records,
      store valid transactions, apply the 3 core fraud-detection rules,
      and display suspicious activity.
  ADVANCED (targeting Distinction / High Distinction):
      5.1 Enhanced Data Validation
      5.2 Time-Based Fraud Detection
      5.3 Advanced Transaction Storage and Management
      5.7 Summary Statistics and Reporting

Run with:   python main.py
If no argument is given, it defaults to 'transactions.csv' in this folder.
"""

import sys

from transaction_reader import read_transaction_file
from validators import validate_enhanced
import storage
import fraud_detector
import reporting

DEFAULT_TRANSACTION_FILE = "transactions.csv"
INVALID_RECORDS_FILE = "invalid_transactions.csv"
SUMMARY_FILE = "summary_report.csv"


def process_transactions(file_path):
    """
    Run the full pipeline: read -> validate -> store -> detect fraud.
    Returns a dictionary with every intermediate and final result, which
    makes the whole pipeline easy to unit-test (see test.py).
    """
    raw_records = read_transaction_file(file_path)

    valid_transactions = []
    transactions_by_account = {}
    invalid_records = []
    seen_transaction_ids = set()

    for line_number, fields in raw_records:
        is_valid, reason = validate_enhanced(fields, line_number, seen_transaction_ids)
        if is_valid:
            cleaned_fields = [f.strip() for f in fields]
            record = storage.build_transaction_record(line_number, cleaned_fields)
            storage.store_transaction(record, valid_transactions, transactions_by_account)
            seen_transaction_ids.add(record["transaction_id"])
        else:
            invalid_records.append({
                "line_number": line_number,
                "fields": fields,
                "reason": reason,
            })

    high_value = fraud_detector.detect_high_value_transactions(valid_transactions)
    repeated_declines = fraud_detector.detect_repeated_declines(transactions_by_account)
    multiple_locations = fraud_detector.detect_multiple_locations(transactions_by_account)
    time_based_declines = fraud_detector.detect_time_based_declines(transactions_by_account)

    # Advanced Feature 3: store suspicious transactions/accounts separately
    # from the valid-transaction store.
    suspicious_store = {}
    for item in high_value:
        storage.store_suspicious(suspicious_store, "high_value", item)
    for item in repeated_declines:
        storage.store_suspicious(suspicious_store, "repeated_declines", item)
    for item in multiple_locations:
        storage.store_suspicious(suspicious_store, "multiple_locations", item)
    for item in time_based_declines:
        storage.store_suspicious(suspicious_store, "time_based_declines", item)

    suspicious_accounts = fraud_detector.get_unique_suspicious_accounts(
        high_value, repeated_declines, multiple_locations, time_based_declines
    )

    summary = reporting.generate_summary(
        total_records=len(raw_records),
        valid_transactions=valid_transactions,
        invalid_records=invalid_records,
        high_value=high_value,
        repeated_declines=repeated_declines,
        multiple_locations=multiple_locations,
        time_based_declines=time_based_declines,
        suspicious_accounts=suspicious_accounts,
    )

    return {
        "raw_records": raw_records,
        "valid_transactions": valid_transactions,
        "transactions_by_account": transactions_by_account,
        "invalid_records": invalid_records,
        "high_value": high_value,
        "repeated_declines": repeated_declines,
        "multiple_locations": multiple_locations,
        "time_based_declines": time_based_declines,
        "suspicious_store": suspicious_store,
        "suspicious_accounts": suspicious_accounts,
        "summary": summary,
    }


def display_results(results):
    print("=" * 60)
    print(" BANK TRANSACTION FRAUD DETECTION SYSTEM")
    print("=" * 60)

    reporting.display_invalid_records(results["invalid_records"])
    reporting.display_high_value_transactions(results["high_value"])
    reporting.display_repeated_declines(results["repeated_declines"])
    reporting.display_multiple_locations(results["multiple_locations"])
    reporting.display_time_based_declines(results["time_based_declines"])
    reporting.display_summary(results["summary"])


def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TRANSACTION_FILE
    results = process_transactions(file_path)
    display_results(results)

    if results["raw_records"]:
        reporting.export_invalid_records_to_csv(results["invalid_records"], INVALID_RECORDS_FILE)
        reporting.export_summary_to_csv(results["summary"], SUMMARY_FILE)


if __name__ == "__main__":
    main()
