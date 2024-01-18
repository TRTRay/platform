import torch
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from backend.utils.utils import *


def make_input(plcr_files, init_pos):
    plcrs = sio.loadmat(plcr_files[0])['plcr']
    for plcr_file in plcr_files:
        plcr = sio.loadmat(plcr_file)['plcr']
        plcrs = np.hstack((plcrs, plcr))
    plcrs = plcrs[:, 1:]
    matrix = np.hstack((plcrs, np.zeros((plcrs.shape[0], 2))))
    matrix[:, -2] = init_pos[0]
    matrix[:, -1] = init_pos[1]
    return matrix


def plot_and_save(data):
    plt.xlim((-1, 5))
    plt.ylim((-1, 5))
    # 设置坐标轴名称

    plt.xlabel('X(m)')
    plt.ylabel('Y(m)')
    # 设置坐标轴刻度
    my_x_ticks = np.arange(-1, 5, 1)
    my_y_ticks = np.arange(-1, 5, 1)
    plt.xticks(my_x_ticks)
    plt.yticks(my_y_ticks)

    x_loc = data[:, 0]
    y_loc = data[:, 1]
    plt.plot(x_loc, y_loc)
    plt.show()


def nne(input_tensor):
    input_tensor = torch.from_numpy(input_tensor).float()
    input_tensor = input_tensor.unsqueeze(0)
    input_tensor = input_tensor.permute(0, 2, 1)

    device = torch.device("cpu" if torch.cuda.is_available() else "cpu")
    model = torch.load(os.path.join(Utils.get_proj_path(), 'backend', 'resources', 'net_plcr.pth'), map_location='cpu')
    model = model.to(device)
    model.eval()

    input_tensor = input_tensor.to(device)
    output_tensor = model(input_tensor)  # 使用加载的模型进行前向计算
    output_tensor = output_tensor.detach().numpy()

    return output_tensor
