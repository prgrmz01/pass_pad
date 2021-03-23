####
#####!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='pass_pad',
    version='0.0.2.4',
    author='prgrmz07',
    author_email='prgrmz07@163.com',
    url='https://blog.csdn.net/hfcaoguilin',
    description=u'密码本',
    packages=['pass_pad'],
    install_requires=[
        'pycryptodomex>=3.10.1',
        'pandas>=1.1.3',
        'jupyterlab-pygments>=0.1.2',
        'prompt-toolkit>=3.0.8',
    ],
    entry_points={
        'console_scripts': [
            'pass_pad=pass_pad:main',
            # 'pass_pad_test=pass_pad:test'
        ]
    }
)