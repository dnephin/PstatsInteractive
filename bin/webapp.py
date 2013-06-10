
import os.path
from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.response import Response


def main():
    config = Configurator()
    config.add_settings(pstats_base_path=os.path.abspath('.'))
    config.scan('psi.web.views')
    return config.make_wsgi_app()


if __name__ == '__main__':
    app = main()
    server = make_server('0.0.0.0', 8080, main())
    server.serve_forever()
