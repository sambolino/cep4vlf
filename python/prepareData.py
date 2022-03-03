# -*- coding: utf-8 -*-
"""
Script for turning .mat narrow band dataset(s) into csv
some parts based on https://github.com/ISWI-Tunisia/PyDAQviewer/PlotNarrowData.py
"""

import os
import time
import math
import csv
directory = os.chdir('../data/2011/03_06')
#directory = os.chdir('../data/2012/04_15')
import scipy.io as matlab
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sg

class NBdataset:

    """ Represents AWESOME data from .mat file, with a fixed phase """
    PhaseFixLength90 = 60
    PhaseFixLength180 = 60

    def __init__(self, station, CH, amp, phi, fsL, tstart):
        self.averaging_length=fsL*NBdataset.PhaseFixLength180
        self.station = station
        self.CH = CH
        self.amp = amp
        self.phi = self._fixPhase(phi, self.averaging_length)
        self.fsL = fsL
        self.tstart = tstart
        self.startTime = self._makeStartTime(tstart)

    def _makeStartTime(self, tstart):
        S = np.array([3600, 60., 1.]) * tstart[3:6]
        startTime = S.sum(axis=0) # start time in seconds
        return(startTime)

    #fix_phasedata function are from:
    #http://stackoverflow.com/questions/34722985/matlab-fftfilt-equivalent-for-python
    @staticmethod
    def fix_phasedata180(phi, averaging_length):
        phi = np.reshape(phi,len(phi))
        x = np.exp(1j*phi*2./180.*np.pi)
        N = float(averaging_length)
        b, a = sg.butter(10, 1./np.sqrt(N))
        y = sg.filtfilt(b, a, x)
        output_phase = phi - np.array(list(map(round,((phi/180*np.pi-np.unwrap(np.angle(y))/2)%(2*np.pi))*180/np.pi/180)))*180
        temp = output_phase[0]%90
        output_phase = output_phase-output_phase[0]+temp
        s = output_phase[output_phase >= 180]
        for s in range(len(output_phase)):
            output_phase[s] = output_phase[s]-360
        return output_phase

    @staticmethod
    def fix_phasedata90(phi, averaging_length):
        phi = np.reshape(phi,len(phi))
        x = np.exp(1j*phi*4./180.*np.pi)
        N = float(averaging_length)
        b, a = sg.butter(10, 1./np.sqrt(N))
        y = sg.filtfilt(b, a, x)
        output_phase = phi - np.array(list(map(round,((phi/180*np.pi-np.unwrap(np.angle(y))/4)%(2*np.pi))*180/np.pi/90)))*90
        temp = output_phase[0]%90
        output_phase = output_phase-output_phase[0]+temp
        output_phase = output_phase%360
        s = output_phase[output_phase >= 180]
        for s in range(len(output_phase)):
            output_phase[s] = output_phase[s]-360
        return output_phase

    def _fixPhase(self, phi, averaging_length):
        data_phase_fixed180 = NBdataset.fix_phasedata180(phi, averaging_length)
        data_phase_fixed90 = NBdataset.fix_phasedata90(data_phase_fixed180, averaging_length)
        return(data_phase_fixed90)

# convert seconds to h:m:s.ms
def convertToHMS(s):
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%06.3f" % (h,m,s)

# lists of input amplitude and phase files
# here is the specification of AWESOME generated files
# http://solar-center.stanford.edu/SID/AWESOME/docs/AWESOME%20Data.pdf
# quick hint: make A&B or C&D pairs
# (although high resolution isn't actually needed for these purposes)
amp_filenames = ['BL110306000001DHO_006A.mat','BL110306000001ICV_016A.mat'] #['BL120415000000DHO_000A.mat','BL120415000000ICV_001A.mat']
phi_filenames = ['BL110306000001DHO_006B.mat','BL110306000001ICV_016B.mat'] #['BL120415000000DHO_000B.mat','BL120415000000ICV_001B.mat']

# you can add time offset, usually to avoid night hours
time_offset = 8*60*60

nbdatasets = []

#generate datasets from amp&phi pairs
for amp_filename, phi_filename in zip(amp_filenames, phi_filenames):
    if amp_filename[-8:-5]=='000': CH='N/S'
    else: CH='E/W'
    station= amp_filename[14:17]

    mat_a = matlab.loadmat(amp_filename, struct_as_record=False, squeeze_me=True)
    mat_p = matlab.loadmat(phi_filename, struct_as_record=False, squeeze_me=True)

    nbdataset = NBdataset(station, CH, amp = mat_a['data'],
            phi = mat_p['data'], fsL = mat_a['Fs'],
            tstart = [float(mat_a['start_year']),
                float(mat_a['start_month']),
                float(mat_a['start_day']),
                float(mat_a['start_hour']),
                float(mat_a['start_minute']),
                float(mat_a['start_second'])])
    nbdatasets.append(nbdataset)

nbrecords = []
tLo= []
filename = 'eventsfixed.csv'

for nbdataset in nbdatasets:

    # multiply offset by frequency (for high res case)
    index_offset = time_offset*nbdataset.fsL
    # dd mm yyyy format
    date = "%02d %02d %d " % (nbdataset.tstart[2], nbdataset.tstart[1], nbdataset.tstart[0])

    for i in range(index_offset, len(nbdataset.amp), 1):
        timestamp = i-index_offset
        tdelta = i
        t1= nbdataset.startTime + tdelta/nbdataset.fsL
        nbrecords.append([nbdataset.station, nbdataset.amp[i], nbdataset.phi[i],
            date+convertToHMS(t1), int(timestamp*1000)])
        tLo.append(t1)

header = ['station', 'amp', 'phi', 'date', 'timestamp']
sorted_nbrecords = sorted(nbrecords, key=lambda x: x[4])
with open(filename, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(sorted_nbrecords)

'''
print(data_phase_fixed90)
fig=plt.figure(figsize=(8,5))
ax1=plt.subplot(2, 1, 1)
plt.grid()
plt.plot(tLo, 20*np.log10(amp), '-b')
ax1.set_ylabel('Amplitude [dB]', fontsize=12)
#ax1.set_xticks([])
#plt.xlabel('Time (UT)', fontsize=12)
ax1.set_title ('Tunisia %.0f-%.0f-%.0f %s   %s Antenna'%(float(year),float(month),float(day),station,CH),
           fontsize=14, weight='bold')


ax2=plt.subplot(2, 1, 2, sharex=ax1)
ax2.grid()
ax2.plot(tLo[:len(data_phase_fixed90)], data_phase_fixed90, '-b')
#ax2.plot(tLo[:len(phi)], phi, '-b')
ax2.set_ylabel(r'Phase [$^\circ$]', fontsize=12)
ax2.set_xlabel('Time (UT)', fontsize=12)
plt.savefig("%s%s%s%s.png"%(year,month,day,station))
plt.savefig("%s%s%s%s.eps"%(year,month,day,station))

'''
