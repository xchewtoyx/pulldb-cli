import json

from cement.core import controller, handler

class SubscriptionController(controller.CementBaseController):
    class Meta:
        label = 'subscription'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['--raw'], {
                'help': 'display raw json output',
                'action': 'store_true',
            }),
            (['--context'], {
                'help': 'Request context information',
                'action': 'store_true',
            }),
        ]

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
        if self.app.pargs.context:
            path = path + '?context=1'
        resp, content = http_client.request(base_url + path)
        if self.app.pargs.raw:
            print content
        elif resp.status == 200:
            subscriptions = json.loads(content)
            for subscription in subscriptions['results']:
                print "%6s %4s %s" % (
                    subscription['subscription']['volume_id'],
                    subscription['subscription']['start_date'],
                    subscription.get('volume', {}).get('name'),
                )
        else:
            self.app.log.error('Unable to load content:\n%r\n\n%r' % (
                resp, content))

class AddSubscription(controller.CementBaseController):
    class Meta:
        label = 'subscription_add'
        stacked_on = 'subscription'
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
        path = '/api/subscriptions/add'
        data = json.dumps({
            'volumes': self.app.pargs.ids,
        })
        resp, content = http_client.request(
            base_url + path,
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=data,
        )
        if resp.status != 200:
            self.app.log.error('%r %r' % (resp, content))
        else:
            results = json.loads(content)
            failed = results['results'].get('failed', [])
            print '%d issues failed:\n%r' % (len(failed), failed)
            added = results['results'].get('added', [])
            print '%d issues added:\n%r' % (len(added), added)
            skipped = results['results'].get('skipped', [])
            print '%d issues skipped:\n%r' % (len(skipped), skipped)

class UpdateSubscription(controller.CementBaseController):
    class Meta:
        label = 'subscription_update'
        stacked_on = 'subscription'
        stacked_type = 'nested'
        aliases = ['update']
        aliases_only = True
        arguments = [
            (['id'], {
                'help': 'Comicvine identifier for volume',
                'action': 'store',
            }),
            (['date'], {
                'help': 'Subscription start date for volume',
                'action': 'store',
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/subscriptions/update'
        data = json.dumps({
            'updates': {
                self.app.pargs.id: self.app.pargs.date,
            },
        })
        resp, content = http_client.request(
            base_url + path,
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=data,
        )
        if resp.status != 200:
            self.app.log.error('%r %r' % (resp, content))
        else:
            results = json.loads(content)
            failed = results['results'].get('failed', [])
            print '%d issues failed:\n%r' % (len(failed), failed)
            added = results['results'].get('added', [])
            print '%d issues added:\n%r' % (len(added), added)
            updated = results['results'].get('updated', [])
            print '%d issues updated:\n%r' % (len(updated), updated)
            skipped = results['results'].get('skipped', [])
            print '%d issues skipped:\n%r' % (len(skipped), skipped)

def load():
    handler.register(SubscriptionController)
    handler.register(AddSubscription)
    handler.register(UpdateSubscription)
