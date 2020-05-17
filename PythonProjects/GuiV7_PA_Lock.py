# -*- coding: utf-8 -*-
"""
Created on Fri May 15 09:03:56 2020

@author: vmpsk
"""

from random import randint
# these two imports are important
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
import numpy as np 
import pyaudio
from scipy.fftpack import fft
from winsound import PlaySound, SND_FILENAME, SND_LOOP, SND_ASYNC # for asynchronous tone generation
from scipy.io.wavfile import write

#----plot data---
class MyApp(object):

    def __init__(self):
        # Pyaudio stream constants
        self.CHUNK = 512 * 1
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.pause = False
        # stream object
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, input_device_index = 1, rate=self.RATE, input=True, output=True,
            frames_per_buffer=self.CHUNK,)
        
######----Configure sound output for winsound-----------
        self.Amplitude = 0.1
        self.fLock = 440.0        # sine frequency, Hz, may be float    
        self.duration = 1.0   # in seconds, may be float
        self.sinWave = self.Amplitude*(np.sin(2*np.pi*np.arange(self.RATE*self.duration)*self.fLock/self.RATE)).astype(np.float32)
        write("example.wav", self.RATE, self.sinWave) 

####-----Main GUI code----
        self.data = np.array([])
        self.cond = False
        self.root = tk.Tk() # create main root window
        self.root.title("Real time FFT of audio-in/mic") # name the root window
        self.root.configure(background = 'black') # set back ground for root
        self.root.geometry("950x700") # set the root geometry   
        self.frame_bottom = tk.Frame(self.root, bg= 'black')
        self.frame_bottom.grid(row=1,column=0, sticky=tk.N)
        self.frame_right = tk.Frame(self.root, bg= 'black')
        self.frame_right.grid(row=0,column=1, sticky=tk.N)
        
#####-----create plot object on GUI----------
        self.fig = Figure(figsize=(7, 6)) # create figure object
        self.ax = self.fig.add_subplot(111) # Add subplot
        self.ax.set_title('Real time audio FFT')
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('Amplitude at lock frequency')
        self.ax.set_xlim(0, self.CHUNK)
        self.ax.set_ylim(0, 100006)
        self.freqs = (self.RATE/2)*np.linspace(0,1,int(self.CHUNK/2))
        self.lockFreqIndex = int(431/(self.RATE)*self.CHUNK) 
#        self.lines = self.ax.plot([],[], linestyle='-', marker='o')[0] # plot initialize
        self.lines = self.ax.plot([],[])[0] # plot initialize
#        self.lines = self.ax.semilogx([],[])[0] # semilogx plot initialize
#        self.lines.set_xdata(np.arange(0,len(self.data)))

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root) # Embed plot into root
#        self.canvas.get_tk_widget().place(x = 10, y = 10, width = 500, height = 400) # place plot in root and set geometry
        self.canvas.get_tk_widget().grid(row=0,column=0, padx=10, pady=10)
        self.canvas.draw() # draw plot on root
        
        

#######-----create buttons----------------------
#        self.root.update()
        self.start_button = tk.Button(self.frame_bottom, text = "Start", font = ('calibri', 12), command = self.plot_start)
        self.start_button.grid(row=0,column=0, padx=10, pady=10) #        self.start_button.place(x = 20, y = 450)
#        self.root.update()
        self.stop_button = tk.Button(self.frame_bottom, text = "Stop", font = ('calibri', 12), command = self.plot_stop)
        self.stop_button.grid(row=0,column=1, padx=10, pady=10)#        self.stop.place(x = 120, y = 450)
#        self.root.update()
        self.exit_button = tk.Button(self.frame_bottom, text = "Exit", font = ('calibri', 12), command = self.destroy)
        self.exit_button.grid(row=0,column=2, padx=10, pady=10)

        self.label_Freq = tk.Label(self.frame_right,text='Freq (Hz)')
        self.label_Freq.grid(row=0, column=0, padx=10, pady=10)
        self.var_fLock = tk.StringVar(value='440')
        self.entry_fLock = tk.Entry(self.frame_right,bd=5,width=5, textvariable=self.var_fLock)  
        self.entry_fLock.grid(row=0, column=1, padx=5, pady=5)
        
        self.label_Amp = tk.Label(self.frame_right,text='Ampl (V)')
        self.label_Amp.grid(row=1, column=0, padx=5, pady=5)
        self.var_Amplitude = tk.StringVar(value='0.1')
        self.entry_Amplitude = tk.Entry(self.frame_right,bd=5,width=5, textvariable=self.var_Amplitude)  
        self.entry_Amplitude.grid(row=1, column=1, padx=5, pady=5)

#        self.root.update()
        self.setButton = tk.Button(self.frame_right, text='Set', font = ('calibri', 12), command=self.set_sinwave)
        self.setButton.grid(row=2,column=0, padx=10, pady=10, columnspan=2)
#        self.root.update()
        self.playButton = tk.Button(self.frame_right, text='Play', font = ('calibri', 12), command=self.play_sound)
        self.playButton.grid(row=3,column=0, padx=10, pady=10)
#        self.root.update()
        self.pauseButton = tk.Button(self.frame_right, text='Pause', font = ('calibri', 12), command=self.stop_sound)
        self.pauseButton.grid(row=3, column=1, padx=10, pady=10)
#        self.root.update()
        self.lockButton = tk.Button(self.frame_right, text='Lock it (Hz)', font = ('calibri', 12), command=self.lock_sinwave)
        self.lockButton.grid(row=4,column=1)#, padx=10, pady=10, columnspan=2)

        self.var_fLocked = tk.StringVar(value='440')
        self.entry_fLocked = tk.Entry(self.frame_right,bd=5,width=5, textvariable=self.var_fLocked)  
        self.entry_fLocked.grid(row=4, column=0, padx=5, pady=10)


######--------------call self.plot_data method to start plotting on the canvas-----
        self.root.after(1, self.plot_data)
        self.root.mainloop() # Main root loop

    def set_sinwave(self):
        self.fLock = self.entry_fLock.get() # Get the lock in sinewave frequency(Hz) from the entry 
        self.Amplitude = float(self.entry_Amplitude.get()) # Get the sinewave amplitude from the entry   
        self.duration = 1.0   # in seconds, may be float
        self.sinWave = self.Amplitude*(np.sin(2*np.pi*np.arange(self.RATE*self.duration)*float(self.fLock)/self.RATE)).astype(np.float32)
        write("example.wav", self.RATE, self.sinWave)        

    def lock_sinwave(self):
        self.fLocked = float(self.entry_fLocked.get())
        self.lockFreqIndex = int(self.fLocked/(self.RATE)*self.CHUNK) 
        self.root.after(1, self.plot_data)

    def plot_data(self):
        if (self.cond == True):
            self.audioData = self.stream.read(self.CHUNK, exception_on_overflow = False)  #data = recorder.read(CHUNK)
            self.aData = np.frombuffer(self.audioData, dtype=np.int16)
            self.fftData = np.abs(fft(self.aData))
            self.a = self.fftData[self.lockFreqIndex]

            if(len(self.data)<self.CHUNK):
                self.data = np.append(self.data, self.a)
            else:
                self.data[0:self.CHUNK-1] = self.data [1:self.CHUNK]
                self.data[self.CHUNK-1] = float(self.a)

            self.lines.set_xdata(np.arange(0,len(self.data)))
            self.lines.set_ydata(self.data)

            self.canvas.draw()
        self.root.after(1, self.plot_data)

    def play_sound(self):
        PlaySound('example.wav', SND_FILENAME|SND_LOOP|SND_ASYNC)

    def stop_sound(self):
        PlaySound(None, SND_FILENAME)

    def plot_start(self):
        self.cond = True
        print(self.cond)

    def plot_stop(self):
        self.cond = False
        print(self.cond)
        
    def destroy(self):
        PlaySound(None, SND_FILENAME)
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.root.destroy()

test = MyApp()