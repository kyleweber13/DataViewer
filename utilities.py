import pandas as pd


def convert_time_columns(df):

    df = df.copy()

    for column in df.columns:
        if 'time' in column:
            try:
                df[column] = pd.to_datetime(df[column])
            except:
                pass

    return df


def index_from_timestamp(timestamp, start_timestamp, sample_rate):

    i = int((pd.to_datetime(timestamp) - pd.to_datetime(start_timestamp)).total_seconds() * sample_rate)

    if i < 0:
        i = 0

    return i

