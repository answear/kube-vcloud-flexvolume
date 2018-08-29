#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='kube-vcloud-flexvolume',
    description='VMware vCloud Director flexVolume driver for Kubernetes ',
    url='git@github.com:sysoperator/kube-vcloud-flexvolume.git',
    author='Piotr Mazurkiewicz',
    author_email='piotr.mazurkiewicz@sysoperator.pl',
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
        'pyvcloud==19.3.0',
        'pyudev',
        'bitmath',
        'etcd3autodiscover==0.1.0'
    ],
    dependency_links=[
        'git+https://github.com/sysoperator/python-etcd3autodiscover@0.1.0#egg=etcd3autodiscover-0.1.0'
    ],
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
)

