#!/usr/bin/env python
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
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='',
    package_dir={'': 'src'},
    packages=['flexvolume'],
    scripts=['src/vcloud-flexvolume'],
    install_requires=[
        'click',
    ],
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
)

