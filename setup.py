from setuptools import setup

setup(
    name='tpn',
    version='0.1',
    py_modules=['tpn'],
    install_requires=['Click'],
    entry_points={
        'console_scripts': [
            'tpn = tpn:cli',
        ]
    }
)
