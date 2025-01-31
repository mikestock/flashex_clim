import enipy3 as lx
import numpy as np
import h5py
import os, glob


inPaths = sorted( glob.glob('/localdata/mstock/flashEx/climatology/pulses/*csv') )
lofarPt = 52.91426, 6.86933 

class Storm( ):
    def __init__( self, pulse ):
        self.startTime = pulse[1]
        self.stopTime  = pulse[1]
        self.lat       = pulse[2]
        self.lon       = pulse[3]
        self.pulses    = [pulse]
    def contains( self, pulse ):
        if pulse[1] < self.startTime-3600 or pulse[1] > self.stopTime+3600:
            #this pulse isn't inside the timebounds for being part of this storm
            return False
        else:
            return True
    def append( self, pulse ):
        self.stopTime  = max( self.stopTime,  pulse[1] )
        self.startTime = min( self.startTime, pulse[1] )
        self.pulses.append( pulse )

storms = []

tlnData = lx.Report( 'lofar_lxflash.state')
tlnData.truncate( tlnData.time.argsort() )

for iTln in range( len( tlnData.time) ):
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



# for inPath in inPaths:
#     print( inPath )
#     fh = open( inPath, 'r' )
#     header = fh.readline()

#     l = fh.readline()
#     while l.strip() != '':
#         pulse = lx.Pulse( l, format='csv', header=header)

#         #calculate distance from superterp
#         D = lx.oblate_distance( lofarPt, [pulse.lat, pulse.lon] )
#         if D > 50000:
#             l = fh.readline()
#             continue

#         report.append( pulse )

#         pulse = report._arr[-1].copy()
#         stormFound = False
        # for s in storms:
        #     if s.contains( pulse ):
        #         s.append( pulse )
        #         stormFound = True
        #         break
        # if not stormFound:
        #     print( 'new storm' )
        #     #make a new one
        #     s = Storm( pulse )
        #     storms.append( s )
        #     stormKey = lx.epoch2timestamp( s.startTime )

#         l = fh.readline()

# sys.exit()
#2017-07-19T14:34:19
#store the report state
# report.save_state( '/localdata/mstock/flashEx/climatology/lofar_superterp.state' )
#store the storms, we'll put them in a big hdf file
hdfFile = h5py.File( '/localdata/mstock/flashEx/climatology/storms_flashes.h5', 'w' )
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
