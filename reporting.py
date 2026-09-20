"""
reporting.py

Console display and summary reporting functions.

Covers Section 4.5 (Display Suspicious Activity) and ADVANCED FEATURE 7 -
Summary Statistics and Reporting (Section 5.7), including exporting the
summary to a CSV file.
"""

import csv


def display_invalid_records(invalid_records):
    """Print a simple message for each rejected record (Section 4.2)."""
    if not invalid_records:
        print("\nNo invalid records found")
        return
    print(f"\n{len(invalid_records)} invalid record(s) rejected:")
    for rec in invalid_records:
        print(f"  Line {rec['line_number']}: {rec['reason']}")


def display_high_value_transactions(flagged):
    print("\n--- Rule 1: High-Value Transactions ---")
    if not flagged:
        print("  None found")
    for item in flagged:
        print(f"  Transaction {item['transaction_id']} (Account {item['account_id']}): "
              f"${item['amount']:.2f} -> {item['reason']}")


def display_repeated_declines(flagged):
    print("\n--- Rule 2: Repeated Declined Transactions ---")
    if not flagged:
        print("  None found.")
    for item in flagged:
        print(f"  Account {item['account_id']}: {item['count']} declines "
              f"({', '.join(item['transaction_ids'])}) -> {item['reason']}")


def display_multiple_locations(flagged):
    print("\n--- Rule 3: Multiple Locations ---")
    if not flagged:
        print("  None found.")
    for item in flagged:
        print(f"  Account {item['account_id']}: {item['num_locations']} locations "
              f"({', '.join(item['locations'])}) -> {item['reason']}")


def display_time_based_declines(flagged):
    print("\n--- Rule 4 (Advanced): Time-Based Repeated Declines ---")
    if not flagged:
        print("  None found.")
    for item in flagged:
        print(f"  Account {item['account_id']}: {item['count']} declines between "
              f"{item['window_start']} and {item['window_end']} -> {item['reason']}")


def generate_summary(total_records, valid_transactions, invalid_records,
                      high_value, repeated_declines, multiple_locations,
                      time_based_declines, suspicious_accounts):
    """Build the summary statistics dictionary (Advanced Feature 7)."""
    approved = [r for r in valid_transactions if r["status"] == "APPROVED"]
    declined = [r for r in valid_transactions if r["status"] == "DECLINED"]
    total_suspicious_transactions = len(high_value) + sum(
        len(item["transaction_ids"])
        for item in repeated_declines + multiple_locations + time_based_declines
    )

    return {
        "Total records processed": total_records,
        "Total valid records": len(valid_transactions),
        "Total invalid records": len(invalid_records),
        "Total approved transactions": len(approved),
        "Total declined transactions": len(declined),
        "Total value of approved transactions": round(sum(r["amount"] for r in approved), 2),
        "Total suspicious transactions": total_suspicious_transactions,
        "Total suspicious accounts": len(suspicious_accounts),
        "High-value transaction alerts": len(high_value),
        "Repeated-decline alerts": len(repeated_declines),
        "Multiple-location alerts": len(multiple_locations),
        "Time-based decline alerts (advanced)": len(time_based_declines),
    }


def display_summary(summary):
    print("\n--- Summary Statistics ---")
    for label, value in summary.items():
        print(f"  {label}: {value}")


def export_summary_to_csv(summary, file_path):
    """Export the summary statistics to a CSV file (Advanced Feature 7)."""
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            for label, value in summary.items():
                writer.writerow([label, value])
        print(f"\nSummary exported to {file_path}")
    except OSError as e:
        print(f"Error: could not export summary to '{file_path}' ({e}).")


def export_invalid_records_to_csv(invalid_records, file_path):
    """Export rejected records to CSV (extension check under Advanced Feature 1)."""
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["line_number", "raw_fields", "reason"])
            for rec in invalid_records:
                writer.writerow([rec["line_number"], " | ".join(rec["fields"]), rec["reason"]])
        print(f"Invalid records exported to {file_path}")
    except OSError as e:
        print(f"Error: could not export invalid records to '{file_path}' ({e}).")
