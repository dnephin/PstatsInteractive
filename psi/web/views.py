"""Views for PstatsInteractive."""

import os.path
import pstats
from pyramid.config import Configurator
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from psi import proftojson


@view_config(renderer='string')
def profile_index(request):
    return "Index"


def get_pstats_path(base, filename):
    filename = os.path.normpath(os.path.join(base, filename))
    if not filename.startswith(base) or not os.path.isfile(filename):
        raise exc.HTTPNotFound()
    return filename


@view_config(name='pstats', renderer='json')
def profile_json(request):
    base_path = request.registry.settings['pstats_base_path']
    filename = request.params.get('filename')
    if not filename:
        raise exc.HTTPBadRequest("Missing filename param.")
    stats = pstats.Stats(get_pstats_path(base_path, filename))
    return proftojson.encode_stats(stats)

