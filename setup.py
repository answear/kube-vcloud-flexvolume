#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='kube-vcloud-flexvolume',
    description='VMware vCloud Director flexVolume driver for Kubernetes ',
    url='git@github.com:answear/kube-vcloud-flexvolume.git',
    author='Piotr Mazurkiewicz',
    author_email='piotr.mazurkiewicz@wearco.pl',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5'
    ],
    keywords='',
    package_dir={'': 'src'},
    packages=['flexvolume','vcloud'],
    scripts=['src/vcloud-flexvolume'],
    install_requires=[
        'click',
        'bitmath',
        'etcd3autodiscover>=1.0.1'
    ],
    extras_require={
        ':python_version < "3.6"': [
            'pyvcloud==20.0.4'
        ],
        ':python_version >= "3.6"': [
            'pyvcloud==20.0.3'
        ]
    },
    dependency_links=[
        'git+https://github.com/answear/pyvcloud@20.0.4#egg=pyvcloud-20.0.4',
        'git+https://github.com/answear/python-etcd3autodiscover@1.0.1#egg=etcd3autodiscover-1.0.1'
    ],
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
)
