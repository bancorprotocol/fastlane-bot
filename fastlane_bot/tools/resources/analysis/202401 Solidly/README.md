# Solidly

_January 2024_

The main notebook here is `202401 Solidly` which contains the analysis regarding the Solidly analysis we performed in January 2023.

The other notebooks are in relation to the `invariants` library that we developed to perform the analysis


## Running the notebooks

In order to run the notebooks, run

    ln -s ../../../fastlane_bot/tools/invariants invariants
    ln -s ../../../fastlane_bot/testing.py testing.py
    echo invariants >>.gitignore
    echo testing.py >>.gitignore

to link the library that is now part of fastlane_bot