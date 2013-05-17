# -*- coding: utf-8 -*-
"""
zeit.api
========

The ZEIT ONLINE content API project is available at http://developer.zeit.de.
It enables you to access articles and corresponding metadata from the ZEIT
newspaper archive, as well as recent articles from ZEIT and ZEIT ONLINE.
"""

from setuptools import setup, find_packages

setup(
    name='zeit.api',
    version='0.4',
    author='Nicolas Drebenstedt',
    author_email='nicolas.drebenstedt@zeit.de',
    url='http://developer.zeit.de',
    download_url='http://github.com/ZeitOnline/content-api',
    description='ZEIT ONLINE content API - A flask and Solr based middleware',
    long_description=__doc__,
    keywords='API REST JSON Solr Newspaper News Metadata',
    license='BSD',
    platforms='any',
    test_suite='zeit.api.tests',
    zip_safe=False,
    include_package_data=True,
    namespace_packages=['zeit',],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
    'setuptools',
    'flask',
    'lxml'
    ],
    entry_points="""
    [console_scripts]
    api = zeit.api.application:run_local_api
    doc = zeit.api.application:run_local_doc
    """
)