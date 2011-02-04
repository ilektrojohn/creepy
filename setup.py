from distutils.core import setup

files = ["include/*"]

setup(name = "creepy",
    version = "0.1",
    author = "Yiannis Kakavas",
    author_email = "jkakavas@gmail.com",
    url = "https://github.com/ilektrojohn/creepy",
    packages = ['package'], 
    package_data = {'package' : files }, 
    scripts = ["package/creepymap.py"], 
    license = "gpl")
