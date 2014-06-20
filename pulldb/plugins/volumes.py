import json
from urllib import urlencode

from cement.core import controller, handler
from dateutil.parser import parse as parse_date

class VolumeController(controller.CementBaseController):
    class Meta:
        label = 'volume'
        stacked_on = 'base'
        stacked_type = 'nested'

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

class VolumeAddController(controller.CementBaseController):
    class Meta:
        label = 'volume_add'
        stacked_on = 'volume'
        stacked_type = 'nested'
        aliases = ['add']
        aliases_only = True
        arguments = [
            (['ids'], {
                'help': 'Comicvine identifier for volume',
                'action': 'store',
                'nargs': '+',
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/volumes/add'
        data = json.dumps({
            'volumes': self.app.pargs.ids,
        })
        resp, content = http_client.request(
            base_url + path,
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=data,
        )
        results = json.loads(content)
        failed = results['results'].get('failed', [])
        print '%d issues failed:\n%r' % (len(failed), failed)
        added = results['results'].get('added', [])
        print '%d issues added:\n%r' % (len(added), added)
        skipped = results['results'].get('existing', [])
        print '%d issues skipped:\n%r' % (len(skipped), skipped)

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
        self.app.args.print_usage()

    @controller.expose()
    def get(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/volumes/%s/get' % self.app.pargs.identifier
        resp, content = http_client.request(base_url + path)
        result = json.loads(content)
        if result['status'] == 200:
            print '%7s %s' % (
                result['volume']['identifier'],
                result['volume']['name'],
            )
        else:
            print '%d %s' % (
                result['status'],
                result['message'],
            )

    @controller.expose()
    def list(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/volumes/%s/list' % self.app.pargs.identifier
        resp, content = http_client.request(base_url + path)
        result = json.loads(content)
        if result['status'] == 200:
            for issue in result['results']:
                print '%7s %s %s %s' % (
                    issue['identifier'],
                    issue['pubdate'],
                    result['volume']['name'],
                    issue['issue_number'],
                )
        else:
            print '%d %s' % (
                result['status'],
                result['message'],
            )

class VolumeRefreshController(controller.CementBaseController):
    class Meta:
        label = 'volume_refresh'
        stacked_on = 'volume'
        stacked_type = 'nested'
        aliases = ['refresh']
        aliases_only = True
        arguments = [
            (['--shard'], {
                'help': 'Shard number to process',
                'action': 'store',
                'type': int,
            }),
            (['--shard_count'], {
                'help': 'Total number of shards',
                'action': 'store',
                'type': int,
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/volumes/refresh/%s/%s' % (
            self.app.pargs.shard_count,
            self.app.pargs.shard,
        )
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
        volumes = json.loads(content)
        for volume in volumes['results']:
            print '%7s %4s %4s %s' % (
                volume['volume_id'],
                volume['start_year'],
                volume.get('issue_count', ''),
                volume['name'],
            )

def load():
    handler.register(VolumeController)
    handler.register(VolumeAddController)
    handler.register(VolumeGetController)
    #handler.register(VolumeRefreshController)
    handler.register(VolumeSearchController)
