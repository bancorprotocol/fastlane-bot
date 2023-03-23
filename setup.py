import re

from setuptools import find_packages, setup

with open("fastlane_bot/__init__.py") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    )[1]

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

extras_require = {}
extras_require["complete"] = sorted(set(sum(extras_require.values(), [])))

setup(
    name="fastlane_bot",
    version=version,
    author="Bancor Network",
    author_email="mike@bancor.network",
    description="""
                    Fast Lane, an open-source arbitrage protocol, allows any user to perform arbitrage between Bancor ecosystem protocols and external exchanges and redirect arbitrage profits back to the protocol.
                """,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bancorprotocol/fastlane",
    install_requires=open("requirements.txt").readlines(),
    extras_require=extras_require,
    tests_require=['pytest==6.2.5', 'pytest-mock==3.10.0'],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
)
