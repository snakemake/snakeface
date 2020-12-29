__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from wsgiref.util import FileWrapper
from django.http import StreamingHttpResponse
from snakeface.settings import cfg
import subprocess
import threading
import ctypes

import tempfile
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


def write_file(filename, content):
    """Write some text content to a file"""
    with open(filename, "w") as fd:
        fd.write(content)
    return filename


def get_tmpfile(prefix="", suffix=""):
    """get a temporary file with an optional prefix. By default, the file
    is closed (and just a name returned).

    Arguments:
     - prefix (str) : prefix with this string
    """
    tmpdir = tempfile.gettempdir()
    prefix = os.path.join(tmpdir, os.path.basename(prefix))
    fd, tmp_file = tempfile.mkstemp(prefix=prefix, suffix=suffix)
    os.close(fd)
    return tmp_file


class ThreadRunner(threading.Thread):
    """We need to be able to run a Snakemake job as a thread, and kill it if
    an exception is raised based on it's id
    """

    def set_workflow(self, workflow):
        self.workflow = workflow

    #    def run(self):
    #
    # target function of the thread class
    ##        try:
    #            while True:
    #                print('running ' + self.name)
    #        finally:
    #            print('ended')

    @property
    def thread_id(self):
        """Return the id of the thread, either attributed to the class or
        by matching the Thread instance
        """
        if hasattr(self, "_thread_id"):
            return self._thread_id
        for thread_id, thread in threading._active.items():
            if thread is self:
                return thread_id

    def stop_workflow(self):
        """Stop the workflow from running given the thread id"""
        thread_id = self.thread_id
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            thread_id, ctypes.py_object(SystemExit)
        )
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print("Failed to stop thread %s" % thread_id)
        self.workflow.status = "NOTRUNNING"
        self.workflow.save()


class CommandRunner(object):
    """Wrapper to use subprocess to run a command. This is based off of pypi
    vendor distlib SubprocesMixin.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.error = []
        self.output = []

    def reader(self, stream, context):
        """Get output and error lines and save to command runner."""
        # Make sure we save to the correct field
        lines = self.error
        if context == "stdout":
            lines = self.output

        while True:
            s = stream.readline()
            if not s:
                break
            lines.append(s.decode("utf-8"))
        stream.close()

    def run_command(self, cmd, env=None, **kwargs):
        self.reset()

        # If we need to update the environment
        # **IMPORTANT: this will include envars from host. Absolutely cannot
        # be any secrets (they should be defined in the app settings file)
        envars = os.environ.copy()
        if env:
            envars.update(env)

        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=envars, **kwargs
        )

        # Create threads for error and output
        t1 = threading.Thread(target=self.reader, args=(p.stdout, "stdout"))
        t1.start()
        t2 = threading.Thread(target=self.reader, args=(p.stderr, "stderr"))
        t2.start()
        p.wait()
        t1.join()
        t2.join()
        return self.output
