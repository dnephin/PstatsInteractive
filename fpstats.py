"""
Filter pstats.Stats using an include/exclude list of function/files and 
allocate `tottime` only to included functions.

Pstats are stored using this structure:

    { 
        (
            file_name,
            line_number,
            function_name,
        ): (
            primitive call count,
            total call count,
            total time,
            cumulative time,
            callers
        ),
        ...
    }

callers is:
    {
        (
            file_name, 
            line_number, 
            function_name
        ): (
            total call count,
            primitive call count,
            total time attributed to this caller,
            cumulative time attributed to this caller
        ),
        ...
    }


Rules are executed in the order they're configured.  If a function does not
match any rules, the default behaviour is inclusion. Once a rule is matched 
the comparison ends.

The config is a list of rules in the form:
[
    (action, match_type, rule),
    ...
]

 where:
 - action is one of INCLUDE, EXCLUDE
 - match_type is one of EQ, START, END
 - rule is a string to match against the filename


 `~` is the filename used for builtins.  
 The empty string ('') can be used with START to make everything.


Sample configuration.:
rules = [
    (EXCLUDE, EQ, '~'),
    (INCLUDE, START, '/src/tree/some/file'),
    (EXCLUDE, START, '/src/tree/others'),
]

"""
import marshal
from config import INCLUDE, EXCLUDE, START, END, EQ

class FilteredStats(object):


    def __init__(self, pstats, config):
        self.pstats = pstats
        self.ftimes = {}
        self.filtered_stats = {}
        self.load_config(config)

    def build_match_func(self, match_type, rule):
        """Create a closure that matches the param to the rule."""
        if match_type == EQ:
            return lambda name: name == rule
        elif match_type == START:
            return lambda name: name.startswith(rule)
        elif match_type == END:
            return lambda name: name.endswith(rule)
        else:
            raise ValueError("Unknown match type %s" % match_type)

    def load_config(self, config):
        self.rules = []
        for action, match_type, rule in config:
            match_func = self.build_match_func(match_type, rule)
            self.rules.append((action, match_func))

    def include(self, func):
        """Check if this function is included or excluded by our rules.
        Returns true if the function is included.
        """
        filename, line_no, funcname = func
        for action, match_func in self.rules:
            if match_func(filename):
                return action

        return True

    def calculate(self):
        for func, stats in self.pstats.stats.iteritems():
            if not self.include(func):
                self.set_ftimes(func, stats)
        self.build_new_stats()

    def set_ftimes(self, func, stats):
        """Assign portion of cumulative time to callers time. """
        cc, nc, tt, ct, callers = stats
        for c_func, caller in callers.iteritems():
            if not self.include(c_func):
                continue
            c_nc, c_cc, c_tt, c_ct = caller
            # TODO: allow line numbers to be different
            self.ftimes.setdefault(c_func, 0)
            self.ftimes[c_func] += c_ct

    def build_new_stats(self):
        self.filtered_stats = {}
        for func, stats in self.pstats.stats.iteritems():
            if not self.include(func):
                continue

            additional_time = self.ftimes.get(func)
            if not additional_time:
                self.filtered_stats[func] = stats
                continue

            stats = stats[0:2] + (stats[2] + additional_time,) + stats[3:]
            self.filtered_stats[func] = stats

    def write(self, filename):
        with open(filename, 'w') as f:
            marshal.dump(self.filtered_stats, f)


# TODO: proper arg parsing
if __name__ == '__main__':
    from pstats import Stats
    import sys
    filename = sys.argv[1] 
    p = Stats(filename)
    config = __import__(sys.argv[2]).rules
    fp = FilteredStats(p, config)
    fp.calculate()
    fp.write('output.profile')

