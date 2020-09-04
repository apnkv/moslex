from functools import partial

from pyramid.config import Configurator
from clld.web.app import menu_item

# we must make sure custom models are known at database initialization!
from moslex import models, views


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['navbar.inverse'] = True
    config = Configurator(settings=settings)
    config.include('clldmpg')
    config.register_menu(
        ('dataset', partial(menu_item, 'dataset', label='Home')),
        ('languages', partial(menu_item, 'languages', label='Languages')),
        ('parameters', partial(menu_item, 'parameters', label='Concepts')),
        ('values', partial(menu_item, 'values', label='Forms')),
        ('sources', partial(menu_item, 'sources', label='References')),
        ('about', partial(menu_item, 'about', label='About')),
    )
    config.add_route_and_view(
        'home.' + 'downloads',
        '/meta/downloads',
        getattr(views, 'downloads'),
        renderer='downloads' + '.mako')
    config.include('clld.web.app')
    return config.make_wsgi_app()
