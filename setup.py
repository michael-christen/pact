from setuptools import find_packages
from setuptools import setup

import pact_request


PACKAGE_NAME = 'pact_request'


setup(
    name=PACKAGE_NAME,
    version=pact_request.__version__,
    description='Python pact implementation',
    author='Michael Christen',
    url='https://github.com/michael-christen/pact-request',
    license='MIT',
    packages=find_packages(exclude=["*.tests"]),
    install_requires=[
    ],
    package_data={},
    data_files=[],
    entry_points={
    },
    test_suite="{}.tests".format(PACKAGE_NAME),
)
