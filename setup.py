"""
A simple JSON API web framework based on Flask

Document: https://github.com/ncuhome/fighting
"""
from setuptools import setup
from os.path import join, dirname

with open(join(dirname(__file__), 'requires.txt'), 'r') as f:
    install_requires = f.read().split("\n")

setup(
    name="fighting",
    version="0.1.0",
    description="A simple JSON API web framework based on Flask",
    long_description=__doc__,
    author="guyskk",
    author_email='guyskk@qq.com',
    url="https://github.com/ncuhome/fighting",
    license="MIT",
    packages=["fighting"],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    classifiers=[
        'Framework :: Flask',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
