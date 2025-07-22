from account_service import AccountService, AccountNotFoundError, InsufficientFundsError

service = AccountService()

# Create two accounts
acc1 = service.create_account(user_id="user123", account_type="Savings")
acc2 = service.create_account(user_id="user456", account_type="Checking")

print(f"Account 1 ID: {acc1.account_id}")
print(f"Account 2 ID: {acc2.account_id}")

# Deposit
print("\nDepositing 1000 to acc1")
service.deposit(acc1.account_id, 1000)
print("Balance acc1:", service.check_funds(acc1.account_id))

# Withdraw
print("\nWithdrawing 200 from acc1")
service.withdraw(acc1.account_id, 200)
print("Balance acc1:", service.check_funds(acc1.account_id))

# Transfer
print("\nTransferring 300 from acc1 to acc2")
service.transfer_funds(acc1.account_id, acc2.account_id, 300)
print("Balance acc1:", service.check_funds(acc1.account_id))
print("Balance acc2:", service.check_funds(acc2.account_id))

# Transaction history
print("\nTransactions for acc1:")
for tx in service.get_transaction_history(acc1.account_id):
    print(f"{tx.timestamp}: {tx.transaction_type} {tx.amount}")

print("\nTransactions for acc2:")
for tx in service.get_transaction_history(acc2.account_id):
    print(f"{tx.timestamp}: {tx.transaction_type} {tx.amount}")

# Update account
print("\nUpdating acc2: setting custom property 'nickname'")
updated_acc2 = service.update_account(acc2.account_id, nickname="Daily Use")
print(vars(updated_acc2))
