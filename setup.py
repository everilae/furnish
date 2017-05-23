from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="furnish",
    version="0.1.0",
    description="Create HTTP API clients from Python.",
    long_description=long_description,
    author="Ilja Everilä",
    author_email="saarni@gmail.com",
    url="https://github.com/everilae/furnish",
    download_url="https://github.com/everilae/furnish/archive/v0.1.0.tar.gz",
    packages=["furnish"],
    setup_requires=[ "pytest-runner" ],
    tests_require=[ "pytest" ],
    install_requires=[ "requests" ]
)
