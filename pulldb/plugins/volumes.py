import json
from urllib import urlencode

from cement.core import controller, handler

class VolumeController(controller.CementBaseController):
    class Meta:
        label = 'volume'
        stacked_on = 'base'
        stacked_type = 'nested'

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

class VolumeGetController(controller.CementBaseController):
    class Meta:
        label = 'volume_get'
        stacked_on = 'volume'
        stacked_type = 'nested'
        aliases = ['get']
        aliases_only = True
        arguments = [
            (['identifier'], {
                'help': 'Comicvine identifier for volume',
                'action': 'store',
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/volumes/get/%s' % self.app.pargs.identifier
        resp, content = http_client.request(base_url + path)
        print content

class VolumeSearchController(controller.CementBaseController):
    class Meta:
        label = 'volume_search'
        stacked_on = 'volume'
        stacked_type = 'nested'
        aliases = ['search']
        aliases_only = True
        arguments = [
            (['query'], {
                'help': 'Search string',
                'action': 'store',
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/volumes/search?%s' % urlencode({
            'q': self.app.pargs.query,
        })
        resp, content = http_client.request(base_url + path)
        print content

def load():
    handler.register(VolumeController)
    handler.register(VolumeGetController)
    handler.register(VolumeSearchController)
