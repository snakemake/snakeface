__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020, Vanessa Sochat"
__license__ = "MPL 2.0"

import uuid


def get_notebook_token(request, verbose=True):
    """If a notebook token isn't defined, generate it (and print to the console)"""
    token = request.session.get("notebook_token")
    if not token:
        token = str(uuid.uuid4())
        request.session["notebook_token"] = token
        request.session.modified = True
    if verbose:
        print("Enter token: %s" % token)
    return token
