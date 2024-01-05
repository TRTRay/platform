import numpy as np
import scipy
import scipy.io as scio
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import butter, filtfilt, hilbert

from backend.utils.utils import Utils


# 一维滑窗函数
def rolling_window(csi_one_dimension, window):
    # 参数分别为一维numpy数组，窗口大小
    shape = csi_one_dimension.shape[:-1] + (csi_one_dimension.shape[-1] - window + 1, window)
    strides = csi_one_dimension.strides + (csi_one_dimension.strides[-1],)
    return np.lib.stride_tricks.as_strided(csi_one_dimension, shape=shape, strides=strides)


# 方差函数
def get_var(csi_one_dimension):
    # 参数为一维numpy数组
    csi_window_var = rolling_window(csi_one_dimension, 900)
    v_var = np.var(csi_window_var, axis=1)
    return v_var


# 相关性函数
def get_corr(csi_two_dimension):
    # 按照30s滑窗，每个窗口900个点
    csi_window_corr = np.lib.stride_tricks.sliding_window_view(csi_two_dimension, (900, 30))
    csi_window_corr_transpose = csi_window_corr[:, 0, :, :].T

    z = np.size(csi_window_corr_transpose, 2)
    corr_array = np.empty(z, dtype=np.float64)
    for x in range(0, z):
        corr_array[x] = np.array(sum(np.corrcoef(csi_window_corr_transpose[:, :, x])[:, 4]))
    return corr_array


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


# smooth滤波(多项式拟合)
def smooth(x, k):
    x_smooth = scipy.signal.savgol_filter(x, k, 5)
    # window_length必须为正奇整数，越小越真实，越大越平滑
    # polyorder小于window_length,越大越真实，越小越平滑
    return x_smooth


# convolve 滤波
def convolve(x):
    window_size = 50
    window = np.ones(int(window_size)) / float(window_size)
    re = np.convolve(x, window, 'same')
    return re


# stft函数
def my_stft(x):
    f, t, amp = signal.stft(x, fs=100, window='boxcar', nperseg=32, noverlap=22, nfft=256,
                            detrend=False, return_onesided=True, boundary='zeros', padded=True, axis=-1)
    # fs:时间序列的采样频率,  nperseg:每个段的长度，默认为256(2^n)
    # noverlap:段之间重叠的点数。如果没有则noverlap=nperseg/2
    # 如果window是一个字符串或元组，则传递给它window是数组类型，直接以其为窗，其长度必须是nperseg。
    # 常用的窗函数有boxcar，triang，hamming， hann等，默认为Hann窗。
    return f, t, amp


# 带通滤波
def bandpass_filter(data, lowcut, highcut, fs, order=5):
    # 计算归一化的截止频率
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist

    # 使用巴特沃斯滤波器设计滤波器系数
    b, a = butter(order, [low, high], btype='band')

    # 应用滤波器到数据
    filtered_data = filtfilt(b, a, data)
    return filtered_data


# 下标最大值函数
def Getampmax(amp):
    t = np.size(amp[0, :])
    amp_max = np.empty(t, dtype=np.int16)
    for x in range(0, t):
        amp_max[x] = np.argmax(abs(amp[:, x]))
    return amp_max


#
def get_DFS(x):
    # X为原始信号的divide
    # x_lfilter = fir_bandpass_filter(x)
    x_lfilter = bandpass_filter(x, 0.1, 30, 100)

    # stft变换
    fre, ts, amp = my_stft(x_lfilter)

    # 取时间序列
    t = np.size(ts)

    # 取对应最大值的下标
    amp_max = Getampmax(amp)

    fre_max = np.empty(t, dtype=np.float64)
    for i in range(0, t):
        fre_max[i] = fre[amp_max[i]]
    fre_max_filter = smooth(hampel(abs(fre_max), 20), 103)

    plt.plot(fre_max_filter)
    plt.title('DFS')
    plt.show()

    return fre_max_filter


# 希尔伯特变换
def hilbert_transform(data):
    # 对输入数据执行希尔伯特变换
    analytic_signal = hilbert(data)

    return analytic_signal


# 离散小波变换
# def my_dwt(data, wavelet='db4', level=1):
#     coeffs = pywt.wavedec(data, wavelet, level=level)
#     # data是输入的原始数据，wavelet是小波基函数的名称（默认为'db4'，即Daubechies4小波），level是变换的级数（默认为1级）
#     return coeffs


# 曲线绘图函数
def plot_curve(x):
    plt.plot(x)
    plt.show()


# 方差相关性绘图函数
def plot_varcorr(v_var, corr_array, title, xlabel, ylabel_var, ylabel_corr, legend_var, legend_corr):
    # 参数分别为 方差数组 相关性数组 标题 x轴标签 方差y轴标签 相关性y轴标签 方差图例 相关性图例
    fig, ax1 = plt.subplots()
    l1, = ax1.plot(v_var, label=legend_var)
    plt.title(title)
    ax1.set_ylabel(ylabel_var)
    ax1.set_xlabel(xlabel)

    ax2 = ax1.twinx()
    l2, = ax2.plot(corr_array, color='red', label=legend_corr)
    plt.legend(handles=[l1, l2], labels=[legend_var, legend_corr], loc=0)
    ax2.set_ylabel(ylabel_corr)
    ax2.set_xticklabels(['', '0', '20', '40', '60', '80'])
    plt.show()


# 输出函数
def output(v_var, corr_array, dfs_array):
    # 时间序列-9000(按照var设置) 补充dfs到1000
    dfs = np.zeros(1000)
    for i in range(0, np.size(dfs_array)):
        dfs[i] = dfs_array[i]

    var_corr_array = np.empty([2, 9000], dtype=np.float64)
    motion = np.zeros(100, dtype=int)
    for x in range(0, 100):
        if np.mean(dfs[x * 10:(x+1) * 10]) > 1:
            motion[x] = 3
        else:
            print(np.mean(corr_array[x * 90:(x+3) * 90]))
            if np.mean(corr_array[x * 90:(x+3) * 90]) >= np.mean(corr_array[1000:3000]) / 1.4:
                motion[x] = 2
            else:
                # print(max(var_corr_array[0, x * 90:(x+3) * 90]))
                if np.mean(v_var[x * 90:(x+3) * 90]) < np.mean(v_var[6000:8000]):
                    motion[x] = 1
                else:
                    motion[x] = 2
    return motion


# motion绘图函数
def plot_motion(motion, title, y_label, x_label):
    motion = hampel(motion, 15)
    fig, ax = plt.subplots()
    ax.plot(motion)
    ax.set_title(title)
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_xticklabels(['', '0', '20', '40', '60', '80'])
    plt.show()


# 主体函数
def classify(csi):
    # var 取第一根天线和第三根天线的第14个子载波的和
    csi_1 = abs(csi[:, 0, 5] + csi[:, 2, 5])
    var = smooth(hampel(get_var(csi_1), 1000), 1003)

    # corr 取第一根天线和第三根天线的平均
    csi_2 = abs(csi[:, 0, :] + csi[:, 2, :]) / 2
    corr = smooth(hampel(get_corr(csi_2), 1000), 1003)
    plot_varcorr(var, corr, 'BWS Sift', 'Time(s)', 'Variance', 'Correlation', 'variance', 'correlation')

    # DFS 取第一根天线和第三根天线的比
    csi_3 = np.divide(csi[:, 0, 5], (csi[:, 2, 5] + 0.01))
    dfs = get_DFS(csi_3)

    motion = output(var, corr, dfs)
    plot_motion(motion, 'Motion', 'Type', 'Time(s)')
    return motion
