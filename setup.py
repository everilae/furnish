from setuptools import setup

setup(
    name="furnish",
    version="0.1",
    description="Create HTTP API clients from Python.",
    author="Ilja Everilä",
    author_email="saarni@gmail.com",
    url="https://github.com/everilae/furnish",
    packages=["furnish"],
    setup_requires=[ "pytest-runner" ],
    tests_require=[ "pytest" ],
    install_requires=[ "requests" ]
)
