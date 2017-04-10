# Building

This code builds using setuptools. I strongly suggest you use a virtual environment, and then use 
```python setup.py develop``` - this will symlink into your python installation such that any changes
you make to the code here will be immediately reflected in the libraries imported by scripts without
having to install again.

## Publishing to PyPi

Publishing to the Python Package Index allows users to install through pip. Register first using 
```python setup.py register``` then upload with ```python setup.py clean sdist upload```