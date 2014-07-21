from setuptools import setup, find_packages, Distribution

Distribution(attrs=dict(setup_requires=['cffi >= 0.8']))

import cffi
import os
import smbus

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
with open(readme) as f:
        long_description = f.read()

setup(
    name='smbus-cffi',
    version='0.3.2',
    description='This Python module allows SMBus access through the I2C /dev interface on Linux hosts. The host kernel must have I2C support, I2C device interface support, and a bus adapter driver.',
    long_description=long_description,
    author='David Schneider',
    author_email='david.schneider@bivab.de',
    url='https://github.com/bivab/smbus-cffi',
    packages=find_packages(exclude=["test*", "*test*"]),
    zip_safe=False,
    ext_package='smbus',
    ext_modules=[smbus.ffi.verifier.get_extension()],
    install_requires=['cffi >= 0.8'],
    license='GPLv2',

    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: System :: Hardware',
    ],
)
