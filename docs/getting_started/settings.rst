.. _getting_started-settings:


========
Settings
========

Settings are defined in the settings.yml file, and are automatically populated 
into Snakeface. If you want a notebook, you will likely be good using the defaults.


.. list-table:: Title
   :widths: 25 65 10
   :header-rows: 1

   * - Name
     - Description
     - Default
   * - GOOGLE_ANALYTICS_SITE
     - The url of your website for Google Analytics, if desired
     - None
   * - GOOGLE_ANALYTICS_ID
     - The identifier for Google Analytics, if desired
     - None
   * - TWITTER_USERNAME
     - A Twitter username to link to in the footer.
     - johanneskoester
   * - GITHUB_REPOSITORY
     - A GitHub repository to link to in the footer
     - https://github.com/snakemake/snakeface
   * - GITHUB_DOCUMENTATION
     - GitHub documentation (or other) to link to in the footer
     - https://snakemake.github.io/snakeface
   * - USER_WORKFLOW_LIMIT
     - The maximum number of workflows to allow a user to create
     - 50
   * - USER_WORKFLOW_RUNS_LIMIT
     - The maximum number of running workflows to allow
     - 50
   * - USER_WORKFLOW_GLOBAL_RUNS_LIMIT
     - Giving a shared Snakeface interface, the total maximum allowed running at once.
     - 1000
   * - NOTEBOOK_ONLY
     - Only allow notebooks (disables all other auth)
     - None
   * - MAXIMUM_NOTEBOOK_JOBS
     - Given a notebook, the maximum number of jobs to allow running at once
     - 2
   * - WORKFLOW_UPDATE_SECONDS
     - How often to refresh the status table on a workflow details page
     - 10
   * - EXECUTOR_CLUSTER
     - Set this to non null to enable the cluster executor
     - None
   * - EXECUTOR_GOOGLE_LIFE_SCIENCES
     - Set this to non null to enable the GLS executor
     - None
   * - EXECUTOR_KUBERNETES
     - Set this to non null to enable the K8 executor
     - None
   * - EXECUTOR_GA4GH_TES
     - Set this to non null to enable this executor
     - None
   * - EXECUTOR_TIBANNA
     - Set this to non null to enable the tibanna executor
     - None
   * - DISABLE_SINGULARITY
     - Disable Singularity argument groups by setting this to non null
     - None
   * - DISABLE_CONDA
     - Disable Conda argument groups by setting this to non null
     - None
   * - DISABLE_NOTEBOOKS
     - Disable notebook argument groups by setting this to non null
     - true
   * - ENVIRONMENT
     - The global name for the deployment environment
     - test
   * - HELP_CONTACT_URL
     - The help contact email or url used for the API
     - https://github.com/snakemake/snakeface/issues
   * - SENDGRID_API_KEY
     - Not in use yet, will allow sending email notifications
     - None
   * - SENDGRID_SENDER_EMAIL
     - Not in use yet, will allow sending email notifications
     - None
   * - DOMAIN_NAME
     - The server domain name, defaults to a localhost address
     - http://127.0.0.1
   * - DOMAIN_PORT
     - The server port, can be overridden from the command line
     - 5000
   * - REQUIRE_AUTH
     - Should authentication be required?
     - true
   * - PROFILE
     - Set a default profile (see https://github.com/snakemake-profiles)
     - None
   * - PROFILE
     - Set a default profile (see https://github.com/snakemake-profiles)
     - None
   * - PRIVATE_ONLY
     - Make all workflows private (not relevant for notebooks)
     - None
   * - ENABLE_CACHE
     - Enable view caching
     - false
   * - WORKDIR
     - Default working directory (overridden by client and environment)
     - None
   * - PLUGINS_LDAP_AUTH_ENABLED
     - Set to non null to enable
     - None
   * - PLUGINS_PAM_AUTH_ENABLED
     - Set to non null to enable
     - None
   * - PLUGINS_SAML_AUTH_ENABLED
     - Set to non null to enable
     - None
