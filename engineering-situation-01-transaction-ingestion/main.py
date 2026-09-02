import os
import pandas as pd
from typing import List
import hashlib

import json

def validate_schema(df):
    columns = ['transaction_id',
                'customer_id',
                'amount',
                'currency',
                'timestamp']
    
    df_cols = df.columns
    for col in columns:
        if col in df_cols:
            continue
        else:
            raise ValueError(f"Columns - {col} is Missing")
        
        
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
 
def calculate_file_hash(path):
    hasher = hashlib.sha256()
    
    with open(path,"rb") as file:
        while True:
            chunk = file.read(8192)
            
            if not chunk:
                break
            
            hasher.update(chunk)
            
    return hasher.hexdigest()

def load_preprocessing_state(file_name):
    try:
        with open(file_name,"r") as file:
            data = json.load(file)
    except FileNotFoundError:
        return {}
    
    return data

def save_preprocessing_state(file_name,data):
    with open(file_name, "w") as file:
        json.dump(data,file,indent = 4)
      
def main():
    raw_dir = os.path.join(
    "data",
    "raw"
)

    all_files = [f for f in os.listdir(raw_dir) if os.path.isfile(os.path.join(raw_dir, f))]
    
    for file in all_files:

        file_path = os.path.join(raw_dir,file)
        file_hash = calculate_file_hash(file_path)
        file_name = os.path.basename(file_path)
        file_stem = os.path.splitext(file_name)[0]
        
        history_json = load_preprocessing_state("processed_files.json")
        
        if file_hash not in history_json or history_json[file_hash]['status'] != 'Completed':
            try:
                history_json[file_hash] = {'file_name':file_name,
                'status' : 'Processing'}
                
                save_preprocessing_state(
                                "processed_files.json",history_json)

                data = pd.read_csv(file_path)
                
                validate_schema(data)

                validated_data = validate_data(data, ["INR", "USD", "EUR"])

                rejected_data = validated_data[
                    validated_data["rejection_reason"] != ""
                ].copy()

                cleaned_data = validated_data[
                    validated_data["rejection_reason"] == ""
                ].copy()
                # to move the clean data into Processed folder
                cleaned_data.to_csv(f"data/processed/{file_stem +'_clean.csv'}", index=False)
                
                # to move the rejected data into Processed folder
                rejected_data.to_csv(f"data/processed/{file_stem +'_rejected.csv'}", index=False)
                
                history_json[file_hash] = {
            "file_name": file_name,
            "status": "Completed"
        }
                save_preprocessing_state(
                    "processed_files.json",history_json)
            except Exception as e:
                history_json[file_hash] = {'file_name':file_name,
                            'status' : 'Failed'}
                
                save_preprocessing_state(
                                "processed_files.json",history_json)
                
                print(f"{file_name}, Failed. Reason -> {e}")
                            
        
        elif file_hash in history_json and history_json[file_hash]['status'] == 'Completed':
            print(f"{file_name}, already processed. Skipping.")
                   
        
if __name__== "__main__":
    main()

