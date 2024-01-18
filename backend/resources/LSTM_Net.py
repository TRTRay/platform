import torch.nn as nn


class TransformerModel(nn.Module):
    def __init__(self, input_size = 4, hidden_size = 64, output_size = 2 ):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, 1, batch_first=True)
        # self.multi_att = nn.MultiheadAttention(embed_dim =input_size*10, num_heads=10)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):

        x = x.permute(0, 2, 1)  # 调整维度顺序，变成 (batch_size, input_dim, sequence_length)
        # x, (h_t, c_t) = self.lstm(x)
        x, _ = self.lstm(x)
        x = x[:, :]  # 取最后一个时间步的输出作为 LSTM 层的输出

        # 全连接层
        x = self.fc(x)
        # print(x.shape)
        x = x.squeeze()  # 去掉 size 为 1 的维度

        return x


