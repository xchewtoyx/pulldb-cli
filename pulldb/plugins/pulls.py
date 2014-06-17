import json

from cement.core import controller, handler

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

def load():
    handler.register(PullsController)
