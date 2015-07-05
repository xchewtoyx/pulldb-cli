import json
from urllib import urlencode

from dateutil.parser import parse as parse_date

from cement.core import controller, handler

class IssueController(controller.CementBaseController):
    class Meta:
        label = 'issue'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['--raw'], {
                'help': 'Output raw json response',
                'action': 'store_true',
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose(help='issue statistics')
    def stats(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/issues/stats'
        resp, content = http_client.request(base_url + path)
        if resp.status == 200:
            if self.app.pargs.raw:
                print content
            else:
                issue_stats = json.loads(content)
                counts = issue_stats['counts']
                print 'Queued issues: %d' % counts['queued']
                print 'Unindexed issues: %d' % counts['toindex']
        else:
            self.app.log.error(resp, content)


class IndexController(controller.CementBaseController):
    class Meta:
        label = 'issue_index'
        stacked_on = 'issue'
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
        path = '/api/issues/index/%s/drop' % self.app.pargs.identifier
        resp, content = http_client.request(base_url + path)
        results = json.loads(content)
        print '%(status)d %(message)s' % results

    @controller.expose()
    def reindex(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/issues/%s/reindex' % self.app.pargs.identifier
        resp, content = http_client.request(base_url + path)
        results = json.loads(content)
        print '%(status)d %(message)s' % results

class IssueGetController(controller.CementBaseController):
    class Meta:
        label = 'issue_get'
        stacked_on = 'issue'
        stacked_type = 'nested'
        aliases = ['get']
        aliases_only = True
        arguments = [
            (['identifier'], {
                'help': 'Comicvine identifier for issue',
                'action': 'store',
            }),
            (['--raw'], {
                'help': 'Output raw json response',
                'action': 'store_true',
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/issues/get/%s' % self.app.pargs.identifier
        resp, content = http_client.request(base_url + path)
        if resp.status != 200:
            print resp, content
        elif self.app.pargs.raw:
            print content
        else:
            result = json.loads(content)
            for issue in result['results']:
                print issue.keys()
                print "%7s %10s %s [%s]" % (
                    issue['issue']['identifier'], issue['issue']['pubdate'],
                    issue['issue']['name'], issue['issue']['key']
                )

class IssueListController(controller.CementBaseController):
    class Meta:
        label = 'issue_list'
        stacked_on = 'issue'
        stacked_type = 'nested'
        aliases = ['list']
        aliases_only = True
        arguments = [
            (['--context'], {
                'help': 'Include object context',
                'action': 'store_true',
            }),
            (['--sort_key', '-k'], {
                'help': 'Field to sort on',
                'action': 'store',
            }),
            (['--reverse', '-r'], {
                'help': 'Reverse sort order',
                'action': 'store_true',
            }),
            (['--raw'], {
                'help': 'Output raw json response',
                'action': 'store_true',
            }),
            (['--queued'], {
                'help': 'Only list issues queued for refresh',
                'action': 'store_true',
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/issues/list'
        params = {}
        if self.app.pargs.queued:
            params['queued'] = 1
        if self.app.pargs.context:
            params['context'] = 1
        if self.app.pargs.sort_key:
            params['sort_key'] = self.app.pargs.sort_key
            if self.app.pargs.reverse:
                params['sort_order'] = 'desc'
            else:
                params['sort_order'] = 'asc'
        if params:
            path = path + '?%s' % urlencode(params)
        resp, content = http_client.request(base_url + path)
        if resp.status != 200:
            print resp, content
        elif self.app.pargs.raw:
            print content
        else:
            result = json.loads(content)
            for issue in result['results']:
                print issue.keys()
                print "%7s %10s %s [%s]" % (
                    issue['issue']['identifier'], issue['issue']['pubdate'],
                    issue['issue']['name'], issue['issue']['key']
                )

class IssueRefreshController(controller.CementBaseController):
    class Meta:
        label = 'issue_refresh'
        stacked_on = 'issue'
        stacked_type = 'nested'
        aliases = ['refresh']
        aliases_only = True
        arguments = [
            (['issue'], {
                'help': 'Issue/shard to refresh',
                'action': 'store',
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/issues/refresh/%s' % (
                self.app.pargs.issue,
            )
        resp, content = http_client.request(base_url + path)
        print content

    @controller.expose()
    def shard(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'batch_url')
        path = '/batch/issues/refresh?shard=%s' % (
                self.app.pargs.issue,
            )
        resp, content = http_client.request(base_url + path)
        print content

class IssueSearchController(controller.CementBaseController):
    class Meta:
        label = 'issue_search'
        stacked_on = 'issue'
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
        path = '/api/issues/search?%s' % urlencode({
            'q': self.app.pargs.query,
        })
        resp, content = http_client.request(base_url + path)
        issues = json.loads(content)
        print "Found %s matches" % issues['count']
        for issue in issues['results']:
            if issue.get('pubdate'):
                pubdate = parse_date(issue['pubdate']).strftime('%Y-%m-%d')
            else:
                pubdate = ''
            print "%7d %10s %s" % (
                int(float(issue['issue_id'])),
                pubdate,
                issue.get('name', 'key=%s' % issue['id']),
            )

def load(app=None):
    handler.register(IssueController)
    handler.register(IndexController)
    handler.register(IssueGetController)
    handler.register(IssueListController)
    handler.register(IssueRefreshController)
    handler.register(IssueSearchController)
