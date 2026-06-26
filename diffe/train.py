import pandas as pd

path_data = "dataset/spam_ham_dataset.csv"             # 0 ham, 1 spam

data = pd.read_csv(path_data)
print(data)
