'''
Created by dedouwe26 / dedouwe / ...
At 24-8-2022 20:25.

This python program will automaticly convert 
java minecraft code to a maven project and 
it also can make a patcher program later on.
'''
from importlib.resources import path
import json
import os
import requests
from pathlib import Path

CLIENT='c'
SERVER='s'

def download(url,path):
    with open(path,'w') as file:
        file.write(requests.get(url).content.decode('utf-8'))

def createVersionManifest(manifest):
    
    download(manifest,Path('tmp/version_manifest_v2.json'))
    with open(Path('tmp/version_manifest_v2.json'),'r') as file:
        latestData = json.load(file)
        latestRelease=latestData['latest']['release']
        latestSnapshot=latestData['latest']['snapshot']
    return latestRelease, latestSnapshot

def getVersionManifest(version):
    with open(Path('tmp/version_manifest_v2.json'),'r') as file:
        jsonData = json.load(file)
        for obj in jsonData['versions']:
            if obj['id']==version:
                print('Found...')
                return obj
        print('This is not a valid version.')
        exit(1)  

def main():
    manifestV2='https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'

    print('-- Welcome to MCDemaster --')
    if not Path('tmp/').is_dir():
        os.makedirs(Path('tmp/'))
    release, snapshot = createVersionManifest(manifestV2)
    version=input(f'The latest version is {release} and the latest snapshot is {snapshot}.\nPlease put your version in: ')
    versionManifestUrl=getVersionManifest(version)['url']
    download(versionManifestUrl,Path(f'tmp/{version}.json'))
    side = input('Client or server side (c/s): ')
    if side==CLIENT:
        pass
        # client
    elif side==SERVER:
        pass
        # server
    else: 
        print('Invalid version side...')
        exit(1)
        
    

if __name__ == "__main__":
    main()