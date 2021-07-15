import pyaudio
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.colors as colors
from scipy import signal
from threading import Thread
import multiprocessing
import os

RATE = 44100
CHUNK = 256
FORMAT = pyaudio.paFloat32
CHANNELS = 1
TIME = 12

def record(conn_in):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK
                    )
    while True:
        os.write(conn_in.fileno(), stream.read(CHUNK, exception_on_overflow=False))


conn_out, conn_in = multiprocessing.Pipe(duplex=False)

t1 = Thread(target=record, args=(conn_in,))
t1.start()

fig = plt.figure(figsize=(12, 7))
ax = fig.add_subplot(1, 1, 1)
draw_data = np.zeros((1,))
while True:
    data = np.frombuffer(os.read(conn_out.fileno(), round(RATE / 4) * pyaudio.get_sample_size(FORMAT)),
                         dtype=np.float32)
    draw_data = np.hstack([draw_data, data])[-RATE * 10:]
    f, t, Sxx = signal.spectrogram(draw_data, mode='magnitude', fs=RATE, nperseg=1024)
    plt.pcolormesh(t, f, Sxx, shading='auto', norm=colors.LogNorm(vmin=Sxx.min(), vmax=Sxx.max()))
    plt.draw()
    plt.pause(0.0001)
    fig.clear()
