import json

from cement.core import controller, handler
from dateutil.parser import parse as parse_date

class StreamsController(controller.CementBaseController):
    class Meta:
        label = 'stream'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['--raw'], {'action': 'store_true'})
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
        path = '/api/streams/list'
        resp, content = http_client.request(base_url + path)
        if resp.status == 200:
            if self.app.pargs.raw:
                print content
            else:
                response = json.loads(content)
                for result in response['results']:
                    stream = result['stream']
                    print '%-20s %4s' % (stream['name'], stream['length'])
        else:
            print resp, content

    def print_stats(self, stream):
        print '{name:20s} {active:04d}/{total:04d} {backlog:d}'.format(**stream)

    @controller.expose(help='Display stream statistics')
    def stats(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        path = '/api/streams/stats'
        resp, content = http_client.request(base_url + path)
        if resp.status == 200:
            if self.app.pargs.raw:
                print content
            else:
                response = json.loads(content)
                for result in response['results']:
                    stream = result['stream']
                    self.print_stats(stream)
        else:
            print resp, content


class StreamInfo(controller.CementBaseController):
    class Meta:
        label = 'stream_info'
        stacked_on = 'stream'
        stacked_type = 'nested'
        aliases = ['info']
        aliases_only = True
        arguments = [
            (['--raw'], {
                'help': 'Print raw json response',
                'action': 'store_true',
            }),
            (['identifier'], {
                'help': 'Comicvine issue id',
                'action': 'store',
            }),
        ]

    def fetch_stream(self, path):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        resp, content = http_client.request(
            base_url + path,
        )
        if resp.status != 200:
            self.app.log.error('%r %r' % (resp, content))
        else:
            if self.app.pargs.raw:
                print content
            else:
                results = json.loads(content)
                print '%(status)d %(message)s' % results
                for result in results['results']:
                    print result

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose()
    def get(self):
        path = '/api/streams/%s/get' % self.app.pargs.identifier
        self.fetch_stream(path)

    @controller.expose(help='List unread pulls for stream')
    def list(self):
        path = '/api/streams/%s/list/unread' % self.app.pargs.identifier
        self.fetch_stream(path)

    @controller.expose()
    def refresh(self):
        path = '/api/streams/%s/refresh' % self.app.pargs.identifier
        self.fetch_stream(path)

class UpdateStreams(controller.CementBaseController):
    class Meta:
        label = 'stream_update'
        stacked_on = 'stream'
        stacked_type = 'nested'
        aliases = ['update']
        aliases_only = True
        arguments = [
            (['streams'], {
                'help': 'Stream names',
                'action': 'store',
                'nargs': '+',
            }),
            (['--publishers'], {
                'help': 'Publisher ids',
                'action': 'store',
                'default': '',
            }),
            (['--volumes'], {
                'help': 'Volume ids',
                'action': 'store',
                'default': '',
            }),
            (['--issues'], {
                'help': 'Issue ids',
                'action': 'store',
                'default': '',
            }),
        ]

    def post_update(self, path, update):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        data = json.dumps(update)
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
            print '%d updates failed:\n%r' % (len(failed), failed)
            success = results['results'].get('successful', [])
            print '%d updates successful:\n%r' % (len(success), success)
            skipped = results['results'].get('skipped', [])
            print '%d issues skipped:\n%r' % (len(skipped), skipped)

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose(help='Add new empty stream')
    def new(self):
        path = '/api/streams/add'
        list_key = 'issues'
        streams = [{'name': stream} for stream in self.app.pargs.streams]
        self.post_update(path, {
            'streams': streams,
        })

    @controller.expose(help='Add resources to a stream')
    def add(self):
        path = '/api/streams/update'
        update = {
            'name': self.app.pargs.streams[0],
        }
        if self.app.pargs.publishers:
            update['publishers'] = {
                'add': self.app.pargs.publishers.split(','),
            }
        if self.app.pargs.volumes:
            update['volumes'] = {
                'add': self.app.pargs.volumes.split(','),
            }
        if self.app.pargs.issues:
            update['issue'] = {
                'add': self.app.pargs.issues.split(','),
            }
        self.post_update(path, [update])

    @controller.expose()
    def remove(self):
        path = '/api/streams/update'
        update = {
            'name': self.app.pargs.streams[0]
        }
        if self.app.pargs.publishers:
            update['publishers'] = {
                'delete': self.app.pargs.publishers.split(','),
            }
        if self.app.pargs.volumes:
            update['volumes'] = {
                'delete': self.app.pargs.volumes.split(','),
            }
        if self.app.pargs.issues:
            update['issue'] = {
                'delete': self.app.pargs.issues.split(','),
            }
        self.post_update(path, [update])


class StreamTask(controller.CementBaseController):
    class Meta:
        label = 'stream_task'
        stacked_on = 'stream'
        stacked_type = 'nested'
        aliases = ['task']
        aliases_only = True

    def update_stream(self, path):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'batch_url')
        resp, content = http_client.request(
            base_url + path,
        )
        if resp.status != 200:
            self.app.log.error('%r %r' % (resp, content))
        else:
            try:
                results = json.loads(content)
            except ValueError as err:
                self.app.log.error(
                    'Error fetching resource %r: got %r\n' % (path, content))
                self.app.log.error(repr(err))
            else:
                print content

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose()
    def counts(self):
        path = '/batch/streams/updatecounts'
        self.update_stream(path)

    @controller.expose()
    def weights(self):
        path = '/batch/streams/updateweights'
        self.update_stream(path)


def load(app=None):
    handler.register(StreamsController)
    handler.register(StreamInfo)
    handler.register(UpdateStreams)
    handler.register(StreamTask)
