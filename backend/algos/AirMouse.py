import multiprocessing
import pyaudio
import numpy as np
from matplotlib import gridspec
import scipy
import matplotlib.pyplot as plt


class SignalParam:
    def __init__(self):
        self.SNR = 0
        self.ChirpBW = 4000
        self.ChirpF0 = 18000
        self.ChirpF1 = 18000 + self.ChirpBW
        self.ChirpT = 0.04
        self.SampleFrequency = 48000
        self.ChannelNum = 6
        self.Speed = 346
        self.sampleTime = 1 / self.SampleFrequency
        self.ChirpSize = int(self.ChirpT / self.sampleTime)
        self.FFTLength = self.SampleFrequency * 1
        self.FFTResolution = self.SampleFrequency / self.FFTLength
        self.offset = 0


signalParam = SignalParam()


class FilterParam:
    def __init__(self, signalParam: SignalParam):
        self.BPF_Center_Frequency = signalParam.ChirpF0 + signalParam.ChirpBW / 2
        self.BPF_Filter_Pass = 500
        self.BPF_Filter_Stop = 1000
        self.HPF_Filter_Pass = signalParam.ChirpF0 - 500
        self.HPF_Filter_Stop = signalParam.ChirpF0 - 1000
        self.LPF_Filter_Pass = 300
        self.LPF_Filter_Stop = 500
        # Band pass filter (Derive single tone)
        self.BPF_b, self.BPF_a = self.designBPF(self.BPF_Center_Frequency, self.BPF_Filter_Pass, self.BPF_Filter_Stop,
                                                signalParam.SampleFrequency)
        # High pass filter (Derive FMCW waves)
        self.HPF_b, self.HPF_a = self.designHPF(self.HPF_Filter_Pass, self.HPF_Filter_Stop, signalParam.SampleFrequency)
        # Low pass filter (Derive FMCW waves)
        self.LPF_b, self.LPF_a = self.designLPF(self.LPF_Filter_Pass, self.LPF_Filter_Stop, signalParam.SampleFrequency)

    def designBPF(self, F_Center, Filter_Pass, Filter_Stop, fs):
        wp = 2 * np.pi * np.array([F_Center - Filter_Pass / 2, F_Center + Filter_Pass / 2]) / fs
        ws = 2 * np.pi * np.array([F_Center - Filter_Stop / 2, F_Center + Filter_Stop / 2]) / fs
        Rp = 1
        Rs = 30
        n, Wn = scipy.signal.ellipord(wp / np.pi, ws / np.pi, Rp, Rs)
        b_value, a_value = scipy.signal.ellip(n, Rp, Rs, Wn, btype='bandpass')
        return b_value, a_value

    def designHPF(self, Filter_Pass, Filter_Stop, fs):
        # 高通滤波
        # 使用注意事项：通带或阻带的截止频率的选取范围是不能超过采样率的一半
        rp = 0.1
        rs = 30  # 通带边衰减DB值和阻带边衰减DB值
        wp = 2 * np.pi * Filter_Pass / fs
        ws = 2 * np.pi * Filter_Stop / fs
        # 设计切比雪夫滤波器
        n, _ = scipy.signal.cheb1ord(wp / np.pi, ws / np.pi, rp, rs)
        b_value, a_value = scipy.signal.cheby1(n, rp, wp / np.pi, 'highpass')
        return b_value, a_value

    def designLPF(self, Filter_Pass, Filter_Stop, fs):
        # 低通滤波
        # 使用注意事项：通带或阻带的截止频率的选取范围是不能超过采样率的一半
        rp = 0.1
        rs = 30  # 通带边衰减DB值和阻带边衰减DB值
        wp = 2 * np.pi * Filter_Pass / fs
        ws = 2 * np.pi * Filter_Stop / fs
        # 设计切比雪夫滤波器
        n, _ = scipy.signal.cheb1ord(wp / np.pi, ws / np.pi, rp, rs)
        b_value, a_value = scipy.signal.cheby1(n, rp, wp / np.pi, 'lowpass')
        return b_value, a_value


filterParam = FilterParam(signalParam)


class FMCWSignal:
    def __init__(self, signalParam: SignalParam, v):
        self.t = np.arange(0, signalParam.ChirpSize) * signalParam.sampleTime
        # up_chirp
        self.up_s = np.exp(1j * (1 - v / signalParam.Speed) * (
                    2 * np.pi * signalParam.ChirpF0 * self.t + np.pi * signalParam.ChirpBW / signalParam.ChirpT * self.t * self.t))
        # down_chirp
        self.dn_s = np.exp(1j * (1 - v / signalParam.Speed) * (
                    2 * np.pi * signalParam.ChirpF1 * self.t - np.pi * signalParam.ChirpBW / signalParam.ChirpT * self.t * self.t))


fmcw = FMCWSignal(signalParam, 0)


class RecorderProcess(multiprocessing.Process):
    def __init__(self, flag, audiodata):
        super().__init__()
        self.RESPEAKER_INDEX = 1
        self.CHUNK = 1024
        self.RESPEAKER_WIDTH = 2
        self.CHANNELS = 8
        self.RATE = 48000
        self.flag = flag
        self._frames = []
        self.audiodata = audiodata

    def run(self):
        print('----------开始录制----------')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(self.RESPEAKER_WIDTH),
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK,
                        input_device_index=self.RESPEAKER_INDEX)
        while self.flag.value:
            data = stream.read(self.CHUNK)
            self.audiodata.put(data)
        stream.stop_stream()
        stream.close()
        print('----------停止录制----------')


class AirMouseProcess(multiprocessing.Process):
    def __init__(self, audiodata, motiondata):
        super().__init__()
        self.SAMPLERANGEOFFSETPERSECOND = 0
        self.CHANNELNUMBER = [0, 1]
        self.CHANNEL = 2
        self.RATE = 48000
        self._frames = np.zeros((0, self.CHANNEL))
        self.INITALDISTANCE = np.zeros((0,))
        self.offset = 0
        self.dataBufferLength = signalParam.ChirpSize
        # [dataBufferLength audiodata]，在使用audiodata时候，因为时钟异步可能会偏移一些采样点，dataBufferLength是用来作为缓冲的，以便能够向左偏移
        self.audiodata = audiodata
        self.motiondata = motiondata
        self.AUDIODIS = 0.7  # 音响间距
        self.smooth_size = 2  # 平滑窗长
        self.phone_length = 0.16  # 手机麦克风间距

    def plotSignal(*signals):
        fig = plt.figure("")
        gs = gridspec.GridSpec(len(signals), 1)  # 设定网格
        for row, s in enumerate(signals):
            ax = fig.add_subplot(gs[row, 0])
            fft_ = scipy.fftpack.fft(s, n=48000, axis=1) / s.shape[1]
            fft_ = scipy.fftpack.fftshift(fft_, axes=(1,))
            fft_abs = np.abs(fft_)
            f_ = np.arange(-500, 501)
            idxrange = f_ + int(48000 / 2) + 1
            plt.plot(f_, fft_abs[:, idxrange].T)
            ax.set_ylim(0, 0.3)
        plt.show()

    def preliminaryAlignment(self):
        while True:
            data = self.audiodata.get()
            data = np.fromstring(data, dtype=np.int16).reshape((-1, self.CHANNEL))
            self._frames = np.concatenate((self._frames, data), axis=0)
            if self._frames.shape[0] >= signalParam.ChirpSize * 2 + self.dataBufferLength * 2 + self.RATE:
                self._frames = np.delete(self._frames, range(0, self.RATE), axis=0)
                data = self._frames[self.dataBufferLength:signalParam.ChirpSize * 2 + self.dataBufferLength,
                       self.CHANNELNUMBER]
                base = np.real(np.concatenate((fmcw.up_s, fmcw.dn_s), axis=0))
                corrIdx = np.correlate(data[:, 0], base, "full")
                alignIdx = (np.argmax(np.abs(corrIdx[data.shape[0] - 1:]))) % (signalParam.ChirpSize * 2)
                # fig=plt.figure("")
                # plt.plot(corrIdx)
                # plt.show()
                self._frames = np.delete(self._frames, range(0, alignIdx), axis=0)
                print("对齐采样点 -- ", alignIdx)
                return

    def clockSynchronization(self):
        print('----------时钟同步----------')
        # 采样的时间同步
        # 系统时间同步
        while True:
            data = self.audiodata.get()
            data = np.fromstring(data, dtype=np.int16).reshape((-1, self.CHANNEL))
            self._frames = np.concatenate((self._frames, data), axis=0)
            if self._frames.shape[0] >= signalParam.ChirpSize * 4 + self.dataBufferLength * 2:
                data = self._frames[self.dataBufferLength:signalParam.ChirpSize + self.dataBufferLength,
                       self.CHANNELNUMBER].T
                data = data / np.max(np.max(data))
                filtered0A = scipy.signal.lfilter(filterParam.LPF_b, filterParam.LPF_a,
                                                  data * np.tile(fmcw.up_s, (2, 1)), axis=1)
                filtered0B = np.flip(
                    scipy.signal.lfilter(filterParam.LPF_b, filterParam.LPF_a, data * np.tile(fmcw.dn_s, (2, 1)),
                                         axis=1), axis=1)
                Ind0A = np.argmax(np.abs(
                    scipy.fftpack.fftshift(
                        scipy.fftpack.fft(
                            filtered0A,
                            n=signalParam.FFTLength,
                            axis=1)
                        , axes=(1,))
                ), axis=1)
                Ind0B = np.argmax(np.abs(
                    scipy.fftpack.fftshift(
                        scipy.fftpack.fft(
                            filtered0B,
                            n=signalParam.FFTLength,
                            axis=1)
                        , axes=(1,))
                ), axis=1)
                self.offset = self.offset + self.SAMPLERANGEOFFSETPERSECOND * signalParam.ChirpT
                self._frames = np.delete(self._frames, range(0, signalParam.ChirpSize + int(
                    self.offset / (signalParam.Speed / signalParam.SampleFrequency))), axis=0)
                self.offset = self.offset % (signalParam.Speed / signalParam.SampleFrequency)

                data = self._frames[self.dataBufferLength:signalParam.ChirpSize + self.dataBufferLength,
                       self.CHANNELNUMBER].T
                data = data / np.max(np.max(data))
                filtered1A = np.flip(
                    scipy.signal.lfilter(filterParam.LPF_b, filterParam.LPF_a, data * np.tile(fmcw.dn_s, (2, 1)),
                                         axis=1), axis=1)
                filtered1B = scipy.signal.lfilter(filterParam.LPF_b, filterParam.LPF_a,
                                                  data * np.tile(fmcw.up_s, (2, 1)), axis=1)
                Ind1A = np.argmax(np.abs(
                    scipy.fftpack.fftshift(
                        scipy.fftpack.fft(
                            filtered1A,
                            n=signalParam.FFTLength,
                            axis=1)
                        , axes=(1,))
                ), axis=1)
                Ind1B = np.argmax(np.abs(
                    scipy.fftpack.fftshift(
                        scipy.fftpack.fft(
                            filtered1B,
                            n=signalParam.FFTLength,
                            axis=1)
                        , axes=(1,))
                ), axis=1)
                self.offset = self.offset + self.SAMPLERANGEOFFSETPERSECOND * signalParam.ChirpT
                self._frames = np.delete(self._frames, range(0, signalParam.ChirpSize + int(
                    self.offset / (signalParam.Speed / signalParam.SampleFrequency))), axis=0)
                self.offset = self.offset % (signalParam.Speed / signalParam.SampleFrequency)

                dA = signalParam.FFTResolution * (
                            Ind0A + Ind1A - signalParam.FFTLength) / 2 * signalParam.ChirpT / signalParam.ChirpBW * signalParam.Speed - self.offset
                dB = signalParam.FFTResolution * (
                            Ind0B + Ind1B - signalParam.FFTLength) / 2 * signalParam.ChirpT / signalParam.ChirpBW * signalParam.Speed - self.offset
                self.INITALDISTANCE = np.append(self.INITALDISTANCE, dA[0])
                if self.INITALDISTANCE.shape[0] == 20:
                    self.offset = self.offset + self.SAMPLERANGEOFFSETPERSECOND * signalParam.ChirpT * 2 + np.mean(
                        self.INITALDISTANCE) - 0.02
                    self._frames = np.delete(self._frames, range(0, signalParam.ChirpSize * 2 + int(
                        self.offset / (signalParam.Speed / signalParam.SampleFrequency))), axis=0)
                    self.offset = self.offset % (signalParam.Speed / signalParam.SampleFrequency)
                    # fig=plt.figure("")
                    # plt.plot(self.INITALDISTANCE)
                    # plt.show()
                    return

    def track(self):
        ARRa = []
        ARRb = []
        ARRx = []
        ARRy = []
        while True:
            data = self.audiodata.get()
            data = np.fromstring(data, dtype=np.int16).reshape((-1, self.CHANNEL))
            self._frames = np.concatenate((self._frames, data), axis=0)
            if self._frames.shape[0] >= signalParam.ChirpSize * 4 + self.dataBufferLength * 2:
                data = self._frames[self.dataBufferLength:signalParam.ChirpSize + self.dataBufferLength,
                       self.CHANNELNUMBER].T
                amplitude = np.mean(np.mean(np.abs(data)))
                data = data / np.max(np.max(data))
                filtered0A = scipy.signal.lfilter(filterParam.LPF_b, filterParam.LPF_a,
                                                  data * np.tile(fmcw.up_s, (2, 1)), axis=1)
                filtered0B = np.flip(
                    scipy.signal.lfilter(filterParam.LPF_b, filterParam.LPF_a, data * np.tile(fmcw.dn_s, (2, 1)),
                                         axis=1), axis=1)
                Ind0A = np.argmax(np.abs(
                    scipy.fftpack.fftshift(
                        scipy.fftpack.fft(
                            filtered0A,
                            n=signalParam.FFTLength,
                            axis=1)
                        , axes=(1,))
                ), axis=1)
                Ind0B = np.argmax(np.abs(
                    scipy.fftpack.fftshift(
                        scipy.fftpack.fft(
                            filtered0B,
                            n=signalParam.FFTLength,
                            axis=1)
                        , axes=(1,))
                ), axis=1)
                self.offset = self.offset + self.SAMPLERANGEOFFSETPERSECOND * signalParam.ChirpT
                self._frames = np.delete(self._frames, range(0, signalParam.ChirpSize + int(
                    self.offset / (signalParam.Speed / signalParam.SampleFrequency))), axis=0)
                self.offset = self.offset % (signalParam.Speed / signalParam.SampleFrequency)

                data = self._frames[self.dataBufferLength:signalParam.ChirpSize + self.dataBufferLength,
                       self.CHANNELNUMBER].T
                data = data / np.max(np.max(data))
                filtered1A = np.flip(
                    scipy.signal.lfilter(filterParam.LPF_b, filterParam.LPF_a, data * np.tile(fmcw.dn_s, (2, 1)),
                                         axis=1), axis=1)
                filtered1B = scipy.signal.lfilter(filterParam.LPF_b, filterParam.LPF_a,
                                                  data * np.tile(fmcw.up_s, (2, 1)), axis=1)
                Ind1A = np.argmax(np.abs(
                    scipy.fftpack.fftshift(
                        scipy.fftpack.fft(
                            filtered1A,
                            n=signalParam.FFTLength,
                            axis=1)
                        , axes=(1,))
                ), axis=1)
                Ind1B = np.argmax(np.abs(
                    scipy.fftpack.fftshift(
                        scipy.fftpack.fft(
                            filtered1B,
                            n=signalParam.FFTLength,
                            axis=1)
                        , axes=(1,))
                ), axis=1)
                self.offset = self.offset + self.SAMPLERANGEOFFSETPERSECOND * signalParam.ChirpT
                self._frames = np.delete(self._frames, range(0, signalParam.ChirpSize + int(
                    self.offset / (signalParam.Speed / signalParam.SampleFrequency))), axis=0)
                self.offset = self.offset % (signalParam.Speed / signalParam.SampleFrequency)

                dA = signalParam.FFTResolution * (
                            Ind0A + Ind1A - signalParam.FFTLength) / 2 * signalParam.ChirpT / signalParam.ChirpBW * signalParam.Speed - self.offset
                dB = signalParam.FFTResolution * (
                            Ind0B + Ind1B - signalParam.FFTLength) / 2 * signalParam.ChirpT / signalParam.ChirpBW * signalParam.Speed - self.offset
                ARRa.append(list(dA))
                if len(ARRa) > self.smooth_size:
                    ARRa.pop(0)
                a = np.mean(ARRa)
                ARRb.append(list(dB))
                if len(ARRb) > self.smooth_size:
                    ARRb.pop(0)
                b = np.mean(ARRb)
                temp = (a ** 2 + self.AUDIODIS ** 2 - b ** 2) / 2 / self.AUDIODIS

                mm = np.nanmean(ARRa, axis=0)
                mm = (mm[0] - mm[1]) / self.phone_length
                nn = np.nanmean(ARRb, axis=0)
                nn = (nn[0] - nn[1]) / self.phone_length
                if -1 <= mm <= 1 and -1 <= nn <= 1:
                    ang = (np.arccos(mm) + np.arccos(nn)) / 2 / np.pi * 180
                elif -1 <= mm <= 1:
                    ang = np.arccos(mm) / np.pi * 180
                elif -1 <= nn <= 1:
                    ang = np.arccos(nn) / np.pi * 180
                else:
                    ang = 0

                ARRx.append(self.AUDIODIS / 2 - temp)
                if -1 <= temp / a <= 1:
                    ARRy.append(a * np.sin(np.arccos(temp / a)))
                else:
                    ARRy.append(0)
                if len(ARRx) > self.smooth_size:
                    ARRx.pop(0)
                if len(ARRy) > self.smooth_size:
                    ARRy.pop(0)
                x = np.mean(ARRx)
                y = np.mean(ARRy)
                if np.isnan(y): y = 0.0
                self.motiondata.append([[x, y], ang, amplitude])

    def run(self):
        print('----------AirMouse开始----------')
        while True:
            if self.audiodata.qsize():
                break
        self.preliminaryAlignment()
        self.clockSynchronization()
        self.track()
