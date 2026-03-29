def get_application_status(user_id="123"):
    mock = {
        "123": "Your Atome card application is under review.",
        "456": "Your Atome card has been approved.",
        "789": "Your application was rejected."
    }
    return mock.get(user_id, "No application status found. Please enter a valid user id or check if you have any application under your account.")


def get_transaction_status(txn_id="tx100"):
    mock = {
        "tx100": "Transaction failed due to insufficient credit.",
        "tx101": "Transaction declined by merchant.",
        "tx102": "Transaction completed successfully."
    }
    return mock.get(txn_id, "Transaction not found. Please enter a valid transaction id.")