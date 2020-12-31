__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from snakemake import get_argument_parser
from snakeface.settings import cfg
from snakeface import settings
from snakeface.apps.main.utils import get_snakefile_choices
from jinja2 import Template
import logging
import os
import json

logger = logging.getLogger("argparser")

# Prepare path to templates
here = os.path.abspath(os.path.dirname(__file__))
templates = os.path.join(here, "apps", "main", "templates", "forms")


class SnakefaceParser:
    """A Snakeface Parser is a wrapper to an argparse.Parser, and aims
    to make it easy to loop over arguments and options, and generate various
    representations (e.g., an input field) for the interface. The point is
    not to use it to parse arguments and validate, but to output all
    fields to a front end form.
    """

    # Update the listing of snakefiles on the parser init
    snakefiles = get_snakefile_choices()

    def __init__(self):
        """load the parser, optionally specifying a profile"""
        self.parser = get_argument_parser()
        self._groups = {}
        self._args = {}
        self.groups
        self._errors = []

        # A profile can further customize job submission
        if cfg.PROFILE and os.path.exists(cfg.PROFILE):
            print("Loading profile %s" % cfg.PROFILE)
            self.parser = get_argument_parser(cfg.PROFILE)

    def __str__(self):
        return "[snakeface-parser]"

    def __repr__(self):
        return self.__str__()

    @property
    def errors(self):
        return " ".join(self._errors)

    def get(self, name, default=None):
        """A general get function to return an argument that might be nested under
        a group. These objects are the same as linked in _groups.
        """
        return self._args.get(name, default)

    def load(self, argdict):
        """Load is a wrapper around set - we loop through a dictionary and set all
        arguments.
        """
        if isinstance(argdict, str):
            argdict = json.loads(argdict)
        for key, value in argdict.items():
            arg = self._args.get(key)
            if arg:
                arg.value = value

    def set(self, name, value):
        """Set a value for an argument. This is typically what the user has selected."""
        arg = self._args.get(name)
        if arg:
            arg.value = value

    def to_dict(self):
        """the opposite of load, this function exports an argument"""
        return {name: arg.value for name, arg in self._args.items()}

    @property
    def snakefile(self):
        snakefile = self._args.get("snakefile")
        if snakefile:
            return snakefile.value

    def validate(self):
        """ensure that all required args are defined"""
        valid = True
        for key in self.required:
            if not self._args.get(key):
                self._errors.append("The %s is required." % key)
                valid = False
        return valid

    @property
    def required(self):
        return ["cores", "snakefile"]

    @property
    def command(self):
        """Given a loaded set of arguments, generate the command."""
        command = "snakemake"

        for name, arg in self._args.items():
            if arg.value:

                # If the value is set to the default, ignore it
                if arg.value == arg.action["default"] and name not in self.required:
                    continue

                flag = ""
                if arg.action["option_strings"]:
                    flag = arg.action["option_strings"][0]

                # Assemble argument based on type
                if arg.is_boolean:
                    command += " %s" % flag
                else:
                    command += " %s %s" % (flag, arg.value)

        return command

    @property
    def groups(self):
        """yield arguments organized by groups, with the intention to easily map
        into a form on the front end. The groups seem to have ALL arguments each,
        so we have to artificially separate them.
        """
        if self._groups:
            return self._groups

        # Generate an argument lookup based on dest
        lookup = {}
        for action in self.parser._actions:
            lookup[action.dest] = SnakefaceArgument(
                action, action.dest in self.required
            )

            # Define choices
            if action.dest == "snakefile":
                lookup[action.dest].update_choice_fields({"snakefile": self.snakefiles})

            # Set the wms monitor to be this server
            if action.dest == "wms_monitor":
                lookup[action.dest].value = settings.DOMAIN_NAME

        # This top level organizes into groups
        for group in self.parser._action_groups:
            group_dict = {
                a.dest: lookup.get(a.dest)
                for a in group._group_actions
                if self.include_argument(a.dest, group.title)
            }

            # Store a flattened representation to manipulate later
            self._args.update(group_dict)

            # Don't add empty groups
            if group_dict:
                self._groups[group.title] = group_dict
        return self._groups

    def include_argument(self, name, group):
        """Given an argument name, and a group name, skip if settings disable
        it
        """
        # Never include these named arguments
        if name in ["help", "version"]:
            return False

        # Skip groups based on specific configuration settings
        if not cfg.EXECUTOR_CLUSTER and group == "CLUSTER":
            return False
        if not cfg.EXECUTOR_GOOGLE_LIFE_SCIENCES and group == "GOOGLE_LIFE_SCIENCE":
            return False
        if not cfg.EXECUTOR_KUBERNETES and group == "KUBERNETES":
            return False
        if not cfg.EXECUTOR_TIBANNA and group == "TIBANNA":
            return False
        if not cfg.EXECUTOR_TIBANNA and group == "TIBANNA":
            return False
        if not cfg.EXECUTOR_GA4GH_TES and group == "TES":
            return False
        if cfg.DISABLE_SINGULARITY and group == "SINGULARITY":
            return False
        if cfg.DISABLE_CONDA and group == "CONDA":
            return False
        if cfg.DISABLE_NOTEBOOKS and group == "NOTEBOOKS":
            return False
        return True


class SnakefaceArgument:
    """A Snakeface argument takes an action from a parser, and is able to
    easily generate front end views (e.g., a form element) for it
    """

    def __init__(self, action, required=False):
        self.action = action.__dict__
        self.boolean_template = ""
        self.text_template = ""
        self.choice_template = ""
        self.choice_fields = {}
        self.value = ""
        self.required = required

    def __str__(self):
        return self.action["dest"]

    def __repr__(self):
        return self.__str__()

    def update_choice_fields(self, updates):
        self.choice_fields.update(updates)

    @property
    def field_name(self):
        return " ".join([x.capitalize() for x in self.action["dest"].split("_")])

    @property
    def is_boolean(self):
        return self.action["nargs"] == 0 and self.action["const"]

    def field(self):
        """generate a form field for the argument"""
        if self.action["dest"] in self.choice_fields:
            return self.choice_field()
        if self.is_boolean:
            return self.boolean_field()
        return self.text_field()

    def load_template(self, path):
        """Given a path to a template file, load the template with jinja2"""
        if os.path.exists(path):
            with open(path, "r") as fd:
                template = Template(fd.read())
            return template
        logging.warning("%s does not exist, no template loaded.")
        return ""

    def boolean_field(self):
        """generate a boolean field (radio button) via a jinja2 template"""
        # Ensure that we only load/read the file once
        if not self.boolean_template:
            self.boolean_template = self.load_template(
                os.path.join(templates, "boolean_field.html")
            )
        checked = "checked" if self.action["default"] == True else ""
        return self.boolean_template.render(
            label=self.field_name,
            help=self.action["help"],
            name=self.action["dest"],
            checked=checked,
            required="required" if self.required else "",
        )

    def text_field(self):
        """generate a text field for using a pre-loaded jinja2 template"""
        if not self.text_template:
            self.text_template = self.load_template(
                os.path.join(templates, "text_field.html")
            )

        return self.text_template.render(
            name=self.action["dest"],
            default=self.action["default"] or self.value,
            label=self.field_name,
            help=self.action["help"],
            required="required" if self.required else "",
        )

    def choice_field(self):
        """generate a choice field for using a pre-loaded jinja2 template"""
        if not self.choice_template:
            self.choice_template = self.load_template(
                os.path.join(templates, "choice_field.html")
            )

        return self.choice_template.render(
            name=self.action["dest"],
            label=self.field_name,
            help=self.action["help"],
            required="required" if self.required else "",
            choices=self.choice_fields.get(self.action["dest"]),
        )
