'''
Created by dedouwe26 / dedouwe / ...
At 24-8-2022 20:25.

This python program will automaticly convert 
java minecraft code to a maven project and 
it also can make a patcher program later on.
'''
import hashlib
import json
import os
import shutil
from pathlib import Path

import requests

CLIENT = 'client'
SERVER = 'server'


def download(url, path):
    with open(path, 'w') as file:
        file.write(requests.get(url).content.decode('utf-8'))


def createDirs(dir):
    if not dir.is_dir():
        os.makedirs(dir)


def createVersionManifest(manifest):

    download(manifest, Path('tmp/version_manifest_v2.json'))
    with open(Path('tmp/version_manifest_v2.json'), 'r') as file:
        latestData = json.load(file)
        latestRelease = latestData['latest']['release']
        latestSnapshot = latestData['latest']['snapshot']
    return latestRelease, latestSnapshot


def getVersionManifest(version):
    with open(Path('tmp/version_manifest_v2.json'), 'r') as file:
        jsonData = json.load(file)
        for obj in jsonData['versions']:
            if obj['id'] == version:
                print('Found...')
                return obj
        print('This is not a valid version.')
        exit(1)


def getSide(side, version):
    if not side == CLIENT and not side == SERVER:
        print('Invalid version side...')
        exit(1)
    with open(Path(f'versions/{version}/manifest.json'), 'r') as file:
        downloadData = json.load(file)['downloads']
    sideData = downloadData[side]
    sideMappingData = downloadData[side+'_mappings']
    request = requests.get(sideData['url'])
    sideHash = hashlib.sha1(request.content).hexdigest()
    request = requests.get(sideMappingData['url'])
    sideMappingHash = hashlib.sha1(request.content).hexdigest()
    if sideHash == sideData['sha1']:
        print('Jar file checked.')
    else:
        print('Jar file doesnt match up...')
        exit(1)
    if sideMappingHash == sideMappingData['sha1']:
        print('Mapping file checked.')
    else:
        print('Mapping file doesnt match up...')
        exit(1)
    with open(Path(f'versions/{version}/{side}.jar'), 'wb') as file:
        request=requests.get(sideData['url'],stream=True)
        request.raw.decode_content=True
        shutil.copyfileobj(request.raw, file)
    download(sideMappingData['url'], Path(f'versions/{version}/{side}.txt'))


def main():
    manifestV2='https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'

    print('-- Welcome to MCDemaster --')
    createDirs(Path('tmp/'))
    createDirs(Path('versions/'))
    release, snapshot = createVersionManifest(manifestV2)
    version = input(
        f'The latest version is {release} and the latest snapshot is {snapshot}.\nPlease put your version in: ')
    createDirs(Path(f'versions/{version}/'))
    versionManifestUrl = getVersionManifest(version)['url']
    download(versionManifestUrl, Path(f'versions/{version}/manifest.json'))
    side = input('Client or server side (client/server): ')
    getSide(side, version)


if __name__ == "__main__":
    main()
