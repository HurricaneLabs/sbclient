import getpass
import hashlib
import os
import sys
from configparser import RawConfigParser
from io import BytesIO

import click
import requests
from dateutil.parser import parse as dateparse
from defusedxml.ElementTree import parse
from six.moves.urllib.parse import urljoin


class AppNotFound(Exception):
    pass


class DownloadFailed(Exception):
    def __init__(self, error, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error = error

    def __str__(self):
        if hasattr(self.error, "status_code"):
            return "DownloadFailed(Status=%s): %s" % (self.error.status_code, self.error.text)
        return "DownloadFailed: %s" % self.error


class NoReleaseFound(Exception):
    pass


class VersionNotFound(Exception):
    pass


class SplunkbaseSession(requests.Session):
    __app_info = {}

    def __init__(self, username, password, *args, **kwargs):
        super(SplunkbaseSession, self).__init__(*args, **kwargs)

        r = self.post(
            "/api/account:login",
            data={
                "username": username,
                "password": password
            }
        )
        r.raise_for_status()
        tree = parse(BytesIO(r.content))
        root = tree.find("./{http://www.w3.org/2005/Atom}id")

        self.headers.update({
            "X-Auth-Token": str(root.text)
        })

    def prepare_request(self, request):
        if not request.url.startswith("https://"):
            request.url = urljoin("https://splunkbase.splunk.com/", request.url)
        return super(SplunkbaseSession, self).prepare_request(request)

    def get_app_numeric_id(self, app_name):
        r = self.get("https://apps.splunk.com/apps/id/%s" % app_name, allow_redirects=False)
        if r.status_code != 302:
            # Didn't find the app
            return None

        return r.headers["Location"].split("/")[-1]

    def get_app_info(self, app_name):
        if app_name not in self.__app_info:
            app_id = self.get_app_numeric_id(app_name)
            if app_id is None:
                # Didn't find the app
                return None

            r = self.get(
                "/api/v1/app/%s/" % app_id,
                params={"include": "all"}
            )
            if r.status_code != 200:
                # Didn't find the app
                return None
            self.__app_info[app_name] = r.json()

        return self.__app_info[app_name]

    def download_app(self, app_name, version=None):
        data = self.get_app_info(app_name)

        if data is None:
            raise AppNotFound

        if version is None:
            release = data.get("release", None)

            if release is None:
                raise NoReleaseFound
        else:
            release = None
            for potential_release in data["releases"]:
                if potential_release["title"] == version:
                    release = potential_release
                    break

            if release is None:
                raise VersionNotFound

        app_data = {}

        for checksum_type in ("sha256", "md5"):
            if checksum_type in release:
                app_data["checksum"] = release[checksum_type]
                break

        r = self.get(
            release["path"]
        )
        if r.status_code != 200:
            raise DownloadFailed(r)

        if "checksum" in app_data and checksum_type in release:
            h = hashlib.new(checksum_type)
            h.update(r.content)
            checksum = h.hexdigest()
            if checksum != app_data["checksum"]:
                raise DownloadFailed("Checksum mismatch: expected %s, got %s" % (
                    app_data["checksum"],
                    checksum
                ))

        return {
            "version": release["title"],
            "app": BytesIO(r.content),
            "author": release["manifest"]["info"]["author"][0],
            "appid": data["appid"],
            "release_notes": release["notes"],
            "release_date": dateparse(release["published_time"])
        }

    def get_app_latest_version(self, app_name, splunk_version=None):
        app_info = self.get_app_info(app_name)
        if app_info is None:
            raise AppNotFound

        if splunk_version is None:
            release = app_info.get("release", None)
        else:
            release = None
            for potential_release in app_info.get("releases", []):
                for compatible_version in potential_release["splunk_compatibility"]:
                    if splunk_version == compatible_version or \
                       splunk_version.startswith("%s." % compatible_version):
                        release = potential_release
                        break

        if release is None:
            raise NoReleaseFound

        return release

    def get_app_splunkbase_path(self, app_name):
        app_info = self.get_app_info(app_name)
        if app_info is None:
            raise AppNotFound

        return app_info["path"]


@click.group()
@click.option("-U", "--username", envvar="SPLUNKBASE_USERNAME", required=True)
@click.option("-P", "--password", envvar="SPLUNKBASE_PASSWORD", required=False)
@click.pass_context
def cli(ctx, username, password):
    if password is None:
        password = getpass.getpass("Splunkbase password: ")
    ctx.obj = SplunkbaseSession(username, password)


@cli.command()
@click.option("--splunk-version", required=False,
              help="Restrict to app versions compatible with a given Splunk version")
@click.argument("app_dir", nargs=1, required=True)
@click.pass_context
def check_app_for_update(ctx, splunk_version, app_dir):
    app_name = os.path.basename(app_dir)

    try:
        release = ctx.obj.get_app_latest_version(app_name, splunk_version)
    except (AppNotFound, NoReleaseFound):
        release = None

    with open(os.path.join(app_dir, "default", "app.conf")) as f:
        app_config = RawConfigParser(delimiters="=", comment_prefixes="#")
        app_config.optionxform = str
        app_config.read_file(f)

    print("%s %s" % (app_name, app_config["launcher"]["version"]))
    if not release:
        print("Latest: UNAVAILABLE")
    else:
        if release["title"] == app_config["launcher"]["version"]:
            print("App is up-to-date")
        else:
            print("Latest: %s" % (release["title"]))

        print("URL: %s" % ctx.obj.get_app_splunkbase_path(app_name))
        print("Supported Splunk Versions:")
        print(" ".join(release["splunk_compatibility"]))


@cli.command()
@click.option("--output-path", required=False,
              help="Path and filename location to save the app")
@click.option("--version", required=False,
              help="Version of app to download, default is latest")
@click.argument("app_name", nargs=1, required=True)
@click.pass_context
def download_app(ctx, output_path, version, app_name):
    try:
        result = ctx.obj.download_app(app_name, version)
    except AppNotFound:
        print("App '%s' not found on Splunkbase" % app_name)
        return 1
    except VersionNotFound:
        print("'%s' found on Splunkbase, but version '%s' is unavailable" % (app_name, version))
        return 1
    except DownloadFailed:
        print(repr(DownloadFailed))
        return 1

    if output_path is None:
        output_path = "%s-%s.tgz" % (app_name, result["version"])

    if output_path == "-":
        sys.stdout.buffer.write(result["app"].read())
    else:
        with open(output_path, "wb") as f:
            f.write(result["app"].read())

    return 0


@cli.command()
@click.option("--splunk-version", required=False,
              help="Restrict to app versions compatible with a given Splunk version")
@click.argument("app_name", nargs=1, required=True,)
@click.pass_context
def get_latest_version(ctx, splunk_version, app_name):
    try:
        release = ctx.obj.get_app_latest_version(app_name, splunk_version)
    except AppNotFound:
        print("App '%s' not found on Splunkbase" % app_name)
        return 1
    except NoReleaseFound:
        print("No compatible version of '%s' found on Splunkbase" % app_name)
        return 1

    if "title" in release["manifest"]["info"]:
        print("%s - %s" % (app_name, release["manifest"]["info"]["title"]))
    else:
        print(app_name)
    print("Latest: %s" % (release["title"]))
    print("Supported Splunk Versions:")
    print(" ".join(release["splunk_compatibility"]))

    return 0
