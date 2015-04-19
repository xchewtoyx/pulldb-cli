from cement.core import handler, interface

class AuthInterface(interface.Interface):
    class IMeta:
        label = 'auth'

    def _setup(app):
        pass

def load(app=None):
    handler.define(AuthInterface)
