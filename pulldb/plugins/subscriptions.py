import json

from cement.core import controller, handler

class SubscriptionController(controller.CementBaseController):
    class Meta:
        label = 'subscription'
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
        path = '/api/subscriptions/list'
        resp, content = http_client.request(base_url + path)
        subscriptions = json.loads(content)
        for subscription in subscriptions:
            print "%6s %4s %s" % (
                subscription['volume']['identifier'],
                subscription['volume']['start_year'],
                subscription['volume']['name'],
            )

def load():
    handler.register(SubscriptionController)
