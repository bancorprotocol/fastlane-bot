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
            f"Your current web3.py version is {installed_version}, which does not meet the requirement of >= {required_version}.\n"
            f"Please upgrade your web3.py version to {required_version} or higher.\n"
            f"We recommend using the latest requirements.txt file to install the latest versions of all "
            f"dependencies.\n"
            f"To do this, run `pip install -r requirements.txt` from the root directory of the fastlane-bot repo.\n"
            f"\n\n************** Version Requirement Error **************\n\n"
            f""
        )


def check_version_requirements(required_version="6.11.0", package_name="web3"):
    """
    Checks the version requirements for the web3 library.

    Args:
        required_version (str, optional): The minimum required version of web3. Defaults to "6.11.0".
        package_name (str, optional): The name of the package to check. Defaults to "web3".

    Raises:
        VersionRequirementError: If the installed version of web3 does not meet the minimum required version.
    """
    # Get the installed version of web3
    installed_version = version(package_name)

    # Check the version and raise an exception if the requirement is not met
    if not pkg_version.parse("6.11.0") <= pkg_version.parse(installed_version):
        raise VersionRequirementError(installed_version, required_version)
