from setuptools import find_packages, setup

setup(
    name="sms3",
    packages=find_packages(),
    install_requires=['pyserial'],
    version="0.0.2",
    description="A library for sending TXT message",
    author="yanganto",
    author_email="yanganto@gmail.com",
    url="https://github.com/yanganto/sms3",
    keywords=["sms"],
    download_url="",
    license="MIT",
    include_package_data=False,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Communications :: Telephony"
    ],
    long_description="""\
SMS3 - a library for sending SMS
---
This package is for Python 3
** if your are using python2, please use sms package.
"""
)
