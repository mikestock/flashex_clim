import enipy3 as lx
import numpy as np
import h5py
import matplotlib.pyplot as plt
import time

hdfFile = h5py.File( '/localdata/mstock/flashEx/climatology/storms.h5', 'r' )

# months = [0,31,28,31,30,31,30,31,31,30,31,30,31]
months = [  0,  31,  59,  90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec', '']
figSize = 6.4,3.5

keyStart = '2015-01-11T00:00:00'
years = 10

def flash_times( storm ):
    flashTime = 0
    flashes   = []
    pulseTimes = storm[:,1]
    pulseTimes.sort()
    for p in pulseTimes:
        if p-flashTime > 1:
            flashes.append( p )
        flashTime = p
    return flashes 


flashesPerStorm = []
flashesPerDeployment = []
periodKeys = []
stormDays   = np.zeros( 366//2 )
flashCounts = np.zeros( 366//2 )
for stormKey in hdfFile:
    if stormKey < keyStart: continue
    print( stormKey )
    storm = hdfFile[stormKey]

    flashes = flash_times( storm )

    flashesPerStorm.append( len(flashes) )
    t = storm.attrs['startTime']

    d = time.gmtime( t ).tm_yday
    if d >= 171 and d <= 250 :
        flashesPerDeployment.append( len(flashes) )
        periodKeys.append( stormKey )
    d = ( int(d//2) )

    if len(flashes) > 5:
        stormDays[ d ] += 1
    flashCounts[d] += len(flashes)


stormDays   /= 20
flashCounts /= 10 * 48

#Stormy Periods
plt.figure( figsize=figSize )
plt.bar( np.arange(0,366,2), stormDays, width=2, align='edge' )

plt.xlim( 0, 365 )
plt.ylim( 0, 1 )

for i in range( len( months ) ):
    d = months[i]
    plt.axvline( d, color=(0,0,0,.5) )
    plt.text( d+2, .95, monthNames[i], color=(0,0,0,.5), horizontalalignment='left', verticalalignment='top')

plt.xlabel( 'Day of the Year' )
plt.ylabel( 'Probability of Storminess' )
plt.tight_layout()
plt.savefig( 'StormProbability_year.png', dpi=200  )

#set limits to Jun 20 -- Sep 7
plt.xlim( 171, 250)
plt.savefig( 'StormProbability_period.png', dpi=200  )


#Total Flash Counts
plt.figure( figsize=figSize )
plt.bar( np.arange(0,366,2), flashCounts, width=2, align='edge' )

plt.xlim( 0, 365 )
# plt.ylim( 0, 1500 )

for i in range( len( months ) ):
    d = months[i]
    plt.axvline( d, color=(0,0,0,.5) )
    # plt.text( d+2, 1450, monthNames[i], color=(0,0,0,.5), horizontalalignment='left', verticalalignment='top')
plt.xlabel( 'Day of the Year' )
plt.ylabel( 'Flashes per Hour' )
plt.tight_layout()
plt.savefig( 'flashrate_year.png', dpi=200  )
plt.xlim( 171, 250)
plt.savefig( 'flashrate_period.png', dpi=200  )

#the diurnal variability
flashHours = np.zeros( 24 )
flashNorm  = 0
for stormKey in periodKeys:
    storm = hdfFile[ stormKey ]
    if len( storm[:] ) < 50: continue
    flashNorm += 1
    flashes = flash_times( storm )
    for t in flashes:
        h = time.gmtime(t).tm_hour
        flashHours[h] += 1

flashHours /= flashNorm#10*(250-171)
plt.figure( figsize=figSize )
plt.bar( np.arange(24), flashHours, width=1, align='edge' )

plt.xlim( 0,24 )

plt.xlabel( 'UTC Hour' )
plt.ylabel( 'Flashes per Hour' )
plt.tight_layout()
plt.savefig( 'flashrate_diurnal.png', dpi=200  )

