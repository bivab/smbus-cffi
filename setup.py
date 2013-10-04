from setuptools import setup
import smbus

setup(
    name='smbus-cffi',
    version='0.1',
    description='This Python module allows SMBus access through the I2C /dev interface on Linux hosts. The host kernel must have I2C support, I2C device interface support, and a bus adapter driver.',
    author='David Schneider',
    author_email='david.schneider@bivab.de',
    url='https://bitbucket.org/bivab/smbus-cffi',
    py_modules=['smbus', 'util'],
    zip_safe=False,
    ext_package='smbus-cffi',
    ext_modules=[smbus.ffi.verifier.get_extension()],
    install_requires=['cffi ==0.6, ==0.7'],
    license='GPLv2',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
	'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Hardware',
    ],
)
