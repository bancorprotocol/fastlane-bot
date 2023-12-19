# ------------------------------------------------------------
# Auto generated test file `test_048_RespectFlashloanTokensClickParam.py`
# ------------------------------------------------------------
# source file   = NBTest_048_RespectFlashloanTokensClickParam.py
# test id       = 048
# test comment  = RespectFlashloanTokensClickParam
# ------------------------------------------------------------



"""
This module contains the tests which ensure that the flashloan tokens click parameters are respected.
"""
from fastlane_bot import Bot
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3,  CarbonV1, BancorV3
import subprocess, os, sys
import pytest
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
from fastlane_bot.testing import *
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)




def find_main_py():
    # Start at the directory of the current script
    cwd = os.path.abspath(os.path.join(os.getcwd()))
    
    print(f"Searching for main.py in {cwd}")
    while True:
        # Check if main.py exists in the current directory
        if "main.py" in os.listdir(cwd):
            return cwd  # Found the directory containing main.py
        else:
            # If not, go up one directory
            new_cwd = os.path.dirname(cwd)

            # If we're already at the root directory, stop searching
            if new_cwd == cwd:
                raise FileNotFoundError("Could not find main.py in any parent directory")

            cwd = new_cwd
       
       
def run_command(arb_mode, expected_log_line):
    
    # Find the correct path to main.py
    main_script_path = find_main_py()
    print(f"Found main.py in {main_script_path}")
    main_script_path = main_script_path + "/main.py"

    # Run the command
    cmd = [
        "python",
        main_script_path,
        f"--arb_mode={arb_mode}",
        "--default_min_profit_bnt=60",
        "--limit_bancor3_flashloan_tokens=False",
        "--use_cached_events=True",
        "--logging_path=fastlane_bot/data/",
        "--timeout=1",
        "--loglevel=DEBUG",
        "--flashloan_tokens=BNT-FF1C,ETH-EEeE,ETH2X-FLI-USD",
    ]
    subprocess.Popen(cmd)
        
    # Wait for the expected log line to appear
    found = False
    result = subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=7)

    # Check if the expected log line is in the output
    if expected_log_line in result.stderr or expected_log_line in result.stdout:
        found = True

    if not found:
        pytest.fail("Expected log line was not found within 1 minute")  # If we reach this point, the test has failed




# ------------------------------------------------------------
# Test      048
# File      test_048_RespectFlashloanTokensClickParam.py
# Segment   Test flashloan_tokens is Respected
# ------------------------------------------------------------
def test_test_flashloan_tokens_is_respected():
# ------------------------------------------------------------
    
    expected_log_line = "Flashloan tokens are set as: ['BNT-FF1C', 'ETH-EEeE', 'ETH2X_FLI-USD']"
    arb_mode = "multi"
    run_command(arb_mode=arb_mode, expected_log_line=expected_log_line)