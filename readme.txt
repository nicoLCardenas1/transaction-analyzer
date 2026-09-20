use in the terminal

python -c "from transaction_reader import read_transaction_file; resultado = read_transaction_file('transactions.csv'); print(len(resultado)); print(resultado[0])"