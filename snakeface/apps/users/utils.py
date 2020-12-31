__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020, Vanessa Sochat"
__license__ = "MPL 2.0"

import uuid
import os


def get_notebook_token(request, verbose=True):
    """If a notebook token isn't defined, generate it (and print to the console)
    The token is used to generate a user to log the user in.
    """
    # If the user has already logged in, return current token
    token = request.session.get("notebook_token")

    # The user session has ended, but has authenticated before
    user = get_notebook_user()
    if request.user.is_authenticated:
        token = request.user.notebook_token

    # Second attempt, see if user has logged in before and retrieve token
    elif user:
        token = user.notebook_token

    if not token:
        token = str(uuid.uuid4())
        user = get_or_create_notebook_user(token)
        request.session["notebook_token"] = token
        request.session.modified = True
    if verbose:
        print("Enter token: %s" % token)
    return token


def get_username():
    """get the username based on the effective uid. This is for a notebook
    execution, and doesn't add any additional security, but rather is used for
    personalization and being able to create an associated django user.
    """
    try:
        import pwd

        return pwd.getpwuid(os.getuid())[0]
    except:
        return "snakeface-user"


def get_notebook_user():
    """Get the notebook user, if they have logged in before."""
    from snakeface.apps.users.models import User
    from snakeface.settings import cfg

    try:
        return User.objects.get(username=cfg.USERNAME)
    except:
        return None


def get_or_create_notebook_user(token):
    """Get or create the notebook user. Imports are done in the function because
    Django startup (settings.py) uses these functions.
    """
    from snakeface.apps.users.models import User
    from snakeface.settings import cfg

    try:
        user = User.objects.get(username=cfg.USERNAME)
    except:
        user = User.objects.create_user(cfg.USERNAME, None, token)
        user.notebook_token = token
        user.save()
    return user
