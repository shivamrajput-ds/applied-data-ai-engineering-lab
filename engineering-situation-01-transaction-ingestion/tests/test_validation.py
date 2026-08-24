from main import validate_data
import pandas as pd

COLUMNS = [
    "transaction_id",
    "customer_id",
    "amount",
    "currency",
    "timestamp",
]

VALID_CURRENCIES = ["INR", "USD", "EUR"]

def make_df(data):
    return pd.DataFrame(data,columns = COLUMNS)

# test case 1 -> to chekc the duplicate mask
def test_duplicate():
    data = [
    ["txn_1001", "cust_201", 1250.50, "INR", "2026-08-22T09:15:00"],
    ["txn_1002", "cust_202", 499.99, "USD", "2026-08-22T09:18:25"],
    ["txn_1001", "cust_201", 1250.50, "INR", "2026-08-22T09:15:00"]
]
    df = make_df(data)
    res = validate_data(df,VALID_CURRENCIES)
    
    assert res.loc[2,'rejection_reason'] == "duplicate record"
 

def test_invalid_currency():
    data = [
    ["txn_2001", "cust_301", 850.50, "BTC", "2026-08-24T10:15:00"]
]
    df = make_df(data)
    res = validate_data(df,VALID_CURRENCIES)
    
    assert res.loc[0,"rejection_reason"] == "invalid currency"
    
def test_invalid_amount():
    data = [
    ["txn_3001", "cust_401", -100, "INR", "2026-08-24T10:20:00"],
    ["txn_3002", "cust_402", "abc", "USD", "2026-08-24T10:25:00"]
]
    df = make_df(data)
    res = validate_data(df,VALID_CURRENCIES)
    
    assert res.loc[0,"rejection_reason"] == "invalid amount"
    assert res.loc[1,"rejection_reason"] == "invalid amount"

def test_invalid_customer_id():
    data = [
    ["txn_4001", None, 500.0, "INR", "2026-08-24T10:30:00"],
    ["txn_4002", "   ", 750.0, "USD", "2026-08-24T10:35:00"],
    ["txn_4003", "0", 900.0, "EUR", "2026-08-24T10:40:00"],
]
    df = make_df(data)
    res = validate_data(df,VALID_CURRENCIES)
    
    assert res.loc[0,"rejection_reason"] == "invalid customer id"
    
    assert res.loc[1,"rejection_reason"] == "invalid customer id"
    assert res.loc[2,"rejection_reason"] == "invalid customer id"
    
    
def test_invalid_timestamp():
    data = [
    ["txn_5001", "cust_501", 500.0, "INR", "not-a-date"],
    ["txn_5002", "cust_502", 750.0, "USD", "24-08-2026 10:30"],
]
    df = make_df(data)
    res = validate_data(df,VALID_CURRENCIES)
    
    assert res.loc[0,"rejection_reason"] == "invalid timestamp"
        
    assert res.loc[1,"rejection_reason"] == "invalid timestamp"

def test_invalid_transaction_id():
    data = [
    ["", "cust_601", 500.0, "INR", "2026-08-24T11:00:00"],
    [None, "cust_602", 700.0, "USD", "2026-08-24T11:05:00"],
    ["txn_6003", "cust_603", 900.0, "EUR", "2026-08-24T11:10:00"],
    ["txn_6003", "cust_604", 1200.0, "INR", "2026-08-24T11:15:00"],
]
    df = make_df(data)
    res = validate_data(df,VALID_CURRENCIES)
    assert res.loc[0,"rejection_reason"] == "invalid transaction id"
            
    assert res.loc[1,"rejection_reason"] == "invalid transaction id"
    
    assert res.loc[2,"rejection_reason"] == ""
    
    assert res.loc[3,"rejection_reason"] == "invalid transaction id" 
    
    
  

