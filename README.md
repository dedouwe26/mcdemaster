# MCDemaster
> Minecraft-Decompile-Master

This python program will automaticly convert java minecraft code to a maven project and it also can make a patcher program later on (or not). I have created this project because i really wanted to change Minecrafts code.
## Requirements
You need to have [Minecraft](https://www.minecraft.net/ "Minecraft") purchased and installed.
You also need to have [Java](https://www.oracle.com/java/technologies/downloads/ "Java") installed. You can install that with that link or you can just search it up.
## Build the project
You can download the releases. You can also build it yourself:
First download [Python](https://www.python.org/ "Python").
Then you need to install the dependencies. \
`pip install -r requirements.txt` \
And now generating the program  *<button onclick='document.body.style.backgroundColor="red";'>for your machine*: \
`python -m PyInstaller main.py -F -c -n MCDemaster` \
*For additional arguments you can look in the [PyInstaller Documentation](https://pyinstaller.org/en/stable/usage.html "PyInstaller Documentation").*
## Libraries Used
[SpecialSource](https://github.com/md-5/SpecialSource "SpecialSource")
and
[Fernflower](https://github.com/JetBrains/intellij-community/tree/master/plugins/java-decompiler/engine "Fernflower")
## Thanks To
[hube12](https://github.com/hube12/DecompilerMC "hube12")