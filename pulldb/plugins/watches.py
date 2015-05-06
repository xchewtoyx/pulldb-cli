import json

from cement.core import controller, handler

class WatchController(controller.CementBaseController):
    class Meta:
        label = 'watch'
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
        path = '/api/watches/list'
        if self.app.pargs.context:
            path = path + '?context=1'
        resp, content = http_client.request(base_url + path)
        if self.app.pargs.raw:
            print content
        elif resp.status == 200:
            watches = json.loads(content)
            for watch in watches['results']:
                print "%8s%6s %4s %s" % (
                    watch['watch']['collection_kind'],
                    watch['watch']['collection_id'],
                    watch['watch']['start_date'],
                    watch.get('collection', {}).get('name'),
                )
        else:
            self.app.log.error('Unable to load content:\n%r\n\n%r' % (
                resp, content))

class AddWatch(controller.CementBaseController):
    class Meta:
        label = 'watch_add'
        stacked_on = 'watch'
        stacked_type = 'nested'
        aliases = ['add']
        aliases_only = True
        arguments = [
            (['--raw'], {
                'help': 'display raw json output',
                'action': 'store_true',
            }),
            (['--volumes'], {
                'help': 'Comicvine identifier for volume',
                'action': 'store',
            }),
            (['--arcs'], {
                'help': 'Comicvine identifier for story_arc',
                'action': 'store',
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/watches/add'
        data = {}
        if self.app.pargs.arcs:
            data['arcs'] = self.app.pargs.arcs.split(',')
        if self.app.pargs.volumes:
            data['volumes'] = self.app.pargs.volumes.split(',')
        resp, content = http_client.request(
            base_url + path,
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps(data),
        )
        if resp.status != 200:
            self.app.log.error('%r %r' % (resp, content))
        elif self.app.pargs.raw:
            print content
        else:
            results = json.loads(content)
            failed = results['results'].get('failed', [])
            print '%d issues failed:\n%r' % (len(failed), failed)
            added = results['results'].get('added', [])
            print '%d issues added:\n%r' % (len(added), added)
            skipped = results['results'].get('skipped', [])
            print '%d issues skipped:\n%r' % (len(skipped), skipped)

class RemoveWatch(controller.CementBaseController):
    class Meta:
        label = 'watch_remove'
        stacked_on = 'watch'
        stacked_type = 'nested'
        aliases = ['remove']
        aliases_only = True
        arguments = [
            (['--volumes'], {
                'help': 'Comicvine identifier for volume',
                'action': 'store',
            }),
            (['--arcs'], {
                'help': 'Comicvine identifier for story_arc',
                'action': 'store',
            }),
            (['--raw'], {
                'help': 'display raw json output',
                'action': 'store_true',
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/watches/remove'
        data = {}
        if self.app.pargs.arcs:
            data['arcs'] = self.app.pargs.arcs.split(',')
        if self.app.pargs.volumes:
            data['volumes'] = self.app.pargs.volumes.split(',')
        resp, content = http_client.request(
            base_url + path,
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps(data),
        )
        if resp.status != 200:
            self.app.log.error('%r %r' % (resp, content))
        elif self.app.pargs.raw:
            print content
        else:
            results = json.loads(content)
            removed = results['results']
            print '%d issues removed:\n%r' % (len(removed), removed)

class CheckShard(controller.CementBaseController):
    class Meta:
        label = 'watch_check_shard'
        stacked_on = 'watch'
        stacked_type = 'nested'
        aliases = ['check']
        aliases_only = True
        arguments = [
            (['--shard', '-s'], {
                'help': 'Shard to check for updates',
                'action': 'store',
                'default': -1,
                'type': int,
            }),
            (['--raw'], {
                'help': 'Display raw json response',
                'action': 'store_true',
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'batch_url')
        path = '/batch/watches/update?shard=%d' % (
            self.app.pargs.shard,
        )
        resp, content = http_client.request(
            base_url + path,
        )
        if self.app.pargs.raw:
            print content
        elif resp.status != 200:
            self.app.log.error('%r %r' % (resp, content))
        else:
            print base_url+path
            results = json.loads(content)
            print 'Found %d updates' % results['updated']

class UpdateWatch(controller.CementBaseController):
    class Meta:
        label = 'watch_update'
        stacked_on = 'watch'
        stacked_type = 'nested'
        aliases = ['update']
        aliases_only = True
        arguments = [
            (['--raw'], {
                'help': 'Display raw json output',
                'action': 'store_true',
            }),
            (['type'], {
                'help': 'Collection type',
                'choices': ['arcs', 'volumes'],
            }),
            (['id'], {
                'help': 'Comicvine identifier for volume',
                'action': 'store',
            }),
            (['date'], {
                'help': 'Watch start date.',
                'action': 'store',
            }),
        ]

    @controller.expose(hide=True)
    def default(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/watches/update'
        data = json.dumps({
            self.app.pargs.type: {
                self.app.pargs.id: self.app.pargs.date,
            },
        })
        resp, content = http_client.request(
            base_url + path,
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=data,
        )
        if self.app.pargs.raw:
            print content
        elif resp.status != 200:
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

def load(app=None):
    handler.register(WatchController)
    handler.register(AddWatch)
    handler.register(RemoveWatch)
    handler.register(CheckShard)
    handler.register(UpdateWatch)
