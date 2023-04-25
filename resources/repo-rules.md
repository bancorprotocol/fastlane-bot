# Repo Rules [whilst repo is private]

1. The main branch is `main`. This branch is _forward-only_, ie no merge-commits, and there is a strict no-rewrite rule enforced on the server. If you push code erroneously you must correct this using `git revert`.

2. In order to be able to push to main, you need to `git rebase` your code on top of the latest main. The command for this is `git checkout main` then `git pull` to get the latest main, then `git checkout mybranch` and `git rebase <lastmain> --onto main`. Here `<lastmain>` is the last commit of main below your pre-rebase branch. **If you have conflicts you must resolve them before you can push. You must not delete anyone else's functional code in this process, and it is in your interest to push things to main early to avoid merge conflicts associated with long-running topic branches.**

3. Unit tests will be prepared using the `NBTest` framework, like it is done [in the `Carbon Simulator` repo][nbt]. The key features of this framework are

    1. All tests live in Jupyter notebooks, and typically you will create those Jupyter notebooks as you go along creating your code, so by the time your code is finished your tests will be finished too.

    2. In the notebooks, Heading 2 sections (`## Heading2`) indicate an individual test. The test name is the text of the heading (meaning you should only use alphanumeric characters and spaces in the heading text). Note: variables that you define in one test will **not** be available in another test. However, all variables defined _before_ the first Heading 2 section will be available in all tests.

    3. Test notebooks **must** print out all the version numbers of the components they are using, so that it can be asserted that the tests are in line with the latest available versions [see below].

    4. The NBTest framework relies on [`JupyText`][jt] as it picks up the tests from the `lightscript` version of the notebook; you must install JupyText on your system; if you usually run test notebooks in VSCode you may have to open and save them in the standard Jupyter Lab environment before you commit.

4. All objects tested have a `__VERSION__` and a `__DATE__` (spelled thusly, in capital letters). It is recommended to set those variables at the top of the file in which they are defined, and then just include them into the classes using `__VERSION__ = __VERSION__` immediately after the end of the docstring

    1. Every day you touch an object, you **must** update its version and date, regardless how small the change, and re-run and re-commit the associated NBTest notebook. 

    2. Whenever you push to main, the top-most commit changing an object must also change its version number, ie you cannot amend objects on main without changing their version number.
    
    3. If you want you _can_ merge multiple version updates into one, effectively skipping version numbers. Of course this only works before you have pushed to main, as main cannot be rewritten.

5. There will be **no use of Black or any other automated formatters on the repo level**. If you like to run Black locally you are free to do so on the modules that are your responsibility. However, **Black changes must be committed separately from functional changes**, clearly marked as such in the commit message, and Black changes must never be merged with functional changes.

6. **Pull requests**: in my personal view, pull requests are over engineered for a small number of core contributors: you should just merge your own code into main and take responsibility for it. However -- if you prefer the github-enabled pull request process then I am not against it. **In any case it is up to the person making the pull request to ensure that it is being taken care of in a sufficiently timely manner.**

_Note: once the repo is published we may need to introduce and intermediate branch called `beta` or `devmain` to which the above rules will apply, and that is periodically merged into the actual `main`. Whether or not you want to allow rewrites before the merge is up to the consensus of the contributors, keeping in mind that rewritting devmain will require (slightly) more git skills as the two-argument form of `git rebase` will be required._ 

[jt]:https://jupytext.readthedocs.io/en/latest/
[nbt]:https://github.com/bancorprotocol/carbon-simulator/tree/main/resources/NBTest