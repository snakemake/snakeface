__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

__version__ = "0.0.11"
AUTHOR = "Vanessa Sochat"
AUTHOR_EMAIL = "vsochat@stanford.edu"
NAME = "snakeface"
PACKAGE_URL = "https://github.com/snakemake/snakeface"
KEYWORDS = "snakemake,workflow management,pipeline,interface, workflows"
DESCRIPTION = "Snakemake Interface"
LICENSE = "LICENSE"

################################################################################
# Global requirements


INSTALL_REQUIRES = (
    ("snakedeploy", {"min_version": None}),
    ("snakemake", {"min_version": None}),
    ("pyaml", {"min_version": "20.4.0"}),
    ("Jinja2", {"min_version": "2.11.2"}),
    ("Django", {"exact_version": "3.0.8"}),
    ("django-q", {"min_version": "1.3.4"}),
    ("django-crispy-forms", {"min_version": "1.10.0"}),
    ("django-taggit", {"min_version": "1.3.0"}),
    ("django-gravatar", {"min_version": None}),
    ("django-ratelimit", {"min_version": "3.0.0"}),
    ("django-extensions", {"min_version": "3.0.2"}),
    ("djangorestframework", {"exact_version": "3.11.1"}),
    ("drf-yasg", {"exact_version": "1.20.0"}),
    ("channels", {"exact_version": "3.0.3"}),
)

# Dependencies provided by snakemake: pyYaml, jinja2

EMAIL_REQUIRES = (("sendgrid", {"min_version": "6.4.3"}),)
POSTGRES_REQUIRES = (("psycopg2-binary", {"min_version": "2.8.5"}),)

TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)

ALL_REQUIRES = INSTALL_REQUIRES + EMAIL_REQUIRES + POSTGRES_REQUIRES
