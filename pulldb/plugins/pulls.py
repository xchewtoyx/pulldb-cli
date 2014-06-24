from datetime import datetime
import json
from operator import itemgetter

from cement.core import controller, handler
from dateutil.parser import parse as parse_date

class PullsController(controller.CementBaseController):
    class Meta:
        label = 'pull'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['--raw'], {
                'help': 'display raw json output',
                'action': 'store_true',
            }),
            (['--nocontext'], {
                'help': 'do not request context information',
                'action': 'store_true',
            }),
            (['--weighted'], {
                'help': ('sort pulls by weight rather than pubdate where '
                         'appropriate'),
                'action': 'store_true',
            }),
        ]

    def _weight_key(self, pull):
        return pull.get('weight')

    def _date_key(self, pull):
        return pull.get('pubdate')

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose(help='List all pulls')
    def list(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        if self.app.pargs.nocontext:
            path = '/api/pulls/list/all'
        else:
            path = '/api/pulls/list/all?context=1'

        resp, content = http_client.request(base_url + path)
        if resp.status == 200:
            if self.app.pargs.raw:
                print content
            else:
                pull_list = json.loads(content)
                for pull in pull_list['results']:
                    print "%6s %4s %s %s %r" % (
                        pull['pull'].get('issue_id'),
                        pull['pull'].get('pubdate'),
                        pull['volume'].get('name'),
                        pull['issue'].get('issue_number'),
                        pull['pull'].get('read'),
                    )
        else:
            print resp, content

    @controller.expose()
    def new(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        if self.app.pargs.nocontext:
            path = '/api/pulls/list/new'
        else:
            path = '/api/pulls/list/new'
        resp, content = http_client.request(base_url + path)
        if resp.status == 200:
            if self.app.pargs.raw:
                print content
            else:
                pull_list = json.loads(content)
                for pull in pull_list['results']:
                    if not pull:
                        self.app.log.error("Null result")
                        continue
                    if pull.get('pull', {}).get('pubdate'):
                        pubdate = parse_date(pull['pull']['pubdate'])
                    else:
                        pubdate = datetime.min
                    print '%7s %10s %s' % (
                        pull['pull']['identifier'],
                        pubdate.strftime('%Y-%m-%d'),
                        pull['pull'].get('name'),
                    )
        else:
            self.app.log.error(resp, content)

    @controller.expose()
    def unread(self):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        params = []
        if not self.app.pargs.nocontext and False:
            params.append('context=1')
        if not self.app.pargs.weighted:
            params.append('weighted=1')
        path = '/api/pulls/list/unread?%s' % '&'.join(params)
        resp, content = http_client.request(base_url + path)
        if resp.status == 200:
            if self.app.pargs.raw:
                print content
            else:
                pull_list = json.loads(content)
                if self.app.pargs.weighted:
                    sortkey=self._weight_key
                else:
                    sortkey=self._date_key
                sorted_pulls = sorted(pull_list['results'], key=sortkey)
                for pull in sorted_pulls:
                    pull = pull
                    if not pull:
                        print 'null'
                        continue
                    print "%05.f %s +%s<%s> {%s} [%s]" % (
                        float(pull['pull'].get('weight', 0.0))*10000,
                        pull['pull'].get('name'),
                        pull['pull'].get('stream_id', ''),
                        pull['pull'].get('shard', ''),
                        pull['pull'].get('volume_id', ''),
                        pull['pull'].get('issue_id'),
                    )
        else:
            self.app.log.error(resp, content)

class PullInfo(controller.CementBaseController):
    class Meta:
        label = 'pull_info'
        stacked_on = 'pull'
        stacked_type = 'nested'
        aliases = ['info']
        aliases_only = True
        arguments = [
            (['identifier'], {
                'help': 'Comicvine issue id',
                'action': 'store',
            }),
        ]

    def fetch_pull(self, path):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        resp, content = http_client.request(
            base_url + path,
        )
        if resp.status != 200:
            self.app.log.error('%r %r' % (resp, content))
            print content
        else:
            print content
            results = json.loads(content)
            print '%(status)d %(message)s' % results

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose()
    def get(self):
        path = '/api/pulls/%s/get' % self.app.pargs.identifier
        self.fetch_pull(path)

    @controller.expose()
    def refresh(self):
        path = '/api/pulls/%s/refresh' % self.app.pargs.identifier
        self.fetch_pull(path)


class UpdatePulls(controller.CementBaseController):
    class Meta:
        label = 'pull_update'
        stacked_on = 'pull'
        stacked_type = 'nested'
        aliases = ['update']
        aliases_only = True
        arguments = [
            (['issues'], {
                'help': 'Comicvine issue ids',
                'action': 'store',
                'nargs': '+',
            }),
        ]

    def post_list(self, path, list_key):
        auth_handler = handler.get('auth', 'oauth2')()
        auth_handler._setup(self.app)
        http_client = auth_handler.client()
        base_url = self.app.config.get('base', 'base_url')
        data = json.dumps({
            list_key: self.app.pargs.issues,
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

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose()
    def add(self):
        path = '/api/pulls/add'
        list_key = 'issues'
        self.post_list(path, list_key)

    @controller.expose()
    def pull(self):
        path = '/api/pulls/update'
        list_key = 'pull'
        self.post_list(path, list_key)

    @controller.expose()
    def read(self):
        path = '/api/pulls/update'
        list_key = 'read'
        self.post_list(path, list_key)

    @controller.expose()
    def unread(self):
        path = '/api/pulls/update'
        list_key = 'unread'
        self.post_list(path, list_key)

def load():
    handler.register(PullsController)
    handler.register(PullInfo)
    handler.register(UpdatePulls)
