#!/usr/bin/env python3

from setuptools import setup
from setuptools import find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

print('-'*120)
print()
print('-'*120)

setup(
    name='scriptskeleton',
    version='0.0.1pre1',
    description='Generate script and project skeletons with pre-defined logging',
    long_description=(here/'README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    url='https://github.com/DrDougPhD/Script-Skeletons',
    author='Doug McGeehan',
    author_email='djmvfb@mst.edu',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        # Help wanted to verify which versions of Python work!
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='codegen',
    package_dir={'scriptskeleton': 'src/scriptskeleton'},
    packages=find_packages(where='src'),
    python_requires='>=3.6.*, <4',
    package_data={
        '': ['*.template', '*.txt'],
    },
    entry_points={
        'console_scripts': [
            'scriptskeleton=scriptskeleton.skeleton:main',
        ],
    },
)
