# sbclient - CLI Splunkbase client

sbclient is a command-line client for interacting with the officially unofficial Splunkbase API.

## Installation

sbclient can be installed using pip3:

    pip3 install sbclient

Or, if you're feeling adventurous, can be installed directly from
github:

   pip3 install git+https://github.com/HurricaneLabs/sbclient.git


## Usage

    Usage: sbclient [OPTIONS] COMMAND [ARGS]...

    Options:
      -U, --username TEXT  [required]
      -P, --password TEXT
      --help               Show this message and exit.

    Commands:
      check-app-for-update
      download-app
      get-latest-version

sbclient is broken into several smaller commands. Credentials for Splunkbase can be passed as
parameters, or can be set as environment variables

    export SPLUNKBASE_USERNAME="doug.merritt"
    export SPLUNKBASE_PASSWORD="spLunk1sc00l"

### check-app-for-update

`check-app-for-update` will parse an app directory for details, and check for updates on
Splunkbase for that app. It will also output the current version of the app, and details of the
update if one is available.

    Usage: sbclient check-app-for-update [OPTIONS] APP_DIR

    Options:
      --splunk-version TEXT  Restrict to app versions compatible with a given
                             Splunk version
      --help                 Show this message and exit.

### download-app

`download-app` will download an app from Splunkbase, either a specific version or the latest
available.

    Usage: sbclient download-app [OPTIONS] APP_NAME

    Options:
      --output-path TEXT  Path and filename location to save the app
      --version TEXT      Version of app to download, default is latest
      --help              Show this message and exit.


### get-latest-version

`get-latest-version` will check Splunkbase and output information on the latest version of an app
available. Optionally, you can restrict the latest version to the latest version compatible with a
specific Splunk version.

    Usage: sbclient get-latest-version [OPTIONS] APP_NAME

    Options:
      --splunk-version TEXT  Restrict to app versions compatible with a given
                             Splunk version
      --help                 Show this message and exit.
