from fpstats import *
from pstats import Stats
import sys

class Config(object):
	rules = [
		(INCLUDE, START, 'openlets'),
		(EXCLUDE, START, '')
	]



def related(func, p, q):

	def drop_callers(i):
		return i[:4]
	
	def get_callees(o):
		for item in o.stats.iteritems():
			if func in item[1][4]:
				yield (item[0], item[1][:4])

	return p.stats[func], q.stats[func], list(get_callees(p)), list(get_callees(q))


filename = 'sample.profile'
p = Stats(filename)
p.sort_stats('cum')
p.print_stats(5)

fp = FilteredStats(p, Config)
fp.calculate()
fp.write('output.profile')

q = Stats('output.profile')
q.sort_stats('cum')
q.print_stats(5)

k = fp.ftimes.keys()
