import json

from cement.core import controller, handler
from dateutil.parser import parse as parse_date

class PullsController(controller.CementBaseController):
    class Meta:
        label = 'pull'
        stacked_on = 'base'
        stacked_type = 'nested'

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose()
    def list(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/pulls/list'
        resp, content = http_client.request(base_url + path)
        pull_list = json.loads(content)
        for pull in pull_list['results']:
            print "%6s %4s %s %r" % (
                pull['issue']['identifier'],
                pull['issue']['pubdate'],
                pull['issue']['name'],
                pull['pull']['read'],
            )

    @controller.expose()
    def new(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/pulls/new'
        resp, content = http_client.request(base_url + path)
        if resp.status == 200:
            pull_list = json.loads(content)
            for pull in pull_list['results']:
                pubdate = parse_date(pull['issue']['pubdate'])
                print '%7s %10s %s %s' % (
                    pull['issue']['identifier'],
                    pubdate.strftime('%Y-%m-%d'),
                    pull['volume']['name'],
                    pull['issue']['issue_number'],
                )
        else:
            self.app.log.error(resp, content)

def load():
    handler.register(PullsController)
