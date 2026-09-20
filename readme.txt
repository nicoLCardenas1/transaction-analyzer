Bank Transaction Fraud Detection System
ICT703 Programming - Assessment Task 2
Student: Ashly

FILES
-----
main.py                 - Runs the whole program (entry point)
transaction_reader.py   - Reads the transaction file
validators.py           - Core and enhanced field validation
storage.py              - Stores, searches and filters transactions
fraud_detector.py       - The 3 core rules + the advanced time-based rule
reporting.py            - Summary statistics and CSV export
test.py                 - Automated tests (25 tests, no manual input needed)
transactions.csv        - Sample transaction data (fictional)

HOW TO RUN
----------
1. Make sure all files above are in the same folder.
2. Run the program:
   python3 main.py
3. Run the tests:
   python3 test.py

WHAT THE PROGRAM GENERATES
---------------------------
When main.py runs, it creates two files in the same folder:
- invalid_transactions.csv   (rejected records, with the reason for rejection)
- summary_report.csv         (summary statistics)

NOTE
----
All accounts, transactions and customer data in this project are fictional,
created for assessment purposes only.

