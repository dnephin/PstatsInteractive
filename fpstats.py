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

"""


class FilteredStats(object):


    def __init__(self, pstats):
        self.pstats = pstats
        self.ftimes = {}


    def is_filtered(self, func):
        """Check if this function is included or excluded by our rules.
        Returns true if the function is excluded.
        """
        filename, line_no, funcname = func
        return not filename.startswith('openlets')


    def calculate(self):
        for func, stats in self.pstats.stats.iteritems():
            if self.is_filtered(func):
                self.set_ftimes(func, stats)
        # TODO: sum ftimes and tt

    def set_ftimes(self, func, stats):
        """Assign portion of cumulative time to callers time. """
        cc, nc, tt, ct, callers = stats
        for c_func, caller in callers.iteritems():
            if self.is_filtered(c_func):
                continue
            c_nc, c_cc, c_tt, c_ct = caller
            # TODO: allow line numbers to be different
            self.ftimes.setdefault(c_func, 0)
            self.ftimes[c_func] += c_ct


    # TODO: write out new file
