# /setup.py
#
# Installation and setup script for polysquare-cmake-linter
#
# See LICENCE.md for Copyright information
"""Installation and setup script for polysquare-cmake-linter."""

from setuptools import find_packages
from setuptools import setup

setup(name="polysquare-cmake-linter",
      version="0.0.4",
      description="Polysquare CMake Linter",
      long_description="Lint a CMake file for polysquare CMake style guide\n"
                       "The following checks are provided:\n"
                       " - structure/namespace: All definitions should be"
                       " prefixed with the namespace indicated by"
                       " --namespace\n"
                       " - style/space_before_func: All function calls"
                       " should have a single space before the open"
                       " brackets\n"
                       " - style/set_var_case: All set variables should be"
                       " uppercase\n"
                       " - style/uppercase_args: All function and macro"
                       " arguments should be uppercase\n"
                       " - style/lowercase_func: All function calls and"
                       " definitions should be lowercase\n"
                       " - style/argument_align: All arguments to a function"
                       " call need to be aligned\n"
                       " - style/doublequotes: Only use double-quotes\n"
                       " - style/indent: All sections must be indented to"
                       " the level specified by --indent\n"
                       " - correctness/quotes: All path dereferences or"
                       " literals that look like paths must be quoted\n"
                       " - unused/private: No unused private definitions\n"
                       " - unused/private_var: No unused private vars\n"
                       " - access/other_private: Do not use private"
                       " definitions not defined in this file\n"
                       " - access/private_var: Do not use private variables"
                       " not defined in this file\n",
      author="Sam Spilsbury",
      author_email="smspillaz@gmail.com",
      url="http://github.com/polysquare/polysquare-cmake-linter",
      classifiers=["Development Status :: 3 - Alpha",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.1",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "Programming Language :: Python :: 3.4",
                   "Intended Audience :: Developers",
                   "Topic :: Software Development :: Build Tools",
                   "License :: OSI Approved :: MIT License",
                   "Programming Language :: Python :: 3"],
      license="MIT",
      keywords="development linters",
      packages=find_packages(exclude=["tests"]),
      install_requires=["cmakeast>=0.0.7"],
      extras_require={
          "test": ["coverage",
                   "nose",
                   "nose-parameterized",
                   "testtools"]
      },
      entry_points={
          "console_scripts": [
              "polysquare-cmake-linter=polysquarecmakelinter.linter:main"
          ]
      },
      test_suite="nose.collector",
      zip_safe=True)
