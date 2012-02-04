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
import itertools
import marshal
import operator
import re
from config import INCLUDE, EXCLUDE, START, END, EQ


# TODO: filter by caller to a single servlet action
# TODO: test
# TODO: look into CPU seconds difference


class FilteredStats(object):


    def __init__(self, pstats, config):
        self.pstats = pstats
        self.ftimes = {}
        self.filtered_stats = {}
        self.load_config(config)

    def matches_rule(self, func_def, rule):
        if len(rule) == 3:
            action, match_type, filename = rule
            funcname = None
        else:
            action, match_type, filename, funcname = rule

        target_filename, linenum, target_funcname = func_def
        funcmatch = not funcname or funcname == target_funcname

        if match_type == EQ:
            return funcmatch and filename == target_filename
        elif match_type == START:
            return funcmatch and target_filename.startswith(filename)
        elif match_type == END:
            return funcmatch and target_filename.endswith(filename)
        else:
            raise ValueError("Unknown match type %s" % match_type)

    def load_config(self, config):
        self.rules = []
        for rule in config.rules:
            # TODO: validate rules
            self.rules.append(rule)

    def include(self, func):
        """Check if this function is included or excluded by our rules.
        Returns true if the function is included.
        """
        for rule in self.rules:
            if self.matches_rule(func, rule):
                return rule[0]

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



class Converter(object):
    """Combine different versions of code into a unified version."""

    def __init__(self, pstats, config):
        self.pstats = pstats
        self.combined_stats = {}
        self.load_config(config)


    def load_config(self, config):
        self.converters = []
        for idx, find, replace in config.converters:
            self.converters.append((idx, re.compile(find), replace))


    def apply_conversions(self, func_def):
        func_def = list(func_def)
        for idx, find_pattern, replace in self.converters:
            func_def[idx] = find_pattern.sub(replace, func_def[idx])
        return tuple(func_def)


    def combine_callers(self, new_callers, old_callers):
        callers = {}
        for c_func, c_stats in itertools.chain(
                new_callers.iteritems(), old_callers.iteritems()):
            old_stats = callers.get(c_func)
            if not old_stats:
                callers[c_func] = c_stats
                continue

            callers[c_func] = tuple(map(operator.add, old_stats, c_stats))
        return callers


    def combine(self, func_def, stats, new_callers):
        old_stats = self.combined_stats.get(func_def)
        if not old_stats:
            self.combined_stats[func_def] = stats[:4] + (new_callers,)
            return
        
        combined_stats = map(operator.add, old_stats[:4], stats[:4])
        combined_stats.append(self.combine_callers(new_callers, old_stats[4]))
        self.combined_stats[func_def] = tuple(combined_stats)


    def process_stats(self):
        for func, stats in self.pstats.stats.iteritems():
            new_func = self.apply_conversions(func)
            new_callers = dict(
                (self.apply_conversions(c_func), c_stats)
                for c_func, c_stats in stats[4].iteritems()
            )
            self.combine(new_func, stats, new_callers)
        return self.combined_stats

    # TODO: base class
    def write(self, filename):
        with open(filename, 'w') as f:
            marshal.dump(self.combined_stats, f)


# TODO: proper arg parsing
if __name__ == '__main__':
    from pstats import Stats
    import sys
    filename = sys.argv[1] 
    p = Stats(filename)
    config = __import__(sys.argv[2])
    fp = FilteredStats(p, config)
    fp.calculate()
    fp.write('output.profile')

    p = Stats('output.profile')
    c = Converter(p, config)
    c.process_stats()
    c.write('converted.profile')




