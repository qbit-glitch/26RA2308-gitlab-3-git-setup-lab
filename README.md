# Git Setup Lab: Kestrel-1, Day Three

Hands-on lab for Experiment 3 (Git Installation and Configuration) of 26RA2308, Git for Software Development and
Collaboration. It is the third morning at the Kestrel-1 rover lab and Ben will not let anyone commit until the workstation
knows who they are: check that Git is here with `git --version` and `which git`, set your name and email, choose the editor
and the first branch name, read where each value comes from with `git config --list --show-origin`, see which of two emails
wins, make aliases, and make an SSH key for GitHub with `ssh-keygen`.

This lab changes the Git settings of your own account (`~/.gitconfig` and `~/.ssh`), so do it on your own login.

## Get started

```bash
cd ~
git clone https://github.com/qbit-glitch/26RA2308-gitlab-3-git-setup-lab.git git-setup-lab
cd git-setup-lab
cp submission/outputs.template.txt submission/outputs.txt
```

1. Read `ASSIGNMENT.md` (the handout) and do the seven tasks in order.
2. Paste each command's output into `submission/outputs.txt`, under the matching `--- N.M` line.
3. Check your work any time with:

```bash
python3 ~/git-setup-lab/tests/grade.py
```

The grader only reads files (your Git settings file and your public key): it never runs anything you wrote and never reads
your private key. Needs `python3`, `nano`, `git` and a GitHub account.
