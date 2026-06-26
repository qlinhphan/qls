import pandas as pd
import torch.nn as nn
import torch
from pprint import pprint
from dataset.MyData import MyDatas
from model.MyModel import MyModels
from torch.utils.data import DataLoader
from tqdm import tqdm

def trains():
    data = MyDatas(path = "dataset/spam_ham_dataset.csv")
    data_loader = DataLoader(dataset=data, batch_size=32, drop_last=True, shuffle=True)

    model = MyModels(50616, 128, 2)
    epochs = 100
    criterion = nn.CrossEntropyLoss(ignore_index=0)
    optimizer = torch.optim.SGD(model.parameters(), lr = 0.001, momentum=0.9)

    for e in range(epochs):
        model.train()
        pro = tqdm(data_loader)
        for data, lb in pro:
            rs = model(data)
            loss = criterion(rs, lb)
            pro.set_description(f"with epoch: {e+1}, loss is: {loss}")

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    torch.save(model.state_dict(), 'model_weights.pth')

if __name__ == "__main__":
    trains()