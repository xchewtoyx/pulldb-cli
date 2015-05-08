import json
from urllib import urlencode

from cement.core import controller, handler
from dateutil.parser import parse as parse_date

class ArcController(controller.CementBaseController):
    class Meta:
        label = 'arc'
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

    @controller.expose(help='Arc statistics')
    def stats(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/arcs/stats'
        resp, content = http_client.request(base_url + path)
        if resp.status == 200:
            if self.app.pargs.raw:
                print content
            else:
                issue_stats = json.loads(content)
                counts = issue_stats['counts']
                print 'Queued arcs: %d' % counts['queued']
                print 'Unindexed arcs: %d' % counts['toindex']
        else:
            self.app.log.error(resp, content)


class ArcAddController(controller.CementBaseController):
    class Meta:
        label = 'arc_add'
        stacked_on = 'arc'
        stacked_type = 'nested'
        aliases = ['add']
        aliases_only = True
        help = 'Add story arc'
        arguments = [
            (['ids'], {
                'help': 'Comicvine identifier for arc',
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
        path = '/api/arcs/add'
        data = json.dumps({
            'arcs': self.app.pargs.ids,
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
        label = 'arc_index'
        stacked_on = 'arc'
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
        path = '/api/arcs/index/%s/drop' % self.app.pargs.identifier
        resp, content = http_client.request(base_url + path)
        results = json.loads(content)
        print '%(status)d %(message)s' % results

    @controller.expose()
    def reindex(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/arcs/%s/reindex' % self.app.pargs.identifier
        resp, content = http_client.request(base_url + path)
        results = json.loads(content)
        print '%(status)d %(message)s' % results

class ArcGetController(controller.CementBaseController):
    class Meta:
        label = 'arc_get'
        stacked_on = 'arc'
        stacked_type = 'nested'
        aliases = ['get']
        aliases_only = True
        arguments = [
            (['identifier'], {
                'help': 'Comicvine identifier for story arc',
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
        path = '/api/arcs/%s/get' % self.app.pargs.identifier
        if self.app.pargs.context:
            path = path + '?context=1'
        resp, content = http_client.request(base_url + path)
        result = json.loads(content)
        if self.app.pargs.raw:
            print content
        elif result['status'] == 200:
            result = result['results'][0]
            print '%7s %s %s' % (
                result['arc']['identifier'],
                result['arc']['name'],
                result['arc']['publisher'],
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
        path = '/api/arcs/%s/list' % self.app.pargs.identifier
        if self.app.pargs.context:
            path = path + '?context=1'
        resp, content = http_client.request(base_url + path)
        if self.app.pargs.raw:
            print content
        else:
            result = json.loads(content)
            if result['status'] == 200:
                for issue in result['results']:
                    print '%7s %s %s' % (
                        issue['identifier'],
                        issue['pubdate'],
                        issue['name'],
                    )
            else:
                print '%d %s' % (
                    result['status'],
                    result['message'],
                )

class ArcSearchController(controller.CementBaseController):
    class Meta:
        label = 'arc_search'
        stacked_on = 'arc'
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
        path = '/api/arcs/search/comicvine?%s' % (urlencode(params),)
        resp, content = http_client.request(base_url + path)
        if self.app.pargs.raw:
            print content
        else:
            arcs = json.loads(content)
            for arc in arcs['results']:
                print '%7s %4s %4s %s' % (
                    arc['id'],
                    arc.get('first_issue_date'),
                    arc.get('count_of_issues'),
                    arc['name'],
                )

    @controller.expose(help='Search the local index')
    def local(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/arcs/search/local?%s' % urlencode({
            'q': self.app.pargs.query,
        })
        resp, content = http_client.request(base_url + path)
        if self.app.pargs.raw:
            print content
        else:
            arcs = json.loads(content)
            for arc in arcs['results']:
                print '%7s %4s %4s' % (
                    arc['arc_id'],
                    arc.get('issue_count', ''),
                    arc.get('name', ''),
                )

def load(app=None):
    handler.register(ArcController)
    handler.register(IndexController)
    handler.register(ArcAddController)
    handler.register(ArcGetController)
    handler.register(ArcSearchController)
