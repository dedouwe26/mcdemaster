'''
Created by dedouwe26 / dedouwe / ...
At 24-8-2022 20:25.

This python program will automaticly convert 
java minecraft code to a maven project and 
it also can make a patcher program later on.
    See: ./README.md
'''
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from zipfile import ZipFile


import requests

CLIENT = 'client'
SERVER = 'server'


def download(url, path, byteMode=False):
    if byteMode:
        with open(path, 'wb') as file:
            file.write(requests.get(url).content)
    else:
        with open(path, 'w') as file:
            file.write(requests.get(url).content.decode('utf-8'))


def createDirs(dir):
    if not dir.is_dir():
        os.makedirs(dir)

def cleanBrackets(line, counter):
    while '[]' in line:  # get rid of the array brackets while counting them
        counter += 1
        line = line[:-2]
    return line, counter


def remapPath(path):
    remapSymbols = {"int": "I", "double": "D", "boolean": "Z", "float": "F",
                    "long": "J", "byte": "B", "short": "S", "char": "C", "void": "V"}
    return "L" + "/".join(path.split(".")) + ";" if path not in remapSymbols else remapSymbols[path]

def listFiles(dir):
    list = []
    for file in os.scandir(dir):
        if file.is_dir():
            list += listFiles(Path(dir, file.name))
        else:
            list.append(file)
    return list

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


def getSide(version, side):
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
    download(sideData['url'], Path(
        f'versions/{version}/{side}.jar'), byteMode=True)
    download(sideMappingData['url'], Path(f'versions/{version}/{side}.txt'))


def formatMappings(version, side):
    with open(Path(f'versions/{version}/{side}.txt'), 'r') as inputFile:
        file_name = {}
        for line in inputFile.readlines():
            if line.startswith('#'):
                continue
            deobf_name, obf_name = line.split(' -> ')
            if not line.startswith('    '):
                obf_name = obf_name.split(":")[0]
                file_name[remapPath(deobf_name)] = obf_name

    with open(Path(f'versions/{version}/{side}.txt'), 'r') as inputFile, open(Path(f'versions/{version}/{side}.tsrg'), 'w') as outputFile:
        for line in inputFile.readlines():
            if line.startswith('#'):
                continue
            deobf_name, obf_name = line.split(' -> ')
            if line.startswith('    '):
                obf_name = obf_name.rstrip()
                deobf_name = deobf_name.lstrip()
                method_type, method_name = deobf_name.split(" ")
                method_type = method_type.split(":")[-1]
                if "(" in method_name and ")" in method_name:
                    variables = method_name.split('(')[-1].split(')')[0]
                    function_name = method_name.split('(')[0]
                    array_length_type = 0
                    method_type, array_length_type = cleanBrackets(
                        method_type, array_length_type)
                    method_type = remapPath(method_type)
                    method_type = "L" + \
                        file_name[method_type] + \
                        ";" if method_type in file_name else method_type
                    if "." in method_type:
                        method_type = "/".join(method_type.split("."))
                    for i in range(array_length_type):
                        if method_type[-1] == ";":
                            method_type = "[" + method_type[:-1] + ";"
                        else:
                            method_type = "[" + method_type

                    if variables != "":
                        array_length_variables = [0] * len(variables)
                        variables = list(variables.split(","))
                        for i in range(len(variables)):
                            variables[i], array_length_variables[i] = cleanBrackets(
                                variables[i], array_length_variables[i])
                        variables = [remapPath(variable)
                                     for variable in variables]
                        variables = [
                            "L" + file_name[variable] + ";" if variable in file_name else variable for variable in variables]
                        variables = [
                            "/".join(variable.split(".")) if "." in variable else variable for variable in variables]
                        for i in range(len(variables)):
                            for j in range(array_length_variables[i]):
                                if variables[i][-1] == ";":
                                    variables[i] = "[" + \
                                        variables[i][:-1] + ";"
                                else:
                                    variables[i] = "[" + variables[i]
                        variables = "".join(variables)

                    outputFile.write(
                        f'\t{obf_name} ({variables}){method_type} {function_name}\n')
                else:
                    outputFile.write(f'\t{obf_name} {method_name}\n')

            else:
                obf_name = obf_name.split(":")[0]
                outputFile.write(remapPath(obf_name)[
                                 1:-1] + " " + remapPath(deobf_name)[1:-1] + "\n")


def downloadLibraries():
    os.mkdir(Path('libraries'))
    download('https://raw.githubusercontent.com/JetBrains/intellij-community/master/LICENSE.txt',
             Path('libraries/LICENSE-Fernflower.txt'))
    download('https://raw.githubusercontent.com/md-5/SpecialSource/master/LICENSE',
             Path('libraries/LICENSE-Specialsource.txt'))
    download('https://dedouwe.nl/download-data/fernflower.jar',
             Path('libraries/fernflower.jar'), byteMode=True)
    download('https://repo.maven.apache.org/maven2/net/md-5/SpecialSource/1.10.0/SpecialSource-1.10.0-shaded.jar',
             Path('libraries/specialsource.jar'), byteMode=True)
    print('Downloaded libraries')


def startMapping(version, side):
    if not Path(f'versions/{version}/{side}-deobf.jar').exists():
        jarIn = Path(f'versions/{version}/{side}.jar')
        jarOut = Path(f'versions/{version}/{side}-deobf.jar')
        srgIn = Path(f'versions/{version}/{side}.tsrg')
        subprocess.run(['java', '-jar', Path('libraries/specialsource.jar'),
                       f'--in-jar={jarIn}', f'--out-jar={jarOut}', f'--srg-in={srgIn}'])
        if Path('versions/{version}/{side}-deobf.jar').exists():
            print('Deobfuscating failed...')
            exit(-1)


def startDecompile(version, side):
    if not Path(f'tmp/{version}/{side}-deobf.jar').exists():
        createDirs(Path(f'tmp/{version}/'))
        source = Path(f'versions/{version}/{side}-deobf.jar')
        dest = Path(f'tmp/{version}/')
        subprocess.run(['java', '-jar', Path('libraries/fernflower.jar'),
                       source.absolute(), dest.absolute()])
        if not Path(f'tmp/{version}/{side}-deobf.jar').exists():
            print('Decompiling failed...')
            exit(-1)


def unzipDecompiled(version, side):
    createDirs(Path(f'src/{version}/{side}/'))
    with ZipFile(Path(f'tmp/{version}/{side}-deobf.jar')) as zip:
        zip.extractall(Path(f'src/{version}/{side}/'))
    shutil.rmtree(Path(f'tmp/{version}/'))


def moveItems(version, side): # Not working!
    acceptedDirs=[]
    filePath=Path(f'src/{version}/{side}')
    for entry in os.scandir(filePath):
        if entry.is_dir():
            fileList = listFiles(filePath)
            isJavainDir=False
            for file in fileList:
                if str(file).endswith('.java'):
                    isJavainDir=True
                    break
            if not isJavainDir:
                continue

            acceptedDirs.append(Path(filePath, entry))
    print(acceptedDirs)

        


            

def main():
    manifestV2 = 'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'

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
    getSide(version, side)
    print('Starting formatting mappings')
    formatMappings(version, side)
    print('succesfull formatted mappings')
    if not Path('libraries').is_dir():
        print('Downloading libraries')
        downloadLibraries()
    else:
        print('Libaries already downloaded')
    startMapping(version, side)
    print('Done mapping')
    print('Start decompiling!')
    startDecompile(version, side)
    print('Starting unzipping')
    #unzipDecompiled(version, side)
    print('Starting moving src')
    moveItems(version, side)

if __name__ == '__main__':
    main()