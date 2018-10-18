#!/usr/bin/env python

import apt
import apt.debfile
# import apt.progress
import sys
import tempfile
import time
import requests

from packaging.version import Version, parse
from progressbar import Bar, Percentage, ProgressBar 

def check_version(latest_version):
    cache = apt.Cache()
    
    try:
        pkg = cache['emby-server']
    except:
        # if package is unavailable, install emby-server
        return True
    
    latest_version = parse(latest_version)
    pkg_version = parse(pkg.versions[0].source_version)

    return pkg_version < latest_version

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

    if not check_version(latest):
        return False

    return latest, download_url

def download_emby_package(url):
    fd, name = tempfile.mkstemp()
    r = requests.get(url)

    total_length = int(r.headers.get('content-length'))
    download_length = 0

    bar = ProgressBar(widgets=[Percentage(), Bar()], maxval=total_length).start()
    
    with open(fd, 'wb') as f: 
        for chunk in r.iter_content(chunk_size=8192):
            if chunk: # filter out keep-alive chunks
                download_length += len(chunk)

                time.sleep(0.01)
                bar.update(download_length)

                f.write(chunk)

    bar.finish()

    return name

def install_emby_package(file_path):
    # initialize the apt cache
    cache = apt.Cache()
    cache.update()
    cache.open(None)

    package = apt.debfile.DebPackage(file_path, cache)
    package.check()
    
    # may fail due to bad file descriptor
    # https://bugs.launchpad.net/ubuntu/+source/software-center/+bug/1306543
    # package.install(apt.progress.base.InstallProgress())
    package.install()

def capture_emby_package(version, url):
    print('Downloading', version, 'from', url)

    pkg = download_emby_package(url)
    
    print('\nInstalling file ', pkg)
    install_emby_package(pkg)

def main():
    release = check_latest_release()

    if not release:
        print('Up to date!')
        return False
    
    version, download_url = release

    return capture_emby_package(version, download_url)

if __name__ == "__main__":
    main()
