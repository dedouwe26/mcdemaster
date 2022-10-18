# MCDemaster
> Minecraft-Decompile-Master

This python program will automaticly convert java minecraft code to a maven project and it also can make a patcher program later on (or not). I have created this project because i wanted to change Minecrafts code.
## Requirements
You need to have [Minecraft](https://www.minecraft.net/ "Minecraft") purchased and installed.
You also need to have [Java](https://www.oracle.com/java/technologies/downloads/ "Java") installed. You can install that with that link or you can just search it up.
## Usage
You can execute the executables in the release section or you can build it yourself. \
Open up the executable and choose your version and enter. Enter the side (client/server). Then you need to wait until its says that it finished. Press enter to exit and open you IDE that supports Maven. Open the mc/ Maven project and you are done. \
When you are done editing, open the executable again and it asks you to select a option. If you want to make a Patcher you enter 1. If you want to choose another version enter 2. When you want to make a Patcher, it can detect the version, else you need to enter the version yourself. The same with the side. Wait until its done. The Patcher is in the pather.zip.
## Build the project
You can download the releases. You can also build it yourself:
First download [Python](https://www.python.org/ "Python").
Then you need to install the dependencies. \
`pip install -r requirements.txt` \
And now generating the program  *for your machine*: \
`python -m PyInstaller main.py -F -c -n MCDemaster` \
*For additional arguments you can look in the [PyInstaller Documentation](https://pyinstaller.org/en/stable/usage.html "PyInstaller Documentation").*
## Libraries Used
[SpecialSource](https://github.com/md-5/SpecialSource "SpecialSource")
and
[Fernflower](https://github.com/JetBrains/intellij-community/tree/master/plugins/java-decompiler/engine "Fernflower")
## Thanks To
[hube12](https://github.com/hube12/DecompilerMC "hube12")