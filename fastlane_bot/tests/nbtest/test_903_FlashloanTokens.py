# ------------------------------------------------------------
# Auto generated test file `test_903_FlashloanTokens.py`
# ------------------------------------------------------------
# source file   = NBTest_903_FlashloanTokens.py
# test id       = 903
# test comment  = FlashloanTokens
# ------------------------------------------------------------



"""
This module contains the tests which ensure the the flashloan_tokens parameter is respected when using the b3_two_hop and bancor_v3 arb modes.
"""
from fastlane_bot import Bot
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3, SushiswapV2, CarbonV1, BancorV3
import subprocess, os, sys
import pytest
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SushiswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
from fastlane_bot.testing import *
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)




def find_main_py():
    # Start at the directory of the current script
    cwd = os.path.abspath(os.path.join(os.getcwd()))
    
    with open("log.txt", "w") as f:
        f.write(f"Searching for main.py in {cwd}")
                
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
       
       
def run_command(mode):
    
    # Find the correct path to main.py
    main_script_path = find_main_py()
    print(f"Found main.py in {main_script_path}")
    main_script_path = main_script_path + "/main.py"

    # Run the command
    cmd = [
        "python",
        main_script_path,
        f"--arb_mode={mode}",
        "--default_min_profit_bnt=60",
        "--limit_bancor3_flashloan_tokens=True",
        "--use_cached_events=True",
        "--logging_path=fastlane_bot/data/",
        "--timeout=70"
    ]
    subprocess.Popen(cmd)
        
    # Wait for the expected log line to appear
    expected_log_line = "limiting flashloan_tokens to ["
    found = False
    result = subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=120)

    # Check if the expected log line is in the output
    if expected_log_line in result.stderr:
        found = True

    if not found:
        pytest.fail("Expected log line was not found within 1 minute")  # If we reach this point, the test has failed




# ------------------------------------------------------------
# Test      903
# File      test_903_FlashloanTokens.py
# Segment   Test Flashloan Tokens b3_two_hop
# ------------------------------------------------------------
def test_test_flashloan_tokens_b3_two_hop():
# ------------------------------------------------------------
    
    run_command("b3_two_hop")