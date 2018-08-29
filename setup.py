from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
namespace = {}

setup(
    name='brocrypt',
    version='0.0.1',
    description="An easyish procedure for storing secrets with others",
    author='jamesob',
    author_email='jamesob@chaincode.com',
    py_modules=['brocrypt'],
    install_requires=('cryptography',),
    entry_points={
        'console_scripts': [
            'brocrypt = brocrypt:main',
        ],
    },
)
