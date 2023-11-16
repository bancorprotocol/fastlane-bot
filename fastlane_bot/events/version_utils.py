from packaging import version as pkg_version
from importlib.metadata import version


class VersionRequirementError(Exception):
    """
    A custom exception class for version requirement errors.

    Args:
        installed_version (str): The installed version of web3.py.
        required_version (str): The required version of web3.py.

    Raises:
        None
    """

    def __init__(self, installed_version, required_version):
        super().__init__(
            f""
            f"\n\n************** Version Requirement Error **************\n\n"
            f"Your current web3.py version is {installed_version}, which does not meet the requirement of ~= {required_version}.\n"
            f"Please upgrade your web3.py version to {required_version}.\n"
            f"We recommend using the latest requirements.txt file to install the latest versions of all "
            f"dependencies.\n\n"
            f"Run `pip install -r requirements.txt` from the project directory of the fastlane-bot repo.\n"
            f"\n\n************** Version Requirement Error **************\n\n"
            f""
        )


def check_version_requirements():
    with open("requirements.txt", "r") as f:
        requirements = f.read().splitlines()

    web3_version = [r for r in requirements if "web3" in r][0]
    required_version = web3_version.split("~=")[1]

    # Get the installed version of web3
    installed_version = version("web3")

    # Check the version and raise an exception if the requirement is not met
    if not pkg_version.parse(installed_version) <= pkg_version.parse("5.32.0"):
        raise VersionRequirementError(installed_version, required_version)
