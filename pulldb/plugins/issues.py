import json
from urllib import urlencode

from dateutil.parser import parse as parse_date

from cement.core import controller, handler

class IssueController(controller.CementBaseController):
    class Meta:
        label = 'issue'
        stacked_on = 'base'
        stacked_type = 'nested'

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

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
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/issues/get/%s' % self.app.pargs.identifier
        resp, content = http_client.request(base_url + path)
        print content

class IssueRefreshController(controller.CementBaseController):
    class Meta:
        label = 'issue_refresh'
        stacked_on = 'issue'
        stacked_type = 'nested'
        aliases = ['refresh']
        aliases_only = True
        arguments = [
            (['issue'], {
                'help': 'Issue to refresh',
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

def load():
    handler.register(IssueController)
    handler.register(IndexController)
    handler.register(IssueGetController)
    handler.register(IssueRefreshController)
    handler.register(IssueSearchController)
