import os
import pandas as pd
from typing import List

def clean_data(df: pd.DataFrame,valid_currency:List[str])-> pd.DataFrame:
    
    valid_data = df.copy()
    
    # remove whole row duplicates
    valid_data = valid_data.drop_duplicates()

    # to validate the currency
    valid_data = valid_data[valid_data["currency"].isin( valid_currency)]
    
    # to validate the amount
    valid_data["amount"] = pd.to_numeric(valid_data["amount"],errors ="coerce")
    valid_data = valid_data[valid_data["amount"] > 0] 
    
    # to validate the transaction_id
    valid_data = valid_data.drop_duplicates(subset=["transaction_id"],keep="first")
    valid_data = valid_data[valid_data["transaction_id"].str.strip() != ""]
    valid_data = valid_data[valid_data['transaction_id'].notna()]
    
    # to validate the customer_id
    customer_id = valid_data['customer_id'].astype("string").str.strip()
    
    valid_data = valid_data[customer_id.notna() &(customer_id != "") & (customer_id != "0")]
    
    # to validate timestamp
    parsed_timestamp = pd.to_datetime(valid_data['timestamp'], format="ISO8601",
    errors="coerce"
)
    valid_data = valid_data[parsed_timestamp.notna()]
    
    return valid_data
        
def main():
    path = os.path.join("data","raw","raw_transactions_day1.csv")
    data = pd.read_csv(path)
    
    cleaned_data = clean_data(data,["INR","USD","EUR"])
    rejected_data = data.loc[~data.index.isin(cleaned_data.index)].copy()
    
    # to move the clean data into Processed folder
    cleaned_data.to_csv("data/processed/clean_transactions.csv", index=False)
    
    # to move the rejected data into Processed folder
    rejected_data.to_csv("data/processed/reject_transactions.csv", index=False)
     
if __name__== "__main__":
    main()

