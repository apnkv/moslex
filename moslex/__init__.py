from pyramid.config import Configurator

from clld.interfaces import IMapMarker, IValueSet

# we must make sure custom models are known at database initialization!
from moslex import models


def main(global_config, **settings):
    settings['navbar.inverse'] = True

    config = Configurator(settings=settings)
    config.include('clld.web.app')
    config.include('clldmpg')

    return config.make_wsgi_app()
