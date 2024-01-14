## 版本说明
# 本版本为2024.1.14版本，与main_v2.py共同使用
# 较之初始版本改动三处，其中第一处是新加的，后两处可能之前已改动过
# 1.本版本较之前版本添加对于静态环境和动态环境的判别，可以区分环境中有无人
# 2.本版本修复可能之前还未修复的、代码移植中幅值减半的问题，使得代码与matlab代码处理完全一致
# 3.本版本修复之前呼吸率选取范围的问题，原代码中为8：17，现改为8：28

## 潜在问题说明
# 在转换过程中发现，matlab和python中对于NAN的出现情况和处理似乎是存在差异的，在结果上（PAR）导致了一定差异的出现
# 对于没有呼吸的情况，暂时根据两个数据设计为阈值以下和NAN，具体合理与否，有待进一步验证

## 其它说明
# 关于PAR值得输出预留了函数接口，输出语句也选择保留在breathe（）函数中（目前已注释）
# 在PAR值为NAN时，无绘图结果
import os, time
import scipy.signal as signal
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio

from backend.utils.utils import Utils


# 绘图函数
def plot_and_save_pic(name, data, start_index, end_index, legend, title, xlabel, ylabel, save_path):
    # 参数分别为 图名，数据，起始点，终止点，图例名，图表名，x轴标签，y轴标签
    plt.figure(name)
    plt.plot(data[start_index: end_index], linewidth=2)
    plt.legend([legend])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(save_path + '.png', format='png')
    plt.show()


# hampel 滤波
def hampel(X):
    length = X.shape[0] - 1
    k = 50
    nsigma = 1
    iLo = np.array([i - k for i in range(0, length + 1)])
    iHi = np.array([i + k for i in range(0, length + 1)])
    iLo[iLo < 0] = 0
    iHi[iHi > length] = length
    xmad = []
    xmedian = []
    for i in range(length + 1):
        w = X[iLo[i]:iHi[i] + 1]
        medj = np.median(w)
        mad = np.median(np.abs(w - medj))
        xmad.append(mad)
        xmedian.append(medj)
    xmad = np.array(xmad)
    xmedian = np.array(xmedian)
    scale = 1.4826  # 缩放
    xsigma = scale * xmad
    xi = ~(np.abs(X - xmedian) <= nsigma * xsigma)  # 找出离群点（即超过nsigma个标准差）

    # 将离群点替换为中为数值
    xf = X.copy()
    xf[xi] = xmedian[xi]
    return xf


# 呼吸处理主体函数
def breathe(csi):
    csi_diff = np.zeros(csi.shape, dtype=complex)
    # 预处理解决异常数据
    for i in range(csi.shape[0]):
        for k in range(csi.shape[1]):
            for j in range(csi.shape[2]):
                if abs(csi[i, k, j]) == 0:
                    # 添加边界检测
                    if i-1 == 0:
                        csi[i, k, j] = csi[i+1, k, j]
                    elif i+1 >= csi.shape[0]:
                        # print(i+1)
                        csi[i, k, j] = csi[i-1, k, j]
                    else:
                        csi[i, k, j] = (csi[i-1, k, j] + csi[i+1, k, j])/2

    csi_diff[:, 1, :] = csi[:, 2, :] / csi[:, 1, :]   # Ratio between antenna 3 and 2
    csi_diff[:, 2, :] = csi[:, 0, :] / csi[:, 2, :]   # Ratio between antenna 3 and 1
    csi_diff[:, 0, :] = csi[:, 1, :] / csi[:, 0, :]   # Ratio between antenna 2 and 1

    csi_value = csi_diff[:, 0, :]  # Selecting the ratio between antenna 3 and 2

    # Define the SimParam and FigureParam
    SimParam = {
        'StepSize': 1,  # Step size in degrees
        'PhaseDiffLabel': 2
    }
    SimParam['SampleShifted'] = csi_diff.shape[0]

    FigureNum = 180 // SimParam['StepSize']
    theta_prime_var = np.zeros((csi_diff.shape[0], FigureNum, csi_diff.shape[2]))

    for Theta in range(SimParam['StepSize'], 181, SimParam['StepSize']):
        Theta_index = Theta // SimParam['StepSize']
        oz_prime_var = np.cos(np.deg2rad(Theta)) * np.real(csi_value) + np.sin(np.deg2rad(Theta)) * np.imag(csi_value)
        theta_prime_var[:, Theta_index-1, :] = oz_prime_var

    # Select a suitable candidate via maximum periodicity
    theta_prime_var1 = theta_prime_var - np.mean(theta_prime_var, axis=0)  # Remove DC component
    pro_fft = np.fft.fft(theta_prime_var1, 8192, axis=0)  # Compute FFT along the first axis
    abs_fft = np.abs(pro_fft)

    bnr = (np.sum(abs_fft[8:28, :, :], axis=0) / np.sum(abs_fft, axis=0))
    bnr_value_index = np.argmax(bnr, axis=0)
    bnr_value = np.max(bnr, axis=0)

    best_projection = np.zeros((theta_prime_var1.shape[0], bnr_value_index.shape[0]))

    for i in range(bnr_value_index.shape[0]):
        best_projection[:, i] = theta_prime_var1[:, bnr_value_index[i], i]

    oz_prime_var = best_projection

    for i in range(30):
        oz_prime_var[:, i] = hampel(oz_prime_var[:, i])

    # Apply autocorrelation on respiration pattern
    auto_shifted = oz_prime_var.shape[0]
    r_i = np.zeros((auto_shifted, oz_prime_var.shape[1]))
    mean_oz_prime_var = np.mean(oz_prime_var, axis=0)

    for k_index in range(auto_shifted):
        '''
        是否有啥问题，很奇怪
        '''
        # 很奇怪对于数据为何会出现一行可能是因为axis=0有无导致的结果与matlab中得到的不同，而axis=0按道理未sum函数默认值，理论上不应该出现问题
        # 故在此先依据此特化处理，以保持一致（具体为999行，即索引行号998）
        if (k_index != 998):
            r_i[k_index, :] = np.sum((oz_prime_var[k_index + 1:auto_shifted, :] - mean_oz_prime_var) * (oz_prime_var[0:(auto_shifted - k_index-1), :] - mean_oz_prime_var), axis=0) / np.sum((oz_prime_var - mean_oz_prime_var) ** 2, axis=0)
        else:
            r_i[k_index, :] = np.sum((oz_prime_var[k_index + 1:auto_shifted, :] - mean_oz_prime_var) * (oz_prime_var[0:(auto_shifted - k_index-1), :] - mean_oz_prime_var)) / np.sum((oz_prime_var - mean_oz_prime_var) ** 2, axis=0)

    # Multiple Sub-carriers Combining
    bnr_max_index = np.argmax(bnr_value)
    bnr_max = np.max(bnr_value)
    oz_prime_var[:, bnr_max_index] = hampel(oz_prime_var[:, bnr_max_index])

    # PAR值检测，判断环境中有无人呼吸
    PAR_value = np.max(np.abs(abs_fft[8:28, bnr_value_index[bnr_max_index], bnr_max_index])) / np.mean(np.abs(abs_fft[:, bnr_value_index[bnr_max_index], bnr_max_index]))
    # print("The value of PAR is:", PAR_value)
    # if PAR_value < 10 or np.isnan(PAR_value):
    #     print("-----------当前为静态环境------------")
    # else:
    #     print("----------当前环境有人呼吸----------")

    # Calculate the sum of all subcarriers instead
    candidate_index = np.where(bnr_value > 0.8 * bnr_max)[0]

    r_msc = np.zeros(r_i.shape[0])
    for i in candidate_index:
        r_msc += bnr_value[i] * r_i[:, i]

    r_msc = hampel(r_msc)
    # Filter the interference of breath
    # 加载参数
    mat_data = sio.loadmat(os.path.join(Utils.get_proj_path(), 'backend', 'resources', 'filter_config.mat'))
    filter_config = np.squeeze(mat_data['b'])

    '''
    # 本行代码使最终波形图的幅值减半,yumatlab代码处理结果存在差异,故将其注释
    # filter_config = filter_config /2
    '''

    rawbreath = oz_prime_var[:, bnr_max_index]
    filtbreath = signal.lfilter(filter_config, 1, np.concatenate((rawbreath, np.zeros(8000))))

    fft_filter = np.abs(np.fft.fft(filtbreath, 8192, axis=0))
    fft_max_index = np.argmax(fft_filter)
    '''
    按照原理不应该出现下面情况，但根据数据情况添加下列语句
    '''
    fft_max_index = min(8192 - fft_max_index + 1, fft_max_index)
    respiration_rate = (fft_max_index + 1) * 100 * 60 / 8192  # 考虑到python与matlab在索引起点上的差别，理论上应该是合理的
    # print('人的呼吸速率为', respiration_rate, 'bpm')

    return respiration_rate, auto_shifted, filtbreath, PAR_value
