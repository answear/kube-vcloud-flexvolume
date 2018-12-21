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
        'pyvcloud>=19.3.0,<19.4',
        'bitmath',
        'etcd3autodiscover>=0.2.0'
    ],
    dependency_links=[
        'git+https://github.com/answear/python-etcd3autodiscover@1.0.0#egg=etcd3autodiscover-1.0.0'
    ],
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
)

