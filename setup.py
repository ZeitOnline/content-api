from setuptools import setup, find_packages

name = 'zeit.api'
setup(
    name = name,
    version = '0.4',
    author = 'Nicolas Drebenstedt',
    author_email = 'nicolas.drebenstedt@zeit.de',
    url = 'http://developer.zeit.de',
    package_dir = {'': 'src'},
    packages = find_packages('src'),
    namespace_packages = ['zeit',],
    include_package_data = True,
    install_requires = [
	'setuptools',
	'flask',
    'lxml'
	],
    zip_safe = False,
    entry_points = """
	[console_scripts]
	api = zeit.api.application:run_local_api
    doc = zeit.api.application:run_local_doc
    """,
    )