"""
validators.py
This module contains the validation functions for the Bank Transaction Fraud Detection System.

It has two levels of validation:

validate_core(): checks the basic requirements, such as the correct number of fields, 
required fields, valid transaction types and statuses, and a positive numeric amount.

validate_enhanced(): adds stricter checks, including the correct format of each field, 
valid dates and times, duplicate transaction IDs, and extra whitespace.

The two functions are kept separate so the core validation can be tested independently. 
The enhanced validation includes all the core checks and adds the extra data-quality 
checks required for Advanced Feature 1.

"""

import re
from datetime import datetime

FIELD_COUNT = 7

VALID_TRANSACTION_TYPES = {
    "TRANSFER", "CARD_PAYMENT", "CASH_WITHDRAWAL",
    "ONLINE_PURCHASE", "DIRECT_DEBIT",
}
VALID_STATUSES = {"APPROVED", "DECLINED", "PENDING"}
# Expected timestamp format: YYYY-MM-DD HH:MM:SS (e.x. "2026-07-11 09:15:23")
# Used with datetime.strptime() to check the timestamp is a real, valid date and time.
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

# Transaction ID must start with "T" followed by exactly 4 digits (e.g. "T1001").
# Matches: "T1001". Does not match: "T101", "T10011", "TX001".
TRANSACTION_ID_PATTERN = re.compile(r"^T\d{4}$")

# Account ID must start with "A" followed by exactly 5 digits (e.g. "A10025").
# Matches: "A10025". Does not match: "A1002", "B10025".
ACCOUNT_ID_PATTERN = re.compile(r"^A\d{5}$")

# Amount must be one or more digits, optionally followed by a decimal point
# and 1 or 2 more digits (e.g. "850", "850.5", "850.00").
# Matches: "850", "850.5", "850.00". Does not match: "850.005", "-50.00", "abc".
AMOUNT_PATTERN = re.compile(r"^\d+(\.\d{1,2})?$")




"""Removes one space at the beginning and end of each field caused by 
the "field | field" formatting. These spaces are part of the file format, so they 
should not be treated as a whitespace error"""
def _strip_delimiter_spacing(field):
    if field.startswith(" "):
        field = field[1:]
    if field.endswith(" "):
        field = field[:-1]
    return field


def has_leading_or_trailing_whitespace(fields):
    """
    Return True if any field has whitespace beyond the normal single space
    that surrounds each '|' delimiter - e.g. double spaces, tabs, or a
    value that was typed with accidental extra padding.
    """
    for field in fields:
        after_delimiter_spacing_removed = _strip_delimiter_spacing(field)
        if after_delimiter_spacing_removed != after_delimiter_spacing_removed.strip():
            return True
    return False


def is_valid_timestamp(value):
    """Return True if value matches YYYY-MM-DD HH:MM:SS and is a real date."""
    try:
        datetime.strptime(value, TIMESTAMP_FORMAT)
        return True
    except ValueError:
        return False


"""Core validation (Section 4.2).

Checks that the record has the correct number of fields, 
required fields are not empty, the transaction type and status are valid, and the 
amount is a positive number.

Returns whether the record is valid and, if it is not valid, gives the reason.
"""
def validate_core(fields, line_number):
   
    if len(fields) != FIELD_COUNT:
        return False, f"Expected {FIELD_COUNT} fields, found {len(fields)}"

    (timestamp, transaction_id, account_id, transaction_type,
     amount_str, location, status) = [f.strip() for f in fields]

    if not transaction_id:
        return False, "Transaction ID is empty"
    if not account_id:
        return False, "Account ID is empty"
    if transaction_type not in VALID_TRANSACTION_TYPES:
        return False, f"Invalid transaction type '{transaction_type}'"
    if status not in VALID_STATUSES:
        return False, f"Invalid status '{status}'"
    try:
        amount = float(amount_str)
    except ValueError:
        return False, f"Amount '{amount_str}' is not numeric"
    if amount <= 0:
        return False, f"Amount {amount} is not greater than zero"

    return True, None


def validate_enhanced(fields, line_number, seen_transaction_ids):
    """
    Enhanced validation (Advanced Feature 1, Section 5.1).

    seen_transaction_ids is the set of transaction IDs already accepted as
    valid so far; the caller is responsible for adding each newly-accepted
    ID to that set. Returns (is_valid, reason).
    """
    if len(fields) != FIELD_COUNT:
        return False, f"Expected {FIELD_COUNT} fields, found {len(fields)}"

    if has_leading_or_trailing_whitespace(fields):
        return False, "One or more fields contain leading/trailing whitespace"

    # Remove the normal single-space padding produced by the " | "
    # delimiter convention before checking each field's own format.
    (timestamp, transaction_id, account_id, transaction_type,
     amount_str, location, status) = [_strip_delimiter_spacing(f) for f in fields]

    if not is_valid_timestamp(timestamp):
        return False, f"Timestamp '{timestamp}' does not match YYYY-MM-DD HH:MM:SS"
    if not TRANSACTION_ID_PATTERN.match(transaction_id):
        return False, f"Transaction ID '{transaction_id}' must be 'T' followed by 4 digits"
    if not ACCOUNT_ID_PATTERN.match(account_id):
        return False, f"Account ID '{account_id}' must be 'A' followed by 5 digits"
    if transaction_type not in VALID_TRANSACTION_TYPES:
        return False, f"Invalid transaction type '{transaction_type}'"
    if not AMOUNT_PATTERN.match(amount_str):
        return False, f"Amount '{amount_str}' must be a positive number with up to 2 decimal places"
    if float(amount_str) <= 0:
        return False, f"Amount {amount_str} is not greater than zero"
    if not location:
        return False, "Location is empty"
    if status not in VALID_STATUSES:
        return False, f"Invalid status '{status}'"
    if transaction_id in seen_transaction_ids:
        return False, f"Duplicate transaction ID '{transaction_id}'"

    return True, None
