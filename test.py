"""
test.py
This is an automated test suite for the Bank Transaction Fraud Detection System.

It can run without any manual input using python3 test.py. Each test shows the feature 
being tested, the input, the expected result, the actual result, and whether the 
test passed or failed. At the end, the program shows the total number of tests passed. It 
also returns a non-zero status code if any test fails, which can be useful for automated checking.

The tests cover the core requirements from Section 6.2, including 
file reading, data validation, the three core fraud detection rules, and checking that a 
normal account is not flagged.

The tests also cover the advanced features, including enhanced validation, duplicate 
and whitespace checks, time-based fraud detection, advanced storage with 
search and filtering, and summary statistics.

"""

import os
import sys
import tempfile

from transaction_reader import read_transaction_file
from validators import validate_core, validate_enhanced
import storage
import fraud_detector
import reporting
from main import process_transactions

PASS_COUNT = 0
FAIL_COUNT = 0

"""
Record and print the result of one test case: feature/function tested,
test input, expected result, actual result, and pass/fail outcome.
"""
def check(feature, test_input, expected, actual):
    
    global PASS_COUNT, FAIL_COUNT
    outcome = "PASS" if actual == expected else "FAIL"
    if outcome == "PASS":
        PASS_COUNT += 1
    else:
        FAIL_COUNT += 1
    print(f"[{outcome}] {feature}")
    print(f"       Input:    {test_input}")
    print(f"       Expected: {expected}")
    print(f"       Actual:   {actual}")


"""Create a temporary transaction file with the given content and
    return its path. The caller is responsible for deleting it."""
def make_temp_file(content):   
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ---------------------------------------------------------------------------
# 1. File reading (Section 6.2)
# ---------------------------------------------------------------------------

"""It tries to read a valid file """
def test_reading_a_valid_file():
    path = make_temp_file(
        "2026-07-11 09:15:23 | T1001 | A10025 | TRANSFER | 850.00 | Brisbane | APPROVED\n"
    )
    try:
        records = read_transaction_file(path)
        check("Reading a valid transaction file", "1 well-formed line",
              1, len(records))
    finally:
        os.remove(path)


def test_handling_a_missing_file():
    records = read_transaction_file("this_file_does_not_exist_12345.csv")
    check("Handling a missing file", "path that does not exist", [], records)


def test_handling_an_empty_file():
    path = make_temp_file("")
    try:
        records = read_transaction_file(path)
        check("Handling an empty file", "0-byte file", [], records)
    finally:
        os.remove(path)


# ---------------------------------------------------------------------------
# 2. Core validation (Section 6.2)
# ---------------------------------------------------------------------------

def test_rejecting_incorrect_field_count():
    fields = ["2026-07-11 09:15:23", "T1001", "A10025", "TRANSFER", "850.00", "Brisbane"]
    is_valid, reason = validate_core(fields, 1)
    check("Rejecting a record with an incorrect number of fields",
          "6 fields instead of 7", False, is_valid)


def test_rejecting_invalid_transaction_type():
    fields = ["2026-07-11 09:15:23", "T1001", "A10025", "BITCOIN_PURCHASE",
              "850.00", "Brisbane", "APPROVED"]
    is_valid, reason = validate_core(fields, 1)
    check("Rejecting an invalid transaction type",
          "transaction_type='BITCOIN_PURCHASE'", False, is_valid)


def test_rejecting_invalid_status():
    fields = ["2026-07-11 09:15:23", "T1001", "A10025", "TRANSFER",
              "850.00", "Brisbane", "UNKNOWN"]
    is_valid, reason = validate_core(fields, 1)
    check("Rejecting an invalid status value", "status='UNKNOWN'", False, is_valid)


def test_rejecting_non_numeric_amount():
    fields = ["2026-07-11 09:15:23", "T1001", "A10025", "TRANSFER",
              "abc", "Brisbane", "APPROVED"]
    is_valid, reason = validate_core(fields, 1)
    check("Rejecting a non-numeric amount", "amount='abc'", False, is_valid)


def test_rejecting_zero_or_negative_amount():
    fields = ["2026-07-11 09:15:23", "T1001", "A10025", "TRANSFER",
              "-50.00", "Brisbane", "APPROVED"]
    is_valid, reason = validate_core(fields, 1)
    check("Rejecting a zero or negative amount", "amount=-50.00", False, is_valid)


def test_accepting_a_valid_record():
    fields = ["2026-07-11 09:15:23", "T1001", "A10025", "TRANSFER",
              "850.00", "Brisbane", "APPROVED"]
    is_valid, reason = validate_core(fields, 1)
    check("Accepting a fully valid record (core validation)",
          "well-formed record", True, is_valid)


# ---------------------------------------------------------------------------
# 3. Core fraud-detection rules (Section 6.2)
# ---------------------------------------------------------------------------

def test_detecting_high_value_transaction():
    transactions = [
        {"transaction_id": "T1002", "account_id": "A10025", "amount": 6500.00, "status": "APPROVED"},
    ]
    flagged = fraud_detector.detect_high_value_transactions(transactions)
    check("Detecting a high-value approved transaction",
          "APPROVED $6500.00 (threshold $5000)", 1, len(flagged))


def test_high_value_not_flagged_when_declined():
    transactions = [
        {"transaction_id": "T1002", "account_id": "A10025", "amount": 6500.00, "status": "DECLINED"},
    ]
    flagged = fraud_detector.detect_high_value_transactions(transactions)
    check("High-value rule ignores non-approved transactions",
          "DECLINED $6500.00", 0, len(flagged))


def test_detecting_repeated_declines():
    by_account = {
        "A30099": [
            {"transaction_id": f"T{i}", "account_id": "A30099", "status": "DECLINED"}
            for i in range(4)
        ]
    }
    flagged = fraud_detector.detect_repeated_declines(by_account)
    check("Detecting repeated declined transactions",
          "4 DECLINED transactions on one account", 1, len(flagged))


def test_detecting_multiple_locations():
    by_account = {
        "A40077": [
            {"transaction_id": "T1", "account_id": "A40077", "location": "Brisbane"},
            {"transaction_id": "T2", "account_id": "A40077", "location": "Sydney"},
            {"transaction_id": "T3", "account_id": "A40077", "location": "Gold Coast"},
        ]
    }
    flagged = fraud_detector.detect_multiple_locations(by_account)
    check("Detecting transactions from multiple locations",
          "3 different locations on one account", 1, len(flagged))


def test_normal_account_not_flagged():
    by_account = {
        "A50000": [
            {"transaction_id": "T1", "account_id": "A50000", "status": "APPROVED",
             "amount": 40.0, "location": "Maroochydore"},
            {"transaction_id": "T2", "account_id": "A50000", "status": "APPROVED",
             "amount": 55.0, "location": "Maroochydore"},
        ]
    }
    high_value = fraud_detector.detect_high_value_transactions(by_account["A50000"])
    declines = fraud_detector.detect_repeated_declines(by_account)
    locations = fraud_detector.detect_multiple_locations(by_account)
    total_flags = len(high_value) + len(declines) + len(locations)
    check("Confirming a normal account is not incorrectly flagged",
          "2 small approved transactions, same location", 0, total_flags)


# ---------------------------------------------------------------------------
# 4. Advanced Feature 1 - Enhanced Data Validation
# ---------------------------------------------------------------------------

def test_enhanced_rejects_bad_timestamp_format():
    fields = ["11-07-2026 09:15:23", "T1001", "A10025", "TRANSFER",
              "850.00", "Brisbane", "APPROVED"]
    is_valid, reason = validate_enhanced(fields, 1, set())
    check("Enhanced validation rejects a malformed timestamp",
          "timestamp='11-07-2026 09:15:23'", False, is_valid)


def test_enhanced_rejects_bad_transaction_id_format():
    fields = ["2026-07-11 09:15:23", "TX001", "A10025", "TRANSFER",
              "850.00", "Brisbane", "APPROVED"]
    is_valid, reason = validate_enhanced(fields, 1, set())
    check("Enhanced validation rejects a malformed transaction ID",
          "transaction_id='TX001'", False, is_valid)


def test_enhanced_detects_duplicate_transaction_id():
    fields = ["2026-07-11 09:15:23", "T1001", "A10025", "TRANSFER",
              "850.00", "Brisbane", "APPROVED"]
    is_valid, reason = validate_enhanced(fields, 2, {"T1001"})
    check("Enhanced validation detects a duplicate transaction ID",
          "T1001 already seen earlier in the file", False, is_valid)


def test_enhanced_detects_whitespace_issue():
    fields = ["2026-07-11 09:15:23", "T1001", "  A10025", "TRANSFER",
              "850.00", "Brisbane", "APPROVED"]
    is_valid, reason = validate_enhanced(fields, 1, set())
    check("Enhanced validation detects extra leading/trailing whitespace",
          "account_id field has an extra leading space", False, is_valid)


def test_enhanced_accepts_normally_spaced_record():
    # Fields as produced by splitting "a | b | c" on '|' - the normal
    # single-space delimiter padding must NOT be flagged as a whitespace
    # data-quality issue.
    fields = ["2026-07-11 09:15:23 ", " T1001 ", " A10025 ", " TRANSFER ",
              " 850.00 ", " Brisbane ", " APPROVED"]
    is_valid, reason = validate_enhanced(fields, 1, set())
    check("Enhanced validation accepts normal '|' delimiter spacing",
          "fields padded only by the standard ' | ' convention", True, is_valid)


# ---------------------------------------------------------------------------
# 5. Advanced Feature 2 - Time-Based Fraud Detection
# ---------------------------------------------------------------------------

def test_time_based_declines_within_window():
    by_account = {
        "A30099": [
            {"transaction_id": "T1", "account_id": "A30099", "status": "DECLINED",
             "timestamp": "2026-07-11 10:00:00"},
            {"transaction_id": "T2", "account_id": "A30099", "status": "DECLINED",
             "timestamp": "2026-07-11 10:05:00"},
            {"transaction_id": "T3", "account_id": "A30099", "status": "DECLINED",
             "timestamp": "2026-07-11 10:12:00"},
            {"transaction_id": "T4", "account_id": "A30099", "status": "DECLINED",
             "timestamp": "2026-07-11 10:20:00"},
        ]
    }
    flagged = fraud_detector.detect_time_based_declines(by_account)
    check("Time-based rule flags 4 declines within 30 minutes",
          "4 declines between 10:00 and 10:20", 1, len(flagged))


def test_time_based_declines_outside_window_not_flagged():
    by_account = {
        "A60000": [
            {"transaction_id": "T1", "account_id": "A60000", "status": "DECLINED",
             "timestamp": "2026-07-11 09:00:00"},
            {"transaction_id": "T2", "account_id": "A60000", "status": "DECLINED",
             "timestamp": "2026-07-11 12:00:00"},
            {"transaction_id": "T3", "account_id": "A60000", "status": "DECLINED",
             "timestamp": "2026-07-11 15:00:00"},
            {"transaction_id": "T4", "account_id": "A60000", "status": "DECLINED",
             "timestamp": "2026-07-11 18:00:00"},
        ]
    }
    flagged = fraud_detector.detect_time_based_declines(by_account)
    check("Time-based rule ignores declines spread across many hours",
          "4 declines, hours apart", 0, len(flagged))


# ---------------------------------------------------------------------------
# 6. Advanced Feature 3 - Advanced Transaction Storage and Management
# ---------------------------------------------------------------------------

def test_search_by_account_id():
    valid_transactions, by_account = [], {}
    for i, amount in enumerate([10.0, 20.0], start=1):
        record = storage.build_transaction_record(
            i, ["2026-07-11 09:00:00", f"T100{i}", "A10025", "TRANSFER",
                str(amount), "Brisbane", "APPROVED"])
        storage.store_transaction(record, valid_transactions, by_account)
    results = storage.search_by_account_id(by_account, "A10025")
    check("Searching stored transactions by account ID",
          "account A10025 with 2 stored transactions", 2, len(results))


def test_filter_transactions_by_status():
    valid_transactions = [
        {"transaction_type": "TRANSFER", "status": "APPROVED", "location": "Brisbane"},
        {"transaction_type": "TRANSFER", "status": "DECLINED", "location": "Brisbane"},
        {"transaction_type": "CARD_PAYMENT", "status": "DECLINED", "location": "Sydney"},
    ]
    results = storage.filter_transactions(valid_transactions, status="DECLINED")
    check("Filtering stored transactions by status",
          "3 transactions, filter status='DECLINED'", 2, len(results))


# ---------------------------------------------------------------------------
# 7. Advanced Feature 7 - Summary Statistics
# ---------------------------------------------------------------------------

def test_summary_counts_suspicious_account_once():
    accounts = fraud_detector.get_unique_suspicious_accounts(
        [{"account_id": "A30099"}],          # from repeated-declines rule
        [{"account_id": "A30099"}],          # from time-based rule (same account)
        [{"account_id": "A40077"}],          # from multiple-locations rule
    )
    check("An account triggering multiple rules is counted once",
          "A30099 flagged by 2 rules, A40077 flagged by 1", 2, len(accounts))


# ---------------------------------------------------------------------------
# 8. End-to-end pipeline test using the real sample data file
# ---------------------------------------------------------------------------

def test_end_to_end_pipeline_on_sample_data():
    results = process_transactions("transactions.csv")
    summary = results["summary"]
    check("End-to-end pipeline produces the expected suspicious-account count",
          "transactions.csv (27 records)", 4, summary["Total suspicious accounts"])


def run_all_tests():
    tests = [
        test_reading_a_valid_file,
        test_handling_a_missing_file,
        test_handling_an_empty_file,
        test_rejecting_incorrect_field_count,
        test_rejecting_invalid_transaction_type,
        test_rejecting_invalid_status,
        test_rejecting_non_numeric_amount,
        test_rejecting_zero_or_negative_amount,
        test_accepting_a_valid_record,
        test_detecting_high_value_transaction,
        test_high_value_not_flagged_when_declined,
        test_detecting_repeated_declines,
        test_detecting_multiple_locations,
        test_normal_account_not_flagged,
        test_enhanced_rejects_bad_timestamp_format,
        test_enhanced_rejects_bad_transaction_id_format,
        test_enhanced_detects_duplicate_transaction_id,
        test_enhanced_detects_whitespace_issue,
        test_enhanced_accepts_normally_spaced_record,
        test_time_based_declines_within_window,
        test_time_based_declines_outside_window_not_flagged,
        test_search_by_account_id,
        test_filter_transactions_by_status,
        test_summary_counts_suspicious_account_once,
        test_end_to_end_pipeline_on_sample_data,
    ]

    print("=" * 60)
    print(" RUNNING TEST SUITE - Bank Transaction Fraud Detection System")
    print("=" * 60)
    for test in tests:
        test()
        print()

    print("=" * 60)
    print(f" RESULTS: {PASS_COUNT} passed, {FAIL_COUNT} failed, out of {PASS_COUNT + FAIL_COUNT} tests")
    print("=" * 60)

    return FAIL_COUNT == 0


if __name__ == "__main__":
    all_passed = run_all_tests()
    sys.exit(0 if all_passed else 1)
