import enipy3 as lx
import numpy as np
import glob


lofarPt = 52.91426, 6.86933 
lofarReport = None
for iYear in range( 2015, 2025 ):
    pattern = '/data2/Archive/Flash/%i/??/LtgFlash????????.state'%iYear
    inPaths = sorted( glob.glob(pattern) )

    for inPath in inPaths:
        #load in this day of data
        r = lx.Report( inPath )

        #calculate the distance of all flashes to the superterp
        D = lx.pythagorean_distance( lofarPt, [r.lat, r.lon] )
        r.truncate( D<100000 )

        #append data to output report?
        if len( r.time ) == 0: continue
        if lofarReport == None:
            lofarReport = r
        else:
            lofarReport.append( r )
        print( inPath, len( lofarReport.time ) )

    #save output
    lofarReport.save_state( 'lofar_lxflash_100.state' )