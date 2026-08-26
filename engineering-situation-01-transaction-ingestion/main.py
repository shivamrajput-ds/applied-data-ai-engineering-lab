import os
import pandas as pd
from typing import List

def validate_data(df: pd.DataFrame,valid_currency:List[str])-> pd.DataFrame:
    
    valid_data = df.copy()
    valid_data["rejection_reason"] = ""
    
    # remove whole row duplicates
    duplicate_mask = valid_data.duplicated()
    valid_data.loc[duplicate_mask,"rejection_reason"] = "duplicate record"
    
    # remove row conflicts
    compare_columns = [
    "customer_id",
    "amount",
    "currency",
    "timestamp"
]

    conflict_check = (
        valid_data
        .groupby("transaction_id")[compare_columns]
        .nunique(dropna=False)
    )

    conflicting_ids = (
        conflict_check[
            (conflict_check > 1).any(axis=1)
        ]
        .index
    )

    conflicting_mask = (
        valid_data["transaction_id"].isin(conflicting_ids)
        & (valid_data["rejection_reason"] == "")
    )

    valid_data.loc[

        conflicting_mask,

        "rejection_reason"

    ] = "conflicting duplicate"

    # to validate the currency
    invalid_currency = (~valid_data["currency"].isin(valid_currency) & (valid_data["rejection_reason"] == ""))
    valid_data.loc[invalid_currency,"rejection_reason"] = "invalid currency"
    
    
    # to validate the amount
    converted_amount  = pd.to_numeric(valid_data["amount"],errors ="coerce")
    invalid_amount = (
    (converted_amount.isnull() | (converted_amount <= 0))
    & (valid_data["rejection_reason"] == "")
)
    valid_data.loc[invalid_amount,"rejection_reason"] = "invalid amount"
    
    
    # to validate the transaction_id  
    invalid_transaction_id = (
    (
        valid_data["transaction_id"].duplicated(keep="first")
        | (valid_data["transaction_id"].str.strip() == "")
        | valid_data["transaction_id"].isnull()
    )
    & (valid_data["rejection_reason"] == "")
)
    valid_data.loc[invalid_transaction_id,"rejection_reason"] = "invalid transaction id"
    
    # to validate the customer_id
    customer_id = valid_data["customer_id"].astype("string").str.strip()
    invalid_customer_id = (
        (customer_id.isnull() | (customer_id == "") | (customer_id == "0"))
        & (valid_data["rejection_reason"] == "")
    )
    valid_data.loc[
        invalid_customer_id,
        "rejection_reason"
    ] = "invalid customer id"
    
    # to validate timestamp
    parsed_timestamp = pd.to_datetime(valid_data['timestamp'], format="ISO8601",
    errors="coerce"
)
    invalid_timestamp = (
    parsed_timestamp.isnull()
    & (valid_data["rejection_reason"] == "")
)

    valid_data.loc[
        invalid_timestamp,
        "rejection_reason"
    ] = "invalid timestamp"
        
    return valid_data
        
def main():
    path = os.path.join("data","raw","raw_transactions_day1.csv")
    data = pd.read_csv(path)
    
    validated_data = validate_data(data, ["INR", "USD", "EUR"])

    rejected_data = validated_data[
        validated_data["rejection_reason"] != ""
    ].copy()

    cleaned_data = validated_data[
        validated_data["rejection_reason"] == ""
    ].copy()
    # to move the clean data into Processed folder
    cleaned_data.to_csv("data/processed/clean_transactions.csv", index=False)
    
    # to move the rejected data into Processed folder
    rejected_data.to_csv("data/processed/reject_transactions.csv", index=False)
     
if __name__== "__main__":
    main()

