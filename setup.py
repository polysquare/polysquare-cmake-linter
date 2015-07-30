# /setup.py
#
# Installation and setup script for polysquare-cmake-linter
#
# See /LICENCE.md for Copyright information
"""Installation and setup script for polysquare-cmake-linter."""

from setuptools import find_packages
from setuptools import setup

setup(name="polysquare-cmake-linter",
      version="0.0.9",
      description="""Polysquare CMake Linter""",
      long_description_markdown_filename="README.md",
      author="Sam Spilsbury",
      author_email="smspillaz@gmail.com",
      url="http://github.com/polysquare/polysquare-cmake-linter",
      classifiers=["Development Status :: 3 - Alpha",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.1",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "Programming Language :: Python :: 3.4",
                   "Intended Audience :: Developers",
                   "Topic :: Software Development :: Build Tools",
                   "License :: OSI Approved :: MIT License"],
      license="MIT",
      keywords="development linters",
      packages=find_packages(exclude=["tests"]),
      install_requires=["cmakeast>=0.0.7"],
      extras_require={
          "green": ["testtools",
                    "nose",
                    "nose-parameterized>=0.5.0",
                    "setuptools-green"],
          "polysquarelint": ["polysquare-setuptools-lint"]
      },
      entry_points={
          "console_scripts": [
              "polysquare-cmake-linter=polysquarecmakelinter.linter:main"
          ]
      },
      test_suite="nose.collector",
      zip_safe=True,
      include_package_data=True)
