import datetime

def timestamp_now():
    return datetime.datetime.utcnow().isoformat() + "Z"

def clean_dataframe(df):
    return df.dropna().reset_index(drop=True)
