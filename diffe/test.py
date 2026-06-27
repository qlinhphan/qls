import pandas as pd
import torch.nn as nn
import torch
from pprint import pprint
from dataset.MyData import MyDatas
from model.MyModel import MyModels
from torch.utils.data import DataLoader
from tqdm import tqdm
from sklearn.metrics import classification_report


def test():
    data = MyDatas(path = "dataset/spam_ham_dataset.csv")
    len_data = data.__len__()

    model = MyModels(50616, 105, 2)
    state_dict = torch.load('model_weights.pth', weights_only=True)
    model.load_state_dict(state_dict)

    data_act = []               # Kết quả thực tế
    data_model = []            # Kết quả dự đoán từ mô hình

    model.eval()
    with torch.no_grad():
        for i in range(len_data - 4171):
            dt, lb = data.__getitem__(i)
            dt = dt.unsqueeze(0)
            rs = model(dt)
            rs= int(torch.argmax(rs, dim = -1)[0])
            data_model.append(rs)
            lb = int(lb)
            data_act.append(lb)
            print("=========================================================================================================")
            # break

    print(classification_report(data_act, data_model))
        


if __name__ == "__main__":
    test()