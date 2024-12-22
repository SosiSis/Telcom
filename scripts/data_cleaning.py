import numpy as np
def clean_data_1(data):
    print('cleaning data ...')
    data=data.drop_duplicates()
    data=data.dropna(subset=['column_of_interest'],how='any')
    data.fillna({'default_column':0},inplace=True)
    print('Data cleaning completed.')
    return data


def clean_data_2(data):
    data.fillna(data.mean(numeric_only=True),inplace=True)

def treat_outliers_with_mean(column):
    Q1=column.quantile(0.25)
    Q3=column.quantile(0.75)
    IQR=Q3-Q1
    lower_bound=Q1 - 1.5 * IQR
    upper_bound=Q3 + 1.5 * IQR

    column_mean=column.mean()
    column=np.where((column < lower_bound) |(column > upper_bound),column_mean,column )
    return column