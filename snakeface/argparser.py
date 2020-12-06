__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020, Vanessa SOchat"
__license__ = "MPL 2.0"

from snakemake import get_argument_parser
from snakemake.settings import cfg

import os
import sys


class SnakefaceParser:
    """A Snakeface Parser is a wrapper to an argparse.Parser, and aims
    to make it easy to loop over arguments and options, and generate various
    representations (e.g., an input field) for the interface. The point is
    not to use it to parse arguments and validate, but to output all
    fields to a front end form.
    """

    def __init__(self):
        """load the parser, optionally specifying a profile"""
        self.parser = get_argument_parser()
        if cfg.PROFILE and os.path.exists(cfg.PROFILE):
            print("Loading profile %s" % cfg.PROFILE)
            self.parser = get_argument_parser(cfg.PROFILE)

    @property
    def groups(self):
        """yield a minimal (dict) version of each group"""
        pass

    # TODO: we will want to get input from interface, and be able to map
    # it back into the parser to get the arguments and then hand off to snakemake
    # STOPPED HERE - need to write this class
