import json
from urllib import urlencode

from cement.core import controller, handler

class IssueController(controller.CementBaseController):
    class Meta:
        label = 'issue'
        stacked_on = 'base'
        stacked_type = 'nested'

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

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
            (['--shard'], {
                'help': 'Shard number to process',
                'action': 'store',
                'type': int,
                'default': 1,
            }),
            (['--shard_count'], {
                'help': 'Total number of shards',
                'action': 'store',
                'type': int,
                'default': 0,
            }),
            (['--volume'], {
                'help': 'Volume to refresh',
                'action': 'store',
                'default': None,
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        if self.app.pargs.volume:
            path = '/api/issues/refresh/%s' % (
                self.app.pargs.volume,
            )
        else:
            path = '/api/issues/refresh/%s/%s' % (
                self.app.pargs.shard_count,
                self.app.pargs.shard,
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
        for issue in issues:
            print "%7s %s %s %s" % (
                issue['issue']['identifier'],
                issue['issue']['pubdate'],
                issue['volume']['name'],
                issue['issue']['issue_number'],
            )

def load():
    handler.register(IssueController)
    handler.register(IssueGetController)
    handler.register(IssueRefreshController)
    handler.register(IssueSearchController)
