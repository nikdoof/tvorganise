from setuptools import setup, find_packages
setup(
name = 'tvorganise',
version='0.1',

author='Andrew Williams',
description='Utilities to verify TV episode filenames and move them into a organise tree. Forked from dbr/Bens checkTvEps toolset',
url='http://github.com/dbr/checktveps/tree/master',
license='GPLv2',

py_modules = ['filename_config', 'tvorganise'],
entry_points = {
    'console_scripts':[
        'tvorganise = tvOrganise:main'
    ]
},

classifiers=[
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Multimedia",
    "Topic :: Utilities"
]
)
