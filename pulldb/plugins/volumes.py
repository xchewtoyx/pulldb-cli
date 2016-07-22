# pylint: disable=too-few-public-methods
import json
from urllib import urlencode

from cement.core import controller, handler
from dateutil.parser import parse as parse_date

class VolumeController(controller.CementBaseController):
    class Meta:
        label = 'volume'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['--raw'], {
                'help': 'Print raw json response',
                'action': 'store_true',
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose(help='Volume statistics')
    def stats(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/volumes/stats'
        resp, content = http_client.request(base_url + path)
        if resp.status == 200:
            if self.app.pargs.raw:
                print content
            else:
                issue_stats = json.loads(content)
                counts = issue_stats['counts']
                print 'Queued volumes: %d' % counts['queued']
                print 'Unindexed volumes: %d' % counts['toindex']
        else:
            self.app.log.error(resp, content)


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

class IndexController(controller.CementBaseController):
    class Meta:
        label = 'volume_index'
        stacked_on = 'volume'
        stacked_type = 'nested'
        aliases = ['index']
        aliases_only = True
        arguments = [
            (['identifier'], {
                'help': 'search index identifier',
                'action': 'store',
            }),
        ]

    @controller.expose(hide=True, aliases=['help'])
    def default(self):
        self.app.args.print_usage()

    @controller.expose()
    def drop(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/volumes/index/%s/drop' % self.app.pargs.identifier
        resp, content = http_client.request(base_url + path)
        results = json.loads(content)
        print '%(status)d %(message)s' % results

    @controller.expose()
    def reindex(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/volumes/%s/reindex' % self.app.pargs.identifier
        resp, content = http_client.request(base_url + path)
        results = json.loads(content)
        print '%(status)d %(message)s' % results

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
            (['--context'], {
                'help': 'Request context information',
                'action': 'store_true',
            }),
            (['--raw'], {
                'help': 'Print raw json response',
                'action': 'store_true',
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
        if self.app.pargs.context:
            path = path + '?context=1'
        resp, content = http_client.request(base_url + path)
        result = json.loads(content)
        if self.app.pargs.raw:
            print content
        elif result['status'] == 200:
            result = result['results'][0]
            print '%7s %s %s' % (
                result['volume']['identifier'],
                result['volume']['name'],
                result['volume']['publisher'],
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
        if self.app.pargs.context:
            path = path + '?context=1'
        resp, content = http_client.request(base_url + path)
        if self.app.pargs.raw:
            print content
            return
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


class VolumeQueueController(controller.CementBaseController):
    'Request that a single volume be marked for refresh.'
    class Meta(object):
        'Settings for queue controller'
        label = 'volume_queue'
        aliases = ['queue']
        aliases_only = True
        stacked_on = 'volume'
        stacked_type = 'nested'
        arguments = [
            (['volume'], {
                'help': 'Volume id to queue for updates.',
                'type': int,
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/volumes/%s/queue' % (
            self.app.pargs.volume,
        )
        resp, content = http_client.request(base_url + path)
        print content


class VolumeRefreshController(controller.CementBaseController):
    class Meta:
        label = 'volume_refresh'
        stacked_on = 'volume'
        stacked_type = 'nested'
        aliases = ['refresh']
        aliases_only = True
        arguments = [
            (['--active'], {
                'help': 'Process an active/fast shard',
                'action': 'store_true',
            }),
            (['--shard', '-s'], {
                'help': 'Shard number to process',
                'action': 'store',
                'type': int,
                'default': -1,
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'batch_url')
        if self.app.pargs.active:
            active = '/active'
        else:
            active = ''
        path = '/batch/volumes/refresh%s?shard=%s' % (
            active,
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
            (['--limit'], {
                'help': 'Number of results per page',
                'action': 'store',
                'type': int,
                'default': 10,
            }),
            (['--page'], {
                'help': 'Page of results to show',
                'action': 'store',
                'type': int,
                'default': 0,
            }),
            (['--raw'], {
                'help': 'Display raw json response',
                'action': 'store_true',
            }),
        ]

    @controller.expose(aliases=['help'], hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose(help='Search comicvine database')
    def comicvine(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        params = {
            'q': self.app.pargs.query,
            'page': self.app.pargs.page,
            'limit': self.app.pargs.limit,
        }
        path = '/api/volumes/search/comicvine?%s' % (urlencode(params),)
        resp, content = http_client.request(base_url + path)
        if self.app.pargs.raw:
            print content
        else:
            volumes = json.loads(content)
            for volume in volumes['results']:
                print '%7s %4s %4s %s [%s]' % (
                    volume['id'],
                    volume['start_year'],
                    volume['count_of_issues'],
                    volume['name'],
                    volume['id'],
                )

    @controller.expose(help='Search the local index')
    def local(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/volumes/search?%s' % urlencode({
            'q': self.app.pargs.query,
        })
        resp, content = http_client.request(base_url + path)
        if self.app.pargs.raw:
            print content
        else:
            volumes = json.loads(content)
            for volume in volumes['results']:
                print '%7s %4s %4s %s [%s]' % (
                    volume['volume_id'],
                    volume['start_year'],
                    volume.get('issue_count', ''),
                    volume['name'],
                    volume['id'],
                )

def load(app=None):
    handler.register(VolumeController)
    handler.register(IndexController)
    handler.register(VolumeAddController)
    handler.register(VolumeGetController)
    handler.register(VolumeQueueController)
    handler.register(VolumeRefreshController)
    handler.register(VolumeSearchController)
