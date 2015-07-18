from setuptools import setup, find_packages

import os

base_dir = os.path.dirname(__file__)

about = {}
with open(os.path.join(base_dir, "smbus", "__about__.py")) as f:
    exec(f.read(), about)

readme = os.path.join(base_dir, 'README.rst')
with open(readme) as f:
        long_description = f.read()

CFFI_VERSION = '1.1.0'

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__summary__'],
    long_description=long_description,
    author=about['__author__'],
    author_email=about['__email__'],
    url=about['__uri__'],
    license=about['__license__'],
    packages=find_packages(exclude=["test*", "*test*"]),
    zip_safe=False,
    ext_package='smbus',
    install_requires=['cffi >= ' + CFFI_VERSION],
    setup_requires=['cffi >= ' + CFFI_VERSION],
    cffi_modules=["smbus_cffi_build.py:ffi"],

    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: System :: Hardware',
    ],
)
