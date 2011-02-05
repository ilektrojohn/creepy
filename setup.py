from distutils.core import setup

files = ["include/*"]

setup(name = "creepy",
    version = "0.1",
    author = "Yiannis Kakavas",
    author_email = "jkakavas@gmail.com",
    url = "https://github.com/ilektrojohn/creepy",
    packages = ['creepy'], 
    package_data = {'creepy' : files }, 
    scripts = ["creepy/creepymap"], 
    license = "GPL")
