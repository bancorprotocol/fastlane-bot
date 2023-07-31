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
import subprocess
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




def run_command(mode):
    import os
    import time
    import subprocess

    try:
        main_script_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, 'main.py'))
        cmd = [
            "python",
            main_script_path,
            f"--arb_mode={mode}",
            "--default_min_profit_bnt=60",
            "--limit_bancor3_flashloan_tokens=True",
            "--use_cached_events=True",
            "--logging_path=fastlane_bot/data/",
            "--timeout=45"
        ]
    except subprocess.CalledProcessError:
        main_script_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir,  'main.py'))
        cmd = [
            "python",
            main_script_path,
            f"--arb_mode={mode}",
            "--default_min_profit_bnt=60",
            "--limit_bancor3_flashloan_tokens=True",
            "--use_cached_events=True",
            "--logging_path=fastlane_bot/data/",
            "--timeout=45"
        ]
        subprocess.Popen(cmd)

    start_time = time.time()
    expected_log_line = "limiting flashloan_tokens to ["
    result = subprocess.run(cmd, text=True, capture_output=True, check=True)

    found = expected_log_line in result.stderr
    if not found:
        pytest.fail("Expected log line was not found within 1 minute")  # If we reach this point, the test has failed



# ------------------------------------------------------------
# Test      903
# File      test_903_FlashloanTokens.py
# Segment   Test Flashloan Tokens b3_two_hop
# ------------------------------------------------------------
# def test_test_flashloan_tokens_b3_two_hop():
# # ------------------------------------------------------------
#
run_command("b3_two_hop")