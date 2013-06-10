import pstats
import simplejson as json


class FuncNameMapper(object):
    """Map func identifiers to an id."""

    def __init__(self):
        self.mapping = {}
        self.last_id = -1

    def get_next_index(self):
        self.last_id += 1
        return hex(self.last_id)[2:]

    def get_func_id(self, func):
        if func in self.mapping:
            return self.mapping[func]
        return self.mapping.setdefault(func, self.get_next_index())

    def get_mapping(self):
        return dict((v, k) for k, v in self.mapping.iteritems())    


iden = lambda v, _: v


def map_stat_values(stats, name_mapper):
    return stats[0:4] + (map_stats_dict(stats[4], name_mapper, iden),)


def map_stats_dict(stats, name_mapper, value_mapper):
    return dict((name_mapper.get_func_id(key), value_mapper(value, name_mapper)) 
                for key, value in stats.iteritems())


def encode_stats(stats):
    name_mapper = FuncNameMapper()
    resp = {
        'summary': {
            'total_cals': stats.total_calls,
            'prim_calls': stats.prim_calls,
            'total_tt':   stats.total_tt,
        },
        'stats':        map_stats_dict(stats.stats, name_mapper, map_stat_values),
        'func_mapping': name_mapper.get_mapping(),
    }
    return json.dumps(resp)
