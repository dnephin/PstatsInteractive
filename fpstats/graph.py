"""

Create a graph structure from the call stats.

"""

class Node(object):
	"""A node in the graph."""

	def __init__(self, func=None, stats=None):
		self.func = func
		self.stats = stats[:4]

		self.caller_stats= stats[4]
		self.caller_nodes = []

		self.callee_stats = {}
		self.callee_nodes = []

	@property
	def ctime(self):
		return self.stats[3]

	@property
	def ttime(self):
		return self.stats[2]

	@property
	def sum_callees(self):
		return sum(s[3] for f, s in self.callee_stats.iteritems() if f != self.func)

	@property
	def diff_from_callees(self):
		return self.ctime - (self.ttime + self.sum_callees)

	def __repr__(self):
		return "Node(%r, %r)" % (self.func, self.stats)

class Graph(object):

	def __init__(self, pstats):
		self.stats = pstats.stats
		self.nodes = {}
		self.heads = []
		self.leafs = []

		for func, stats in self.stats.iteritems():
			self.add_func(func, stats)

		for func, node in self.nodes.iteritems():
			if not node.caller_nodes:
				self.heads.append(node)
				continue

			if not node.callee_nodes:
				self.leafs.append(node)


	def add_func(self, func, stats):
		# may already have been added by a callee
		if func not in self.nodes:
			self.nodes[func] = Node(func, stats)

		node = self.nodes[func]
		for c_func in stats[4].keys():
			c_node = self.nodes.get(c_func)
			if not c_node:
				self.nodes[c_func] = c_node = Node(c_func, self.stats[c_func])

			node.caller_nodes.append(c_node)
			c_node.callee_nodes.append(node)
			c_node.callee_stats[node.func] = stats[4][c_node.func]


	def isgood(self, node, threshold=0.00000001):
		diff = node.ctime - (node.ttime + node.sum_callees)
		if diff > threshold or diff <  - threshold:
			return node
		return None

if __name__ == "__main__":
	from pstats import Stats
	p = Stats('sample.profile')
	g = Graph(p)
	badones = [g.isgood(n) for n in g.nodes.values() if g.isgood(n)]	
