---
name: Running and Changing Scripts
title: NODEYEZ Development Environment
layout: default
---

# Test a Simple Script

From the scripts folder, select the ipaddress.py file to open in an editor.

* Using the IDE

Start running the script by the shortcut (F5) or choosing Start Debugging from the Run menu.

If there are no errors, you will see some startup text in the terminal pane, followed by `sleeping for 120 seconds`.

You can stop debugging via the shortcut (SHIFT+F5) or from the Run menu.

* Using the Terminal

Activate the python virtual environment if it isn't already active. You can rely on the prompt prefixed with the environment name (nodeyez) to know its active or not.
```shell
source ~/.pyenv/nodeyez/bin/activate
```

From the terminal, you won't having debugging support, and instead just run the script directly
```shell
cd ~/nodeyez/scripts

python ./ipaddress.py
```

Press (CTRL+C) to stop the script execution.

Look for an image generated in the [../imageoutput](../imageoutput) folder.

In the footer of most images generated by Nodeyez is an "as of" datestamp.  This can help you be certain whether you are reviewing the latest changes.

# Make Changes and Test

Create a temporary branch to test your changes. 

Using the Terminal
```shell
git checkout -b test1
```

If this is your first time setting up git, you'll also want to set your user email and name
```shell
git config --global user.email "you@example.com"

git config --global user.name "Your Name"
```

Verify that the current branch name is depicted in the lower left corner of Visual Studio Code

Try making a change to the IP Address script. Find the line that renders the current ip list, and change its font size.

In this line below, vicarioustext is one of the scripts with assorted helper methods to render text into an image canvas.  The third argument represents the font size, shown here as 36.  
```python
vicarioustext.drawcenteredtext(draw, str(currentip), 36, int(width/2), int(height/2), colorTextFG, True)
```
Make a change, save the file, and then start running the script via the shortcut (F5) or from choosing Start Debugging from the Run menu.

Stop the script and review the output generated in the imageoutput folder as before.  You should see the as of footer line changed to a more recent time, as well as visual changes to the font size based on your alterations.

# Publish Changes

Once you are satisfied with any changes you've made, you can publish them to a branch in your own repository, and then begin a pull request.

## Commit your Changes Locally

Before going much further, lets commit your changes to your local branch.

* Using the IDE

In Visual Studio Code, switch to the Source Control view (CTRL+SHIFT+G G). If the Source Control subpanel is not displayed, toggle it by clicking the three dots in the upper right corner of the Source Control pane and choosing that menu option. Expand the Source Control subpanel and you'll see the list of files you've added, modified, or deleted.

At the top of the Source Control panel you can provide a comment for your changes, and click Commit.

* Using the Terminal

View the status, reporting branch, working vs staged changes
```shell
cd ~/nodeyez

git status
```

Stage them for committing
```shell
git add .
```
The '.' stages all files from your current working directory downward

Commit with a message
```shell
git commit -m "Brief description of your changes"
```

## Creating your Fork

Sign in to Github, creating a new account if you do not already have one.  If you are creating a new account, you should also [setup an SSH key](https://github.com/settings/keys) from the computer you are working on.

Navigate to the project at [https://github.com/vicariousdrama/nodeyez](https://github.com/vicariousdrama/nodeyez).  

Towards the upper right corner, you can click on the Fork button.  This will start a fork of the project under your username.  Review the settings making adjustments based on your preferences and proceed with Create Fork.

## Add a Remote

With your new fork created in Github, click the green Code dropdown button, and then select SSH.  Copy the value. It should look something like `git@github.com:Username/nodeyez.git`

View your remotes
```shell
git remote -v
```

Add a new remote
```shell
git remote add myfork git@github.com:Username/nodeyez.git
```

## Pushing to the Remote

You can use this command to push your branch to your desired forked repository, replacing `myfork` with whatever you named your remote and `test1` with your branch name.
```shell
git push --set-upstream myfork test1
```

## Initiating a Pull Request

From within the GitHub interface, you can view your branch, and create a pull request. By default, Github will open a pull request against the base repository from which yours is forked, but you can change that as desired.

---

[Home](../) | [Back to Python and IDE Setup]({% link _developer/1basicsetup.md %}) | [Continue to Regtest]({% link _developer/3regtest.md %})