import mock
from testify import TestCase, assert_equal, setup

from psi import proftojson


class FuncNameMapperTestCase(TestCase):

    @setup
    def setup_func_name_mapper(self):
        self.mapper = proftojson.FuncNameMapper()
        self.func = 'module', 123, 'name'

    def test_get_func_id_new(self):
        assert_equal(self.mapper.get_func_id(self.func), '0')
        assert_equal(self.mapper.get_func_id(('m', 1, 'asd')), '1')
        assert_equal(self.mapper.get_func_id(('a', 1, 'asd')), '2')

    def test_get_func_id_exists(self):
        assert_equal(self.mapper.get_func_id(self.func), '0')
        assert_equal(self.mapper.get_func_id(self.func), '0')

    def test_get_mapping(self):
        self.mapper.mapping = dict(a=1, b=2, c=3)
        expected = {1: 'a', 2: 'b', 3: 'c'}
        assert_equal(self.mapper.get_mapping(), expected)


class MapStatsTestCase(TestCase):

    def test_map_stats_dict(self):
        stats = {'a': 1, 'b': 2, 'c': 3}
        name_mapper = mock.create_autospec(proftojson.FuncNameMapper)
        value_mapper = mock.Mock()
        result = proftojson.map_stats_dict(stats, name_mapper, value_mapper)
        name_mapper.get_func_id.assert_has_calls(
            [mock.call(key) for key in ['a', 'b', 'c']], any_order=True)
        value_mapper.assert_has_calls(
            [mock.call(val, name_mapper) for val in range(1, 4)], any_order=True)
        assert result

    @mock.patch('psi.proftojson.map_stats_dict', autospec=True)
    def test_map_stat_values(self, mock_map_stats_dict):
        name_mapper = mock.create_autospec(proftojson.FuncNameMapper)
        stats = tuple(xrange(6))
        result = proftojson.map_stat_values(stats, name_mapper)
        assert_equal(result, (0, 1, 2, 3, mock_map_stats_dict.return_value))


class EncodeStats(TestCase):

    @mock.patch('psi.proftojson.json', autospec=True)
    @mock.patch('psi.proftojson.map_stats_dict', autospec=True)
    @mock.patch('psi.proftojson.FuncNameMapper', autospec=True)
    def test_encode_stats(self, mock_name_mapper, mock_map_stats_dict, mock_json):
        stats = mock.Mock(stats=mock.MagicMock())
        result = proftojson.encode_stats(stats)
        assert_equal(result, mock_json.dumps.return_value)
        mock_name_mapper.assert_called_with()
        name_mapper = mock_name_mapper.return_value
        mock_map_stats_dict.assert_called_with(stats.stats, name_mapper,
            proftojson.map_stat_values)
        name_mapper.get_mapping.assert_called_with()
