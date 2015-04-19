import argparse
import json
import os

from cement.core import handler, hook
import httplib2
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import xdg.BaseDirectory

from pulldb.interfaces import AuthInterface

class OauthHandler(handler.CementBaseHandler):
    class Meta:
        interface = AuthInterface
        label = 'oauth2'
        scope = 'https://www.googleapis.com/auth/userinfo.email'

    @property
    def client_secrets(self):
        secrets_path = os.path.join(
            xdg.BaseDirectory.save_data_path(self.app._meta.label),
            'client_secrets.json')
        with open(secrets_path) as secrets_file:
            client_secret_data = json.load(secrets_file)
        return client_secret_data.get('installed')

    @property
    def credential_store(self):
        storage_path = os.path.join(
            xdg.BaseDirectory.save_data_path(self.app._meta.label),
            'oauth_credentials')
        return Storage(storage_path)

    def client(self):
        http_client = httplib2.Http()
        credentials = self.credential_store.get()
        if not credentials or credentials.invalid:
            self.app.log.debug('No valid credentials, authorizing...')
            flow = client.OAuth2WebServerFlow(
                client_id=self.client_secrets['client_id'],
                client_secret=self.client_secrets['client_secret'],
                scope=self.Meta.scope,
                user_agent="pulldb/0.1",
                redirect_url="urn:ietf:wg:oauth:2.0:oob",
            )
            tools.run_flow(flow, self.credential_store, self.app.pargs)
        # The older gdata api needs the oauth token to be converted
        self.credential_store.get().authorize(http_client)
        return http_client

def load_google_args(app):
    if not isinstance(app.args, argparse.ArgumentParser):
        raise TypeError('Cannot add arguments no non argparse parser %r' % (
            app.args))
    app.args._add_container_actions(tools.argparser)
    app.args.set_defaults(noauth_local_webserver=True)

def load(app=None):
    handler.register(OauthHandler)
    hook.register('pre_argument_parsing', load_google_args)
