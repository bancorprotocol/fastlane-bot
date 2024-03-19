# NBTest Data

All data referred to by NBTest notebooks is stored in this directory. It is copied into the respective directory in the test area by the `run_tests` script. Currently the data will be accessed differently in the notebooks and in the actual tests.

- **Notebooks**. In the notebooks the data can be accessed via a relative path `_data\mydata.csv`.

- **Tests**. In the actual tests the data must be imported via the relative path `fastlane_bot/tests/nbtest/_data/mydata.csv`


Example

    try:
        with open("_data/mydata.csv", "r") as f:
            data = f.read()
    except:
        with open("fastlane_bot/tests/nbtest/_data/mydata.csv", "r") as f:
            data = f.read()

    