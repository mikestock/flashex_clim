import enipy3 as lx
import numpy as np
import h5py
import matplotlib.pyplot as plt
import time

hdfFile = h5py.File( 'storms_flashes_50.h5', 'r' )

# months = [0,31,28,31,30,31,30,31,31,30,31,30,31]
months = [  0,  31,  59,  90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec', '']
figSize = 6.4,3.5

keyStart = '2015-01-11T00:00:00'
years    = 10
opRange  = 171, 250 #this is when we're supposed to be active, in Julian daya

def flash_times( storm ):
    flashTime = 0
    flashes   = []
    pulseTimes = storm[:,1]
    pulseTimes.sort()
    for p in pulseTimes:
        if p-flashTime > .1:
            flashes.append( p )
        flashTime = p
    return flashes 

# stormThreshs    = {0:0, 10:0, 50:0, 100:0}
flashesPerStorm = []
stormDurations  = []
stormWeeks      = []
#calculate some basic statistics on the storms
for stormKey in hdfFile:
    if stormKey < keyStart: continue
    #convert the key into a time_tup
    stormTime = time.strptime( stormKey, '%Y-%m-%dT%H:%M:%S' )
    if stormTime.tm_yday < opRange[0] or stormTime.tm_yday > opRange[1]:
        #this storm is not in our observation period
        continue
    storm = hdfFile[stormKey]
    #calculate some basics
    flashTimes    = flash_times( storm )
    numFlashes    = len( flashTimes )
    duration      = max(flashTimes)-min(flashTimes)
    flashesPerStorm.append( numFlashes )
    stormDurations.append( duration )

bins = [0,1,3,10,30,100,300,1000,3000,10000]
fig, ax1 = plt.subplots( 1,1 )
plt.hist( flashesPerStorm, bins=bins, weights=[1./years]*len(flashesPerStorm) )
plt.xlim( bins[1], bins[-1])
plt.semilogx()
plt.axvline( np.median( flashesPerStorm ), color='k', ls='--')
plt.xlabel( 'Flashes Per Storm' )
plt.ylabel( 'Storms/Year' )
plt.title( 'Storm Size Mean: %i, Median: %i'%(np.mean( flashesPerStorm ),np.median( flashesPerStorm )) )

#cumulative distribtuion

h = np.histogram( flashesPerStorm, bins=bins, weights=[1./years]*len(flashesPerStorm))
ax2 = plt.twinx( ax1 )
ax2.yaxis.label.set_color('tab:orange')
ax2.tick_params(axis='y', colors='tab:orange')
ax2.spines['right'].set_color('tab:orange')
ax2.plot( h[1][1:], len( flashesPerStorm )/years-np.cumsum( h[0] ), color='tab:orange' )
#draw some horizontal lines
flashesPerStorm = np.array( flashesPerStorm) 
x = [10, 50, 100]
y = [(flashesPerStorm>10).sum()/years, (flashesPerStorm>50).sum()/years, (flashesPerStorm>100).sum()/years,]
for i in range( len(y) ):
    ax2.plot( [x[i],bins[-1]],[y[i],y[i]], color='tab:orange', ls='--' )
    ax2.text( bins[-1],y[i],'%i'%x[i], color='tab:orange',  ha='right', va='bottom')
ax2.set_ylabel( 'Storms/Year > #' )


sys.exit()


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

