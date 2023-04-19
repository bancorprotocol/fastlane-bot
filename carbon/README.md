This README file provides instructions on how to set up the required symlink from the current repository to the `arbbot` branch of the `carbon-simulator` repository. This is necessary for the correct functioning of the codebase during development.

Optimizer Code 
-------------

- `cpc.py`: data structures that hold constant product curves [in Carbon]
- `simplepair.py`: simple data structure for token pairs [in Carbon]
- `tokenscale.py`: holds information of the approximate scale (ie price) of a token [in Carbon]
- `arbgraphs.py`: converts constant product curves are trades thereof into graph structures, and allows analysing those graphs
- `optimizer.py`: the convex optimization code


Prerequisites
-------------

Before you create the symlink, you need to have the `carbon-simulator` repository cloned on your machine. If you haven't already done so, follow the steps below to clone the repository using the GitHub Desktop application:

1.  Open the GitHub Desktop application.
2.  Click on the `File` menu and select `Clone repository...`.
3.  In the `Clone a repository` window, switch to the `URL` tab.
4.  Enter the repository URL `https://github.com/your-username/carbon-simulator.git` (replace `your-username` with your GitHub username) in the `Repository URL` field.
5.  Choose a local path where you want to clone the repository on your machine.
6.  Click `Clone` to start cloning the repository.

Symlink Creation
----------------

Now that you have the `carbon-simulator` repository cloned, you need to create a symlink from the current directory to the `carbon-simulator/carbon/tools` directory. The process to create the symlink is different for Windows and Mac/Linux users.

### For Windows Users

1.  Open the Command Prompt with administrative privileges by right-clicking on the Start button and selecting `Windows PowerShell (Admin)` or `Command Prompt (Admin)` from the context menu.

2.  Change the directory to the location of the current repository using the `cd` command:

    bashCopy code

    `cd C:\path\to\current-repo`

3.  Create a symlink to the `carbon-simulator/carbon/tools` directory using the `mklink` command:

    mathematicaCopy code

    `mklink /D symlink_name C:\path\to\carbon-simulator\carbon\tools`

    Replace `symlink_name` with the desired name for your symlink.

### For Mac/Linux Users

1.  Open the Terminal application.

2.  Change the directory to the location of the current repository using the `cd` command:

    bashCopy code

    `cd /path/to/current-repo`

3.  Create a symlink to the `carbon-simulator/carbon/tools` directory using the `ln` command:

    bashCopy code

    `ln -s /path/to/carbon-simulator/carbon/tools symlink_name`

    Replace `symlink_name` with the desired name for your symlink.

Now you have successfully created a symlink from the current repository to the `arbbot` branch of the `carbon-simulator` repository. You should now be able to use the codebase during development without any issues.