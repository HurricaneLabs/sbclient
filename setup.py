from setuptools import setup


VERSION = "1.0.1"


with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name="sbclient",
    version=VERSION,
    author="Steve McMaster",
    author_email="mcmaster@hurricanelabs.com",
    py_modules=["sbclient"],
    description="sbclient - CLI Splunkbase client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "click",
        "python-dateutil",
        "defusedxml",
        "lxml",
        "requests",
        "six>=1.12.0"
    ],
    entry_points={
        "console_scripts": [
            "sbclient = sbclient:cli",
        ]
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
    ],
    bugtrack_url="https://github.com/HurricaneLabs/sbclient/issues",
)
