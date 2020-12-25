__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from wsgiref.util import FileWrapper
from django.http import StreamingHttpResponse
from snakeface.settings import cfg

import os
import re


def get_workdir_choices(path=None):
    """Given the working directory set on init, return potential subdirectories."""
    path = path or cfg.WORKDIR
    choices = [(path, "/")]

    # Recursive to working directory is default
    for root, dirs, files in sorted(os.walk(path)):
        for f in sorted(dirs):
            if f == "__pycache__":
                continue
            fullpath = os.path.join(root, f)
            # Ignore all hidden files and paths
            if "/." in f or "/." in fullpath or "/." in root:
                continue
            choices.append((fullpath, fullpath))
    return choices


def get_snakefile_choices(path=None):
    """Given the working directory set on init, return all discovered snakefiles."""
    path = path or cfg.WORKDIR
    choices = []

    # Recursive to working directory is default
    for root, dirs, files in sorted(os.walk(path)):
        for f in sorted(files):
            fullpath = os.path.join(root, f)
            if re.search("Snakefile", f):
                choices.append((fullpath, fullpath))
    return choices


def send_file(exported_file, chunk_size=8192):
    """Send file is shared by similarity and dataset downloads, and streams a chunked response to
    the server, the expected octet stream
    """
    response = StreamingHttpResponse(
        FileWrapper(open(exported_file, "rb"), chunk_size),
        content_type="application/octet-stream",
    )
    response["Content-Length"] = os.path.getsize(exported_file)
    response["Content-Disposition"] = "attachment; filename=%s" % os.path.basename(
        exported_file
    )
    return response
