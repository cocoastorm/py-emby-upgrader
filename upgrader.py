#!/usr/bin/env python

import apt
import apt.progress
import sys
import tempfile
import requests

def check_version(latest_version):
    # TODO: find a way to query Emby version
    current_version = 'v3.3.0'
    return current_version < latest_version

def get_package_asset_url(assets):
    pkg = {'name': 'amd64.deb','content_type': 'application/octet-stream'}

    for asset in assets:
        is_amd64 = pkg['name'] in asset['name']
        is_content_type = pkg['content_type'] == asset['content_type']

        if is_amd64 and is_content_type:
            return asset['browser_download_url']

def check_latest_release():
    url = 'https://api.github.com/repos/MediaBrowser/Emby.Releases/releases/latest'
    headers = {'user-agent': 'emby-upgrader/0.0.1'}

    r = requests.get(url, headers=headers)
    data = r.json()

    latest = data['tag_name']
    download_url = get_package_asset_url(data['assets'])

    if check_version(latest):
        return False

    return latest, download_url

def download_emby_package(url):
    local_f = tempfile.mkstemp()
    r = requests.get(url)
    with open(local_f, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive chunks
                f.write(chunk)
    return local_f

def install_emby_package(file_path):
    # initialize the apt cache
    cache = apt.Cache()
    cache.update()
    cache.open(None)

    package = apt.debfile.DebPackage(file_path, cache)
    package.install(apt.progress.InstallProgress())

def capture_emby_package(version, url):
    print('Downloading ', version, 'from ', url)

    pkg = download_emby_package(url)
    
    print('Installing file ', pkg)
    install_emby_package(pkg)

def main():
    release = check_latest_release()

    if not release:
        return False
    
    version, download_url = release

    return capture_emby_package(version, download_url)

if __name__ == "__main__":
    main()
