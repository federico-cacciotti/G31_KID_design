from setuptools import setup

setup(
  name='KID_drawer',
  version='0.1.1',
  author='Federico Cacciotti',
  author_email='fe.cacciotti@gmail.com',
  packages=['package_name', 'package_name.test'],
  license='LICENSE.txt',
  description='A python package to generate Kinetic Inductance Detectors',
  long_description=open('README.md').read(),
  install_requires=[
      "numpy",
      "pathlib",
      "os",
      "matplotlib",
      "shapely"
  ],
)
