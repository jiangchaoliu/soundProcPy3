#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 16:12:50 2018

@author: liqianchen
"""

import numpy
import wave,sys,os
from subprocess import check_output,CalledProcessError
max_amplitude = 2**15 - 1

def getstatusoutput(cmd):
    try:
        data = check_output(cmd, shell=True, universal_newlines=True)
        status = 0
    except CalledProcessError as ex:
        data = ex.output
        status = ex.returncode
    if data[-1:] == '\n':
        data = data[:-1]
    return status, data

def note(frequency, length, amplitude=1,
         sample_rate=44100):
    time_points = numpy.linspace(0, length,
                                 length*sample_rate)
    data = numpy.sin(2*numpy.pi*frequency*time_points)
    data = amplitude*data
    return data


def write(data, filename, sample_rate=44100):
    print(type(data))   
    ofile = wave.open(filename, 'w')
    if len(numpy.shape(data)) == 2:
        ofile.setnchannels(numpy.shape(data)[1])
    else:
        ofile.setnchannels(1)
    ofile.setsampwidth(2)
    ofile.setframerate(sample_rate)
    newdata = data.flatten()
    ofile.writeframesraw(newdata.astype(numpy.int16).tostring())
    ofile.close()
    
def read(filename):
    ifile = wave.open(filename)
    channels = ifile.getnchannels()
    sample_rate = ifile.getframerate()
    frames = ifile.getnframes()
    data = ifile.readframes(frames)
    data = numpy.frombuffer(data, dtype=numpy.uint16)
    sounddata = data.reshape((len(data)//channels,channels))
    return sounddata.astype(numpy.int16),sample_rate


def play(data, sample_rate=44100, player=None):
    tmpfile = 'tmp.wav'
    write(data, tmpfile, sample_rate)

    if player:
        msg = 'Unable to open sound file with %s' %player
        if sys.platform[:3] == 'win':
            status = os.system('%s %s' %(player, tmpfile))
        else:
            status, output =getstatusoutput('%s %s' %(player, tmpfile))
            msg += '\nError message:\n%s' %output
        if status != 0:
            raise OSError(msg)
        return

    if sys.platform[:5] == 'linux':
        open_commands = ['gnome-open', 'kmfclient exec', 'exo-open', 'xdg-open', 'open']
        for cmd in open_commands:
            status, output = getstatusoutput('%s %s' %(cmd, tmpfile))
            if status == 0:
                break
        if status != 0:
            raise OSError('Unable to open sound file, try to set player'\
                              ' keyword argument.')

    elif sys.platform == 'darwin':
        print('mac')
        getstatusoutput('open %s' %tmpfile)
    else:
        # assume windows
        os.system('start %s' %tmpfile)

def play_triangle_fourier(T, length, N):
    sample_rate = 44100
    t = numpy.linspace(0, length, sample_rate*length)
    data = numpy.zeros(t.size)
    for n in range(1,N+1,2):
        data = data - numpy.cos(2*numpy.pi*n*t/T)/n**2
    data = data*8/(numpy.pi**2)
    data = max_amplitude*data/max(abs(data))
    data = data.astype(numpy.int16)
    data = data.reshape(len(data), 1)
    play(data,sample_rate)


def add_echo(data, beta=0.8, delay=0.5,
             sample_rate=44100):
    newdata = data.copy()
    shift = int(delay*sample_rate) # b (math symbol)
    for i in range(shift, len(data)):
        newdata[i] = beta*data[i] + (1-beta)*data[i-shift]
    return newdata

def Nothing_Else_Matters():
    E1 = note(164.81, .5)
    G = note(392, .5)
    B = note(493.88, .5)
    E2 = note(659.26, .5)
    intro = numpy.concatenate((E1, G, B, E2, B, G))
    high1_long = note(987.77, 1)
    high1_short = note(987.77, .5)
    high2 = note(1046.50, .5)
    high3 = note(880, .5)
    high4_long = note(659.26, 1)
    high4_medium = note(659.26, .5)
    high4_short = note(659.26, .25)
    high5 = note(739.99, .25)
    pause_long =  note(0, .5)
    pause_short = note(0, .25)
    song = numpy.concatenate(
      (intro, intro, high1_long, pause_long, high1_long,
       pause_long, pause_long,
       high1_short, high2, high1_short, high3, high1_short,
       high3, high4_short, pause_short, high4_long, pause_short,
       high4_medium, high5, high4_short))
    song *= max_amplitude
    return song

    
def play_atone():
    data = note(440, 2)
    data = max_amplitude*data
    data = data.astype(numpy.int16)
    write(data, 'Atone.wav')
    nd,rate = read('Atone.wav')
    play(nd,rate)
def play_echo():
    data,rate = read('nihao.wav')
    data = data.astype(float)
    data = add_echo(data, beta=2)
    data = data.astype(numpy.int16)
    play(data)

def play_song():
    song = Nothing_Else_Matters()
    play(song)

#play_atone()
#play_echo()
#play_song()    
