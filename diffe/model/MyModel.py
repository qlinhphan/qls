import torch
import torch.nn as nn

class MyModels(nn.Module):
    def __init__(self, len_vocab, num_emb_aword, num_output):
        super().__init__()
        self.emb = nn.Embedding(len_vocab, num_emb_aword)
        self.rnn = nn.RNN(num_emb_aword, 32, batch_first=True)
        self.ln = nn.Linear(32, num_output)

    def forward(self, x):
        x = self.emb(x)
        out, h_n = self.rnn(x)
        out = out[:, -1, :]
        out = self.ln(out)
        return out
        
    
if __name__ == "__main__":
    data = torch.tensor([
        [1, 2, 3, 4, 5],
        [1, 2, 3, 4, 5],
        [1, 2, 3, 4, 5],
    ])
    model = MyModels(1245, 28, 2)
    rs = model(data)
    print(rs.shape)
