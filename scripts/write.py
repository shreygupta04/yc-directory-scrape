import pandas as pd
import gspread
import os
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
import time
from functools import lru_cache

@lru_cache(maxsize=1)
def get_google_client():
    """Cached Google Sheets client to avoid repeated authentication"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "credentials.json")
    
    if os.path.exists(path):
        creds = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
    else:
        service_account_info = {
            "type": "service_account",
            "project_id": os.environ.get("PROJECT_ID"),
            "private_key_id": os.environ.get("PRIVATE_KEY_ID"),
            "private_key": os.environ.get("PRIVATE_KEY"),
            "client_email": os.environ.get("CLIENT_EMAIL"),
            "client_id": os.environ.get("CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ.get("CLIENT_X509_CERT_URL"),
            "universe_domain": "googleapis.com"
        }
        creds = service_account.Credentials.from_service_account_info(service_account_info).with_scopes(scope)
    
    return gspread.authorize(creds)

def reformat_new_data(new_data):
    for company in new_data:
        company["Company Name"] = company.pop("company_name")
        company["Batch"] = company.pop("batch")
        company["Company Description"] = company.pop("description")
        company["Website"] = company.pop("website")
        company["Geo"] = company.pop("geo")
        founders = company.pop("founders", [])[:4]
        for i in range(len(founders)):
            founder = founders[i]
            founder_name = founder.pop("name", None)
            founder_linkedin = founder.pop("linkedin", None)
            company["Founder " + str((i + 1))] = founder_name
            company["Founder " + str((i + 1)) + " LinkedIn"] = founder_linkedin
        company["Notes"] = company.pop("notes")
    return new_data


def merge_dataframes(old_df, new_df):
    if old_df.empty:
        return new_df
    
    old_df_copy = old_df.copy()
    new_df_copy = new_df.copy()

    old_df_copy["Company Name"] = old_df_copy["Company Name"].astype(str)
    new_df_copy["Company Name"] = new_df_copy["Company Name"].astype(str)
    
    # Handle NaN values that might become 'nan' strings
    old_df_copy["Company Name"] = old_df_copy["Company Name"].replace('nan', '')
    new_df_copy["Company Name"] = new_df_copy["Company Name"].replace('nan', '')
    
    # Remove rows with empty company names
    old_df_copy = old_df_copy[old_df_copy["Company Name"].str.strip() != '']
    new_df_copy = new_df_copy[new_df_copy["Company Name"].str.strip() != '']
        
    merged = pd.merge(
        old_df_copy, new_df_copy, 
        on="Company Name",
        how="outer", 
        suffixes=('_old', '')
    )

    for col in old_df.columns:
        if col != "Company Name" and col in merged.columns and col + '_old' in merged.columns:
            merged[col] = merged[col].combine_first(merged[col + '_old'])
            merged.drop(columns=[col + '_old'], inplace=True)
    
    desired_columns = [
        "Company Name",
        "Batch",
        "Company Description",
        "Geo",
        "Website",
        "Founder 1",
        "Founder 1 LinkedIn",
        "Founder 2",
        "Founder 2 LinkedIn",
        "Founder 3",
        "Founder 3 LinkedIn"
        "Founder 4",
        "Founder 4 LinkedIn"
        "Notes"
    ]

    merged = merged[[col for col in desired_columns if col in merged.columns]]
    return merged

def write_to_google_sheet(new_data):
    """Optimized Google Sheets writing with batch operations"""
    if not new_data:
        return
        
    new_data = reformat_new_data(new_data)
    client = get_google_client()

    print("Writing to Google Sheet...")
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1jFLtlpbTBKzSEsThdD9tfP8AQr-_TIPOrVWMjr_Zl50")
    worksheet = sheet.get_worksheet(0)
    
    # Add retry logic for Google Sheets operations
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Get old data with better error handling
            old_df = get_as_dataframe(worksheet, evaluate_formulas=True).dropna(how='all')
            new_df = pd.DataFrame(new_data)
            
            # Merge and update
            merged_df = merge_dataframes(old_df, new_df)
            
            # Batch update to reduce API calls
            if not merged_df.empty:
                set_with_dataframe(
                    worksheet, 
                    merged_df, 
                    include_column_header=False,
                    resize=False,
                    row=2  # Start writing from second row
                )
                        
            print("Data written successfully.")
            break
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff



