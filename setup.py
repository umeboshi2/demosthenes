from setuptools import setup, find_packages
import sys, os

version = '0.0.0'

setup(name='demosthenes',
      version=version,
      description="orator for ansible",
      long_description="""\
orator for ansible""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Joseph Rawson',
      author_email='joseph.rawson.works@gmail.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'argparse',
          'netaddr',
          'passlib',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      demos-init = demosthenes.scripts.demos_init:main
      demos = demosthenes.scripts.demos:main
      demos-update = demosthenes.scripts.demos_update:main
      """,
      )
