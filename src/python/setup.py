__author__ = 'tom'
from setuptools import setup, find_namespace_packages

# To build for local development use 'python setup.py develop'.
# To upload a version to pypi use 'python setup.py clean sdist upload'.
# Docs are built with 'make html' in the docs directory parallel to this one
setup(
    name='approxeng.input',
    version='2.5.0',
    description='Python game controller support using evDev for Raspberry Pi and other Linux systems',
    classifiers=['Programming Language :: Python :: 3.5'],
    url='https://github.com/ApproxEng/approxeng.input/',
    author='Tom Oinn',
    author_email='tomoinn@gmail.com',
    license='ASL2.0',
    packages=find_namespace_packages(),
    install_requires=['evdev==1.2.0'],
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['nose'],
    dependency_links=[],
    zip_safe=False)
