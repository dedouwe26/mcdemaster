from pathlib import Path
import shutil
import subprocess
from zipfile import ZipFile
import requests
import hashlib
import json
import os
from diff_match_patch import diff_match_patch
side='client or server'
version='1.19.2'
def download(url, path, byteMode=False):
    if byteMode:
        with open(path, 'wb') as file:
            file.write(requests.get(url).content)
    else:
        with open(path, 'w') as file:
            file.write(requests.get(url).content.decode('utf-8'))
def cleanBrackets(line, counter):
    while '[]' in line:
        counter += 1
        line = line[:-2]
    return line, counter
def remapPath(path):
    remapSymbols = {"int": "I", "double": "D", "boolean": "Z", "float": "F",
                    "long": "J", "byte": "B", "short": "S", "char": "C", "void": "V"}
    return "L" + "/".join(path.split(".")) + ";" if path not in remapSymbols else remapSymbols[path]
print('Starting creating minecraft '+side+'...')
if not side == 'client' and not side == 'server':
    print('Invalid version side...')
    exit(1)
with open(Path('tmp/manifest.json'), 'r') as file:
    downloadData = json.load(file)['downloads']
sideData = downloadData[side]
sideMappingData = downloadData[side+'_mappings']
request = requests.get(sideData['url'])
sideHash = hashlib.sha1(request.content).hexdigest()
request = requests.get(sideMappingData['url'])
sideMappingHash = hashlib.sha1(request.content).hexdigest()
if not sideHash == sideData['sha1']:
    print('Jar file doesnt match up...')
    exit(1)
if not sideMappingHash == sideMappingData['sha1']:
    print('Mapping file doesnt match up...')
    exit(1)
download(sideData['url'], Path('tmp/minecraft.jar'), byteMode=True)
download(sideMappingData['url'], Path('tmp/mapping.txt'))
with open(Path('tmp/mapping.txt'), 'r') as inputFile:
    file_name = {}
    for line in inputFile.readlines():
        if line.startswith('#'):
            continue
        deobf_name, obf_name = line.split(' -> ')
        if not line.startswith('    '):
            obf_name = obf_name.split(":")[0]
            file_name[remapPath(deobf_name)] = obf_name
with open(Path('tmp/mapping.txt'), 'r') as inputFile, open(Path('tmp/mapping.tsrg'), 'w') as outputFile:
    for line in inputFile.readlines():
        if not line.startswith('#'):
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
                    method_type, array_length_type = cleanBrackets(method_type, array_length_type)
                    method_type = remapPath(method_type)
                    method_type = "L"+file_name[method_type]+";" if method_type in file_name else method_type
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
                            variables[i], array_length_variables[i] = cleanBrackets(variables[i], array_length_variables[i])
                        variables = [remapPath(variable)for variable in variables]
                        variables = ["L" + file_name[variable] + ";" if variable in file_name else variable for variable in variables]
                        variables = ["/".join(variable.split(".")) if "." in variable else variable for variable in variables]
                        for i in range(len(variables)):
                            for j in range(array_length_variables[i]):
                                if variables[i][-1] == ";":
                                    variables[i] = "[" + \
                                        variables[i][:-1] + ";"
                                else:
                                    variables[i] = "[" + variables[i]
                        variables = "".join(variables)

                    outputFile.write(f'\t{obf_name} ({variables}){method_type} {function_name}\n')
                else:
                    outputFile.write(f'\t{obf_name} {method_name}\n')

            else:
                obf_name = obf_name.split(":")[0]
                outputFile.write(remapPath(obf_name)[1:-1] + " " + remapPath(deobf_name)[1:-1] + "\n")
os.mkdir(Path('libraries'))
download('https://dedouwe.nl/download-data/fernflower.jar',Path('libraries/fernflower.jar'), byteMode=True)
download('https://repo.maven.apache.org/maven2/net/md-5/SpecialSource/1.10.0/SpecialSource-1.10.0-shaded.jar',Path('libraries/specialsource.jar'), byteMode=True)
jarIn = Path('tmp/minecraft.jar')
jarOut = Path('tmp/deobf.jar')
srgIn = Path(f'tmp/mapping.tsrg')
subprocess.run(['java', '-jar', Path('libraries/specialsource.jar'),'--in-jar='+str(jarIn), '--out-jar='+str(jarOut), '--srg-in='+str(srgIn)])
if Path('tmp/deobf.jar').exists():
    print('Failed...')
    exit(-1)
os.makedirs(Path(f'tmp/decomp/'))
source = Path(f'tmp/deobf.jar')
dest = Path(f'tmp/decomp/')
subprocess.run(['java', '-jar', Path('libraries/fernflower.jar'),source.absolute(), dest.absolute()])
if not Path(f'tmp/decomp/deobf.jar').exists():
    print('Failed...')
    exit(-1)
os.makedirs(Path(f'tmp/src/'))
with ZipFile(Path(f'tmp/decomp/deobf.jar')) as zip:
    zip.extractall(Path(f'src/{version}/{side}/'))
shutil.rmtree(Path(f'src/{version}/{side}/META-INF/'))
dmp=diff_match_patch()
