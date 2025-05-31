import pandas as pd
import gspread
import os

from gspread_dataframe import get_as_dataframe, set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
from extract import extract_company_information

def merge_dataframes(old_df, new_df):
    if old_df.empty:
        return new_df
        
    merged = pd.merge(
        old_df, new_df, 
        on="Company Name",
        how="outer", 
        suffixes=('_old', '')
    )

    for col in old_df.columns:
        if col != "Company Name" and col in merged.columns and col + '_old' in merged.columns:
            merged[col] = merged[col].combine_first(merged[col + '_old'])
            merged.drop(columns=[col + '_old'], inplace=True)
    return merged

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



def write_to_google_sheet(new_data):
    new_data = reformat_new_data(new_data)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    base_dir = os.path.dirname(__file__)
    credentials_path = os.path.join(base_dir, "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)

    # Open the sheet
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1jFLtlpbTBKzSEsThdD9tfP8AQr-_TIPOrVWMjr_Zl50")
    worksheet = sheet.get_worksheet(0)  # Get the first sheet

    # Get old data
    old_df = get_as_dataframe(worksheet, evaluate_formulas=True).dropna(how='all')
    
    new_df = pd.DataFrame(new_data)

    # Merge and update
    merged_df = merge_dataframes(old_df, new_df)

    # Write back to the sheet
    worksheet.clear()
    if not merged_df.empty:
        set_with_dataframe(worksheet, merged_df)