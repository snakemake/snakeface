#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from snakeface.logger import setup_logger
from snakeface.setup import init_snakeface
from django.core.wsgi import get_wsgi_application
from django.core import management
from snakeface.version import __version__
import argparse
import sys
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snakeface.settings")


def get_parser():
    parser = argparse.ArgumentParser(description="Snakeface: interface to snakemake.")

    parser.add_argument(
        "--version",
        dest="version",
        help="print the version and exit.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--noreload",
        dest="noreload",
        help="Tells Django to NOT use the auto-reloader.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--verbosity",
        dest="verbosity",
        type=int,
        help="Verbosity (0, 1, 2, 3).",
        choices=list(range(0, 4)),
        default=0,
    )

    parser.add_argument(
        "--workdir", dest="workdir", help="Specify the working directory.", nargs="?"
    )

    deploy_group = parser.add_argument_group("SETTINGS")
    deploy_group.add_argument(
        "--auth",
        dest="auth",
        help="Authentication type to create for the interface, defaults to token.",
        choices=["token"],
        default="token",
    )

    network_group = parser.add_argument_group("NETWORKING")
    network_group.add_argument(
        "--port", dest="port", help="Port to serve application on."
    )
    network_group.add_argument(
        "--host", dest="host", help="Domain name to serve application."
    )

    # Logging
    logging_group = parser.add_argument_group("LOGGING")

    logging_group.add_argument(
        "--quiet",
        dest="quiet",
        help="suppress logging.",
        default=False,
        action="store_true",
    )

    logging_group.add_argument(
        "--verbose",
        dest="verbose",
        help="verbose output for logging.",
        default=False,
        action="store_true",
    )

    logging_group.add_argument(
        "--log-disable-color",
        dest="disable_color",
        default=False,
        help="Disable color for snakeface logging.",
        action="store_true",
    )

    logging_group.add_argument(
        "--log-use-threads",
        dest="use_threads",
        action="store_true",
        help="Force threads rather than processes.",
    )

    description = "subparsers for Snakeface"
    subparsers = parser.add_subparsers(
        help="snakeface actions",
        title="actions",
        description=description,
        dest="command",
    )

    # print version and exit
    subparsers.add_parser("notebook", help="run a snakeface notebook")
    subparsers.add_parser("init", help="Create new settings in $HOME/.snakeface")

    return parser


def main():
    """main entrypoint for snakeface"""
    parser = get_parser()

    def help(return_code=0):
        """print help, including the software version and active client
        and exit with return code.
        """
        print("\nSnakemake Interface v%s" % __version__)
        parser.print_help()
        sys.exit(return_code)

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    # Show the version and exit
    if args.version:
        print(__version__)
        sys.exit(0)

    # Init snakeface settings in home if they don't exist
    settings = init_snakeface()

    # Currently we only support notebooks!
    settings.NOTEBOOK = True
    settings.save()

    # Default to port on command line, then settings, then 5000
    port = args.port or settings.DOMAIN_PORT or 5000
    host = args.host or settings.DOMAIN_NAME or "127.0.0.1"
    host = "%s:%s" % (host, port)

    # If we just needed to do that, exit
    if args.command == "init":
        sys.exit("Init complete. Settings are at %s" % settings.settings_file)

    # If a working directory is set
    if not args.workdir or args.workdir == ".":
        args.workdir = os.getcwd()
    if args.workdir:
        os.environ["SNAKEFACE_WORKDIR"] = args.workdir
        os.putenv("SNAKEFACE_WORKDIR", args.workdir)

    application = get_wsgi_application()

    # customize django logging
    setup_logger(
        quiet=args.quiet,
        nocolor=args.disable_color,
        debug=args.verbose,
        use_threads=args.use_threads,
    )

    # Migrations
    management.call_command("makemigrations", verbosity=args.verbosity)
    for app in ["users", "main", "base"]:
        management.call_command("makemigrations", app, verbosity=args.verbosity)
    management.call_command("migrate", verbosity=args.verbosity)

    # management.call_command("qcluster", verbosity=args.verbosity)
    management.call_command(
        "collectstatic", verbosity=args.verbosity, interactive=False
    )
    management.call_command(
        "runserver", host, verbosity=args.verbosity, noreload=not args.noreload
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
