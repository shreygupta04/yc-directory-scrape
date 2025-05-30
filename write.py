import pandas as pd


def merge_dataframes(old_data, new_data):
    old_df = pd.DataFrame(old_data)
    new_df = pd.DataFrame(new_data)
        
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