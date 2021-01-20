#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 12:11:57 2019

@author: liuki
"""

import sys
sys.path.append('../ThinkDsp')
import thinkdsp


class SoundSyn:
    def __init__(self):
        self.filename = None
        self.wave = None
        self.scale = equalTempScale()
        self.partialAmp = [0.5, 0.7, 0.3, 0.2, 0.1, 0.1]
        self.partialRatio = range(1,len(self.partialAmp)+1)
        self.bpm = 240
        
    def set_scale(self, scale):
        self.scale = scale
        
    def set_partial(self, partialAmp, partialRatio=None):
        self.partialAmp = partialAmp
        if (partialRatio == None):
            self.partialRatio = range(1,len(partialAmp)+1)        
        else:
            self.partialRatio = partialRatio
    
    def set_bpm(self, bpm):
        self.bpm = bpm

    def set_file(self, filename):
        self.filename = filename
        
    def make_wave(self):
        self.wave = readTrackFile(self.filename, self.scale, self.partialAmp, self.partialRatio, self.bpm)
        return self.wave


def readTrackFile(filename, scale, partialAmp, partialRatio, bpm):
    f = open(filename,"r")
    llist = f.readlines()

#        d = 1/len(llist)
#    d = 1
    track = llist[-1]
    trackList = track.split(" ")
    wave = genTrack(trackList, scale, partialAmp, partialRatio, bpm)
#        wave.scale(d)
    
    for track in llist[:-1]:
        trackList = track.split(" ")
        w = genTrack(trackList, scale, partialAmp, partialRatio, bpm)
#            w.scale(d)
        wave = wave + w
    
    wave.normalize()
    return(wave)


def genTrack(trackList, scale, partialAmp, partialRatio, bpm):
    l = len(trackList)
    noteList = [0]*l
    timeList = [0]*l
    
    for i in range(l):
        klist = trackList[i].split(".")
        noteList[i] = klist[0]
        timeList[i] = int(klist[1])
        
    w = genTrackByNoteList(noteList, timeList, scale, partialAmp, partialRatio, bpm)
    return(w)



def makeWindow(length, cutpoint):
    window = [0] * length
    '''
    for i in range(cutpoint):
        window[i] = 1.0*i / cutpoint
    for i in range(cutpoint, int(1.5*cutpoint)):
        window[i] = (2.0*cutpoint - i) / cutpoint        
    for i in range(int(1.5*cutpoint), length):
        window[i] = (length - i) / ((length - 1.5*cutpoint)*2)
    '''
    for i in range(cutpoint):
        window[i] = 1.0*i / cutpoint
    for i in range(cutpoint, length):
        window[i] = (length - i) / (length - cutpoint)

    return(window)
    

def equalTempScale():
    fe = [0]*89
    fe[0] = 0
    stdA = 440
    for i in range(88):
        fe[i+1] = stdA * 2**((i-48)/12)
    return(fe)

'''
def equalTempScaleArtSpec(note):
    fe = [0]*89
    fe[0] = 0
    pos = noteToIndex(note)
    std = etScale[pos]
    for i in range(88):
        fe[i+1] = std * (2.1)**((i-pos)/12)
    return(fe)
'''    
    

def pythScale(key):
    x = [0]*12
    x[0] = 1
    for i in range(11):
        r = x[i] * 3/2
        if r > 2 :
            r = r/2
        x[i+1] = r    
    x.sort()
    
    fp = [0]*89
    fp[0] = 0
    ind = noteToIndex(key+"1")
    freq = etScale[ind]
    for i in range(12):
        fp[ind+i] = freq * x[i]
        
    for p in range(5):
        for q in range(12):
            fp[ind + q + (p+1)*12] = fp[ind + q] * 2**(p+1)
    return(fp)

def justIntScale(key):
    x = [1, 16/15, 9/8, 6/5, 5/4, 4/3, 729/512, 3/2, 8/5, 5/3, 9/5, 15/8]
    
    fp = [0]*89
    fp[0] = 0
    ind = noteToIndex(key+"1")
    freq = etScale[ind]
    for i in range(12):
        fp[ind+i] = freq * x[i]
        
    for p in range(5):
        for q in range(12):
            fp[ind + q + (p+1)*12] = fp[ind + q] * 2**(p+1)
    return(fp)


        
def noteToIndex(note):
    note = note.strip()
    l = len(note)
    t = int(note[l-1])
    n = note[0]
    
    if n == 'P':
        return(0)
    
    if n == 'C':
        ret = 0
    elif n == 'D':
        ret = 2
    elif n == 'E':
        ret = 4
    elif n == 'F':
        ret = 5
    elif n == 'G':
        ret = 7
    elif n == 'A':
        ret = 9
    elif n == 'B':
        ret = 11
    
    if l == 3:
        if note[1] == '#':
            ret = ret + 1
        else:
            ret = ret - 1
    ret = ret + (t - 1) * 12 + 4

    return(ret)

'''
def ratioArtSpec(i):
    r = 0.0000611657*(i**4) - 0.00216153*(i**3) +0.0313233 *i**2 + 1.02024 * i - 0.0494663
    return r
'''

def genToneByFreq(rootFreq, dur, partialAmp, partialRatio):
#    sc = [0.7, 0.7, 0.7, 0.7, 0.7, 0.7]
#    sc = [0.5, 0.7, 0.3, 0.2, 0.1, 0.1]
#    sc = [0.5, 0.7, 0.7, 0.5, 0.4, 0.4, 0.5, 0.1, 0.3, 0.1, 0.1, 0.05]
#    sc = [0.5]
#    for i in range(len(sc)) :
#        sc[i] = sc[i]*3
#    sc = partialAmp        
    
    sin_sig = thinkdsp.SinSignal(freq=rootFreq, amp=partialAmp[0], offset=0)
    wave = sin_sig.make_wave(duration=dur, start=0, framerate=11025)

    window = makeWindow(len(wave.ys),100)
    wave.window(window)
    
    for i in range(1,len(partialAmp)):
#        sin_sig = thinkdsp.SinSignal(freq=rootFreq * ratioArtSpec(i+1), amp=sc[i], offset=0)
        sin_sig = thinkdsp.SinSignal(freq=rootFreq * partialRatio[i], amp=partialAmp[i], offset=0)
        w = sin_sig.make_wave(duration=dur, start=0, framerate=11025)
        
        window = makeWindow(len(wave.ys),100-i*10)
        w.window(window)
        wave = wave + w
        
    return(wave)    

def genToneByNote(note, dur, scale, partialAmp, partialRatio):
    f = scale[noteToIndex(note)]
    '''
    if scale == 1:
        f = etScale[noteToIndex(note)]
    elif scale == 2:
        f = pyScale[noteToIndex(note)]
    elif scale == 3:
        f = jiScale[noteToIndex(note)]    
#    elif scale == 4:
#        f = etScaleAS[noteToIndex(note)]    
    '''
    w = genToneByFreq(f,dur,partialAmp, partialRatio)
    return(w)
   

def genChordByNote(noteList, dur, scale, partialAmp, partialRatio):
#    d = 1/len(noteList)
    waveList = list()
    for note in noteList:
        w = genToneByNote(note,dur,scale,partialAmp, partialRatio)
#        w.scale(d)
        waveList.append(w)
    
    wave = waveList[0]
    for w in waveList[1:]:
        wave = wave + w
        
    wave.normalize()    
    return(wave)
        
def genTrackByNoteList(noteList, timeList, scale, partialAmp, partialRatio, bpm):
    '''    
    if len(noteList[0]) <= 3:  
        wave = genToneByNote(noteList[0],timeList[0]/3)
    else:
        nlist = noteList[0].split("+")
        wave = genChordByNote(nlist,timeList[0]/3)
    '''
    d = 60/bpm
    l = len(noteList)
    wave = thinkdsp.rest(0)        
    for i in range(l):
        if len(noteList[i]) <= 3:
            wave = wave | genToneByNote(noteList[i], timeList[i]*d, scale, partialAmp, partialRatio)
        else:
            nlist = noteList[i].split("+")
            wave = wave | genChordByNote(nlist, timeList[i]*d, scale, partialAmp, partialRatio)
                
#    wave.normalize()       
    return(wave)


    
    
#def getScale():
#    return(1)    

#def chordToNoteList(chord):
#    noteList = chord.split("+")
#    return(noteList)
  
etScale = equalTempScale()
#pyScale = pythScale("G")
#jiScale = justIntScale("G")

#etScaleAS = equalTempScaleArtSpec("D4")


#def main():
#    soundSyn = SoundSyn()
#
#if __name__ == "__main__":
#    main()




#infilename = "bwvAnhII114.txt"
#outfilename = 'bwv114.wav'

#infilename = "chordseq.txt"
#outfilename = 'chordseq.wav'

#w = readTrackFile(infilename)
#w.write(filename=outfilename)

