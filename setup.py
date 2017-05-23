from setuptools import setup

setup(
    name="furnish",
    version="0.1",
    description="Create HTTP API clients from Python.",
    author="Ilja Everilä",
    author_email="saarni@gmail.com",
    url="https://github.com/everilae/furnish",
    download_url="https://github.com/everilae/furnish/archive/v0.1.tar.gz",
    packages=["furnish"],
    setup_requires=[ "pytest-runner" ],
    tests_require=[ "pytest" ],
    install_requires=[ "requests" ]
)
