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
      get-app-info
      get-app-info-by-id
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

### get-app-info

`get-app-info` will lookup the app by name on Splunkbase and return available metadata as JSON string.

    Usage: sbclient get-app-info APP_NAME

### get-app-info-by-id

`get-app-info-by-id` will lookup the app by id on Splunkbase and return available metadata as JSON string.

    Usage: sbclient get-app-info-by-id APP_ID

> **Note**: This is very helpful to retrieve metadata (such as the name of an app) by just having the ID of an app. You can find the ID of each app by looking at the URL of the app on Splunkbase - it's just the last URL path. E.g. https://splunkbase.splunk.com/app/2890 is the URL for the machine learning toolkit on Splunkbase and 2890 is its ID.

### get-latest-version

`get-latest-version` will check Splunkbase and output information on the latest version of an app
available. Optionally, you can restrict the latest version to the latest version compatible with a
specific Splunk version.

    Usage: sbclient get-latest-version [OPTIONS] APP_NAME

    Options:
      --splunk-version TEXT  Restrict to app versions compatible with a given
                             Splunk version
      --help                 Show this message and exit.
