import enipy3 as lx
import numpy as np
import h5py
import os, glob


inPath  = 'lofar_lxflash_100.state'
outPath = 'storms_flashes_100.h5'
lofarPt = 52.91426, 6.86933 
searchRadius = 100000
stormTimeThreshold = 3600*2

class Storm( ):
    def __init__( self, pulse ):
        self.startTime = pulse[1]
        self.stopTime  = pulse[1]
        self.lat       = pulse[2]
        self.lon       = pulse[3]
        self.pulses    = [pulse]
    def contains( self, pulse ):
        if pulse[1] < self.startTime-stormTimeThreshold or pulse[1] > self.stopTime+stormTimeThreshold:
            #this pulse isn't inside the timebounds for being part of this storm
            return False
        else:
            return True
    def append( self, pulse ):
        self.stopTime  = max( self.stopTime,  pulse[1] )
        self.startTime = min( self.startTime, pulse[1] )
        self.pulses.append( pulse )

storms = []

tlnData = lx.Report( inPath )
tlnData.truncate( tlnData.time.argsort() )

for iTln in range( len( tlnData.time) ):
    #what's the distance to this flash 
    D = lx.pythagorean_distance( lofarPt, (tlnData.lat[iTln], tlnData.lon[iTln]))
    if D > searchRadius: 
        continue

    #put this flash into a storm
    flash = tlnData._arr[iTln].copy()
    stormFound = False
    for s in storms:
        if s.contains( flash ):
            s.append( flash )
            stormFound = True
            break
    if not stormFound:
        print( 'new storm' )
        #make a new one
        s = Storm( flash )
        storms.append( s )
        stormKey = lx.epoch2timestamp( s.startTime ) 


hdfFile = h5py.File( outPath , 'w' )
for s in storms:
    stormKey = lx.epoch2timestamp( s.startTime )
    print( stormKey )
    data = np.array( s.pulses )
    dset = hdfFile.create_dataset( stormKey, data=data )
    dset.attrs['startTime'] = s.startTime
    dset.attrs['stopTime'] = s.stopTime
    dset.attrs['lat'] = s.lat
    dset.attrs['lon'] = s.lon

hdfFile.close()
