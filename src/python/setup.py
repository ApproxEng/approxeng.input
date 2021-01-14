__author__ = 'tom'

from setuptools import setup, find_namespace_packages

# To build for local development use 'python setup.py develop'.
# To upload a version to pypi use 'python setup.py clean sdist upload'.
# Docs are built with 'make html' in the docs directory parallel to this one
setup(
    name='approxeng.input',
    version='2.6.0',
    description='Python game controller support using evDev for Raspberry Pi and other Linux systems',
    classifiers=['Programming Language :: Python :: 3.5'],
    url='https://github.com/ApproxEng/approxeng.input/',
    author='Tom Oinn',
    author_email='tomoinn@gmail.com',
    license='ASL2.0',
    packages=find_namespace_packages(),
    install_requires=['evdev==1.2.0', 'pyyaml==5.3.1'],
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['nose'],
    dependency_links=[],
    zip_safe=False,
    entry_points={'console_scripts': ['approxeng_input_profile=approxeng.input.gui.profiler:profiler_main',
                                      'approxeng_input_show_controls=approxeng.input.gui.console:show_controls',
                                      'approxeng_input_list_devices=approxeng.input.gui.console:list_devices',
                                      'approxeng_input_scan_sys=approxeng.input.gui.console:sys_scan']})
