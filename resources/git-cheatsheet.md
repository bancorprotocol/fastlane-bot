# Git Cheat Sheet

_basics of what you **must** know to work with this repo_

## `gitconfig` file

The gitconfig file (`~/.gitconfig` on Mac, `TODO` on Windows) is a file that contains your git configuration. It is a text file that you can edit with any text editor. It is a hidden file, so you will need to enable hidden files in your file explorer to see it.

I have shared my gitconfig file for you to review in Telegram. Key entries in the alias section are.

    [alias]

        s = status
        rl = reflog
        rsh   = reset --hard

        l = log --pretty=oneline  --graph --abbrev-commit -10 --decorate
        ll = log --pretty=oneline  --graph --abbrev-commit --decorate
        fa = fetch --all -p

        m = merge --ff-only
        plff = pull --ff-only
        plrb = pull --rebase
        t = tag

        co = checkout
        cob = checkout -b

        cp = cherry-pick -x
        cpa = cherry-pick --abort
        cps = cherry-pick --skip
        cpc = cherry-pick --continue

        rbi = rebase -i
        rba = rebase --abort
        rbs = rebase --skip
        rbc = rebase --continue


## Common commands

- `git s` (or `git status`) shows the current status of the repo. 
- `git ll` (or `git l`) shows the commit history of the repo in a reasonable format.
- `git fa` (or `git fetch --all -p`) fetches all the branches from the remote repo and prunes any branches that have been deleted on the remote.
- `git plff` (or `git pull --ff-only`) pulls the current branch from the remote repo and fast forwards the local branch to the remote branch; if fails use either `git rsh` or `git plrb` to recover.
- `git rsh xxx` (or `git reset --hard xxx`) resets the current branch to `xxx`
- `git co xxx` (or `git checkout xxx`) checks out branch `xxx`
- `git cob xxx` (or `git checkout -b xxx`) creates a new branch `xxx` and checks it out
- `git t xxx` (or `git tag xxx`) tags the current commit with tag `xxx`

## Workflows

Before you start: generally `git tag branch_date` (eg `git tag dev_20230428` is a good idea if you want to make sure you don't lose your work)

### Updating a joint branch from the remote repo

- single arrow down --> you are good to go from the GUI
- single arrow up --> **DONT** unless you want to push
- double arrow --> **DANGER ZONE** must use command line

First try

    git plff

If that succeeds, you are good. If that fails, you have two choices:

1. `git plrb` to rebase your branch on top of the remote branch, possibly leading to merge conflicts (`git rba` to back out of this)
2. `git rsh origin/branch` to reset your branch to the remote branch, losing any work you have done since the last push

### Creating a new topic branch

First you make sure you have the latest main (or whatever you want to base it on). Then you create a new branch and check it out.
    
    git cob newbranch
    git touch BRANCH_BRANCHNAME

Check in the file `BRANCH_BRANCHNAME` in a single commit using the GUI.

### Rebasing your branches on top of the joint branch

Once you have a new version of the joint branch, you will want to rebase your branches on top of it. If the joint branch is `main`, this is done in the simple case with

    git rebase main

You may need to deal with merge conflicts. If too hard, back out with `git rba`.

In case you know where your branch diverges from the joint branch (the commit _below_ `BRANCH_XXX`) you can use the two-argument form of rebase:

    git rebase last_commit_before_branch_xxx --onto main

Once you are satisfied with the rebase, you can push your branch to the remote repo with the command below. Note the `-f` (`--force`) flag is required if the rebase did something.

    git push -f origin branch

### Merging you branch into the joint branch

(1) make sure you have the latest version of the joint branch. (2) In the branch you want to merge, use the GUI to **move the `create BRANCH_MYBRANCH` commit to the very top (last commit). (3) rebase your branch onto the joint branch (see above).

The run the following commands

    git checkout main
    git merge --ff-only mybranch
    git reset --hard HEAD^
    git ll
    ./run_tests
    git push

The first of those commands checks out the main branch. The second one merges your branch into the main branch. The third one resets the main branch to the commit before the BRANCH_MYBRANCH commit. The fourth one shows you the commit history. Make sure it is as you expected. The next runs the tests. Make sure they pass. Finally push.