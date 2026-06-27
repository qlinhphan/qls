
import torch
import torch.nn as nn
import pandas as pd

class MyDatas():         # 0 ham, 1 spam
    def __init__(self, path):
        data = pd.read_csv(path)
        self.text = list(data['text'])
        self.label = list(data['label_num'])

        words = []
        for t in self.text:
            # print(t)
            t = t.lower().split()
            # print("======================================")
            words.extend(t)
        words = list(dict.fromkeys(words))

        self.vocab = {}            # word: index
        self.vocab['<pad>'] = 0
        for i, n in enumerate(words):
            self.vocab[n] = i + 1
        # print(vocab)
        # print(len(vocab))

        self.vocab_revert = {v:k for k , v in self.vocab.items()}        #ind: word

        self.datas = []
        self.lbs = [lb for lb in self.label]

        # max_len_sentence = []    #8862: độ dài ký tự lớn nhất trong 1 câu
        for t in self.text:
            text = t.lower().split()
            te = [self.vocab[t] for t in text]
            while True:
                if len(te) == 8862:
                    break
                te.insert(0, 0)
            self.datas.append(te)
            
    def __getitem__(self, ind):
        data = self.datas[ind]
        lb = self.lbs[ind]

        return torch.tensor(data), torch.tensor(lb)

    def __len__(self):
        return len(self.datas)

    def __getvocab__(self):
        return self.vocab, self.vocab_revert          # len = 50616


if __name__ == "__main__":
    my = MyDatas(path="spam_ham_dataset.csv")
    dt, lb = my.__getitem__(10)
    print(dt)
    print(dt.shape)
    print(lb)
    vc, vc_re = my.__getvocab__()
    print(len(vc))
    print("len: ", my.__len__())
