__author__ = 'tom'
from setuptools import setup, find_packages

# To build for local development use 'python setup.py develop'.
# To upload a version to pypi use 'python setup.py clean sdist upload'.
# Docs are built with 'make html' in the docs directory parallel to this one
setup(
    name='approxeng.input',
    version='1.0.1',
    description='Python game controller support using evDev for Raspberry Pi and other Linux systems',
    classifiers=['Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3.4'],
    url='https://github.com/ApproxEng/approxeng.input/',
    author='Tom Oinn',
    author_email='tomoinn@gmail.com',
    license='ASL2.0',
    packages=find_packages(),
    install_requires=['evdev==0.6.4'],
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['nose'],
    dependency_links=[],
    zip_safe=False)
