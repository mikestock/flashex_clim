import enipy3 as lx

inputPath = '/localdata/mstock/flashEx/climatology/pulses/pulsepulse20241120.csv'
fh = open( inputPath, 'r' )
header = fh.readline()
l = fh.readline()
pulse = lx.Pulse( l, format='csv', header=header)

print ( pulse.amplitude )
print ( pulse.altitude )

r = lx.Report()
r.append( pulse )
print( r.decode( pulse ) )