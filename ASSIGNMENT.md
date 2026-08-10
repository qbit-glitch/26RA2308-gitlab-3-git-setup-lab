# Git Setup Lab Assignment: Kestrel-1, Day Three

**Course:** 26RA2308 Git for Software Development and Collaboration
**Based on:** Experiment 3 (Git Installation and Configuration)
**Time allowed:** 1 hour 30 minutes. **Marks:** 100

---

## The story

It is your third morning at the Kestrel-1 rover lab. **Ben** has one rule for every new teammate: nobody commits until the
workstation knows who they are, because every commit carries its author's name and email for good. **Asha** wants the
editor and the name of the first branch agreed for the whole team, **Chitra** wants short names for long commands, and
the field laptops will talk to GitHub over SSH. This lab changes the Git settings of this computer and of your account:
that is its purpose. The house rule this morning:

> **Set it, then read it back. Never trust a setting you have not looked at.**

During your shift you will check that Git is here, tell it who you are, set the team defaults, find out which file each
setting comes from, see which of two emails wins, make two shortcuts, and make an SSH key for GitHub. Every command is from
Experiment 3: `git --version`, `which git`, `git config` (with `--global`, `--local`, `--list`, `--show-origin`,
`--get-regexp`, `--unset`, `--edit`), `ssh-keygen` and `ssh -T`. You also use `nano`, and `grep` from Experiment 2.

## What you need

A terminal on Ubuntu or Debian, macOS Terminal, or Git Bash on Windows (Windows is the least tested), with `python3` (3.9 or newer),
`nano` and `git` (you used Git to clone this lab, so it is here), a **free GitHub account**, and a network that lets you
reach `github.com`. Check with `python3 --version && git --version` (on Windows Git Bash, if `python3` is not found, type
`python` instead of `python3` here and in every command). If a long output opens in a pager (a screen with `:` or `(END)`
at the bottom), press `q` to leave it.

**This lab writes to your own account:** the file `~/.gitconfig`, the file `.git/config` of the lab folder, and the folder
`~/.ssh`. If a classmate shares your login on this computer, you overwrite each other's settings: ask your instructor, and
run the grader right after you finish, on the same computer and the same account.

## Start: get the lab

Clone into your **home directory** (the folder `cd ~` takes you to), so that every "Start here" line below works.
This is not a numbered step and nothing is pasted for it.

```bash
cd ~
git clone https://github.com/qbit-glitch/26RA2308-gitlab-3-git-setup-lab.git git-setup-lab
cd git-setup-lab
cp submission/outputs.template.txt submission/outputs.txt
```

Now open your answer file in nano, press `Ctrl+E` (the cursor jumps to the end of line 1, which reads
`Name   :`), type a space and your full name, then save and leave (next section).

```bash
nano submission/outputs.txt
```

## How to edit a file with nano

You use `nano` in this lab to fill in your answer file and, in step 6.2, to edit your Git settings file.

1. `nano <file>` opens the file (a new file is created when you save).
2. The cursor starts at the **top**. Type exactly the text shown. Do **not** press `Enter` after the last line of a new or
   empty file: nano ends the file with a line break by itself. (Step 6.2 is the exception: the file already has text
   below your lines, so you press `Enter` after your last line there.)
3. Save with `Ctrl+O` and then `Enter` (that confirms the file name).
4. Leave with `Ctrl+X`.

If nano says "Save modified buffer?", press `Y` and then `Enter`. If you typed into the wrong file, press `Ctrl+X`,
then `N`, and start again. Whenever the text shows `Your Full Name`, type your own name, exactly as on line 1 of
`submission/outputs.txt`.

## Rules

1. Remember the house rule: set it, then read it back. Work in your own home folder and in your own clone.
2. Use only the commands shown.
3. Type the commands yourself, with **your own** name and **your own** email. The examples of this handout and of the
   manual (`Your Full Name`, `your-email@your-college.edu`, `yourname@dsu.edu.in`) are not accepted. The grader checks your
   pasted output against this computer, so output copied from a classmate is detected.
4. **Every task starts with a "Start here" line.** Run it first. It puts you in the lab folder whatever you did before, so
   a task you skipped never gets in the way of the next one.
5. Your listings show more settings than the examples (other files of your computer add lines): that is fine.
6. **Never paste or send your private key** (`~/.ssh/id_ed25519`, the file without `.pub`). Only the `.pub` file is public.

## How you hand in your work

1. You copied `submission/outputs.template.txt` to `submission/outputs.txt` and wrote your name at the top.
2. After **each numbered step** (they are numbered **1.1**, **1.2**, ...), paste what the terminal printed under the
   matching `--- N.M` line of `submission/outputs.txt`, replacing `(paste output here)`. Do not edit or delete the
   `=== TASK` and `--- N.M` lines. Type your answers after the colon of the `ANSWER-n :` lines (the line just below
   each `# Qn` question). Any editor is fine for `submission/outputs.txt`, for example a second terminal with nano or
   VS Code: the nano rule is for the files you create in the lab. To open `submission/outputs.txt` again from any folder
   (a second terminal starts in your home folder), type:

   ```bash
   nano ~/git-setup-lab/submission/outputs.txt
   ```

3. Run the automatic grader whenever you want to see where you stand. This command works from any folder:

   ```bash
   python3 ~/git-setup-lab/tests/grade.py
   ```

   It prints **PASS** or **FAIL** for every task, tells you exactly which check failed, and shows your score out of
   100. It reads your Git settings file and your **public** key on this computer (never your private key), so run it on the
   computer where you did the lab, right after the work. You can fix a mistake and run it again as often as you like.
4. When you are done, show the final grader output to your instructor (it is also saved in `submission/results.txt`)
   and submit `submission/outputs.txt` as instructed.

## Time plan

| Task | Time on the clock | Topic | Suggested time | Marks |
|---|---|---|---|---|
| | 09:00 | Setup: clone the lab, copy the template, write your name | 5 min | |
| 1 | 09:05 | Is Git here | 4 min | 8 |
| 2 | 09:09 | Who are you | 6 min | 14 |
| 3 | 09:15 | Defaults | 6 min | 12 |
| 4 | 09:21 | Where do the values come from | 8 min | 16 |
| 5 | 09:29 | Two emails, one folder | 8 min | 14 |
| 6 | 09:37 | Shortcuts | 10 min | 16 |
| 7 | 09:47 | SSH key | 14 min | 20 |
| | | Buffer for the grader and for fixing mistakes | 29 min | |

**Skipped a task, or running behind?** You do not lose the rest of the lab. Tasks 1, 2, 3 and 7 do not depend on each
other. Tasks 4 and 5 need the name and email of Task 2, and Task 6 needs the editor of Task 3: each of them has a
**catch-up box** that sets what you missed.

---

## Task 1: Is Git here (8 marks)

**Start here:** you have just cloned the lab, so run `cd ~/git-setup-lab`.  
**Needs:** nothing.

> **Asha:** Welcome back! First things first: is Git on this machine, which version, and where does the program live?
> Versions older than 2.28 do not know the setting for the first branch name.

```bash
cd ~/git-setup-lab
```

**1.1** Print the version of Git.

```bash
git --version
```

**1.2** Print where the program is. `which` looks the name up in the folders your shell searches.

```bash
which git
```

**Question 1.** Is the version of step 1.1 at least 2.28? Type `yes` or `no` on the `ANSWER-1` line of
`submission/outputs.txt`.

If `git --version` says that the command is not found, Git is not installed. On Ubuntu or Debian type the two commands
below; on macOS type `xcode-select --install`; on Windows install Git for Windows. Then start again at 1.1.

```text
sudo apt update
sudo apt install git -y
```

*Think (not marked):* what does `which git` tell you that `git --version` does not?

## Task 2: Who are you (14 marks)

**Start here:** `cd ~/git-setup-lab`  
**Needs:** nothing.

> **Ben:** Every commit is stamped with an author name and an email address, and the stamp can never be taken off. They
> are not passwords, only labels that Git copies into each commit. Set yours: your own name, the same as on line 1 of
> your answer file, and your own email. The second command after `&&` prints the value back, so you see it is set.

```bash
cd ~/git-setup-lab
```

**2.1** Set your name, using your own name instead of `Your Full Name` (it must not contain a double quote, a `$`, a `!`
or a backslash), and print it back.

```bash
git config --global user.name "Your Full Name" && git config --global user.name
```

**2.2** Set your email, using your own address instead of the example (the one you gave GitHub is best), and print it
back.

```bash
git config --global user.email "your-email@your-college.edu" && git config --global user.email
```

*Think (not marked):* what does `--global` mean, and which file did these two commands change?

## Task 3: Defaults (12 marks)

**Start here:** `cd ~/git-setup-lab`  
**Needs:** nothing.

> **Asha:** Three team defaults: the editor Git opens for you is `nano`, the first branch of a new repository is called
> `main`, and `git pull` merges (it does not rebase). Set each, and read each back.

```bash
cd ~/git-setup-lab
```

**3.1** Choose nano as the editor.

```bash
git config --global core.editor nano && git config --global core.editor
```

**3.2** Name the first branch of every new repository `main`.

```bash
git config --global init.defaultBranch main && git config --global init.defaultBranch
```

**3.3** Make `git pull` merge. The `|` hands the output of the first command to `grep`, which keeps only the lines
that contain `pull`.

```bash
git config --global pull.rebase false && git config --list | grep pull
```

## Task 4: Where do the values come from (16 marks)

**Start here:** `cd ~/git-setup-lab`  
**Needs:** the name and the email of Task 2. If you skipped Task 2, run this catch-up box first:

```bash
cd ~/git-setup-lab
git config --global user.name "Your Full Name"
git config --global user.email "your-email@your-college.edu"
```

> **Chitra:** Git reads settings from three places: the whole system, your account (global) and the folder you are in
> (local). `--list` shows what is in force; `--show-origin` adds the file each setting comes from.

```bash
cd ~/git-setup-lab
```

**4.1** List every setting.

```bash
git config --list
```

**Question 2.** How many lines did the listing of 4.1 print? Count the settings you pasted, one `name=value` per line
(a long setting can wrap onto a second row on a narrow window: it is still one line; a pager may hide some, so press `q`
to leave it first). Type the number on the `ANSWER-2` line.

**4.2** List every setting with its file. A line that starts with `file:` names the file.

```bash
git config --list --show-origin
```

**Question 3.** Which file does the line `user.name` come from in the listing of 4.2? Type its whole path on the
`ANSWER-3` line.

**4.3** Print the global name.

```bash
git config --global user.name
```

**4.4** Print the email that is in force in this folder (no `--global`).

```bash
git config user.email
```

*Think (not marked):* why does the listing of 4.2 show lines from more than one file?

## Task 5: Two emails, one folder (14 marks)

**Start here:** `cd ~/git-setup-lab`  
**Needs:** the name and the email of Task 2. If you skipped Task 2, run this catch-up box first:

```bash
cd ~/git-setup-lab
git config --global user.name "Your Full Name"
git config --global user.email "your-email@your-college.edu"
```

> **Ben:** Your account has one email, but this folder is going to get a different one, only here. Which of the two does
> Git use inside this folder? Find out, then take the second one away again.

```bash
cd ~/git-setup-lab
```

**5.1** Give this folder (`--local`) its own email and print the email in force.

```bash
git config --local user.email "lab-only@kestrel.example" && git config user.email
```

**Question 4.** In this folder, which email wins in 5.1: the local one or the global one? Type `local` or `global` on
the `ANSWER-4` line.

**5.2** Print your global email.

```bash
git config --global user.email
```

**5.3** List where `user.email` is set. `grep` keeps the lines that contain it.

```bash
git config --list --show-origin | grep user.email
```

**5.4** Take the local email away (`--unset`) and print the email in force again. Never leave the lab-only email in place:
your commits in this folder would carry it.

```bash
git config --local --unset user.email && git config user.email
```

## Task 6: Shortcuts (16 marks)

**Start here:** `cd ~/git-setup-lab`  
**Needs:** the editor of Task 3 (step 6.2 opens it). If you skipped Task 3, run this catch-up box first:

```bash
cd ~/git-setup-lab
git config --global core.editor nano
```

> **Asha:** Long commands waste time. An alias is a short name for a long command: `st` for `status`, `lg` for the log
> drawn as a graph. Make two with `git config`, and a third by typing into your settings file.

```bash
cd ~/git-setup-lab
```

**6.1** Make the two aliases and list every alias.

```bash
git config --global alias.st status && git config --global alias.lg "log --oneline --graph --decorate --all" && git config --global --get-regexp alias
```

**6.2** Open your global settings file in your editor. Git starts nano, because you chose it in Task 3.

```bash
git config --global --edit
```

The file already has text. The cursor is at the **top**: type these two lines (the second one starts with four spaces) and
press `Enter` after the second line, then save and leave.

```text
[alias]
    ci = commit
```

Then list every alias again: it must show three. Paste that listing under `--- 6.2`.

```bash
git config --global --get-regexp alias
```

**6.3** Use the first alias: it is `git status`.

```bash
git st
```

**6.4** Use the second alias: the history of this lab, drawn as a graph.

```bash
git lg
```

**Question 5.** What is the subject of the newest commit, the top line of the listing of 6.4? Type it on the `ANSWER-5`
line.

*Think (not marked):* what do the lines `|\` and `|/` of the graph show?

## Task 7: SSH key (20 marks)

**Start here:** `cd ~/git-setup-lab`  
**Needs:** nothing.

> **Chitra:** The field laptops talk to GitHub over SSH: a key pair, a private half that never leaves this computer and a
> public half that you give to GitHub. Make the pair, give GitHub the public half, and ask GitHub whether it knows you.

```bash
cd ~/git-setup-lab
```

**If you already have a key.** Type `ls ~/.ssh/id_ed25519*`. If it lists files, you already have a key: do not make a new
one (it would replace yours). Run 7.1 anyway: `ssh-keygen` asks `Overwrite (y/n)?`, type `n` and press `Enter`, and paste what
the terminal printed under 7.1. Then carry on with 7.2.

**7.1** Make the key pair. `mkdir -p -m 700` creates your private folder `~/.ssh`; `-f` says where to save the key; `-N ""`
means no passphrase (fine for this lab; for real work you would add one).

```bash
mkdir -p -m 700 ~/.ssh && ssh-keygen -t ed25519 -C "your-email@your-college.edu" -f ~/.ssh/id_ed25519 -N ""
```

**7.2** Print the **public** key: one line. This is the half you give away.

```bash
cat ~/.ssh/id_ed25519.pub
```

**Give the public key to GitHub** (nothing to paste for this part). In your browser: github.com, then your picture, then
Settings, then *SSH and GPG keys*, then *New SSH key*. Title: `Kestrel lab`. Key type: *Authentication Key*. Paste the line of
7.2 and save.

**7.3** Print the fingerprint, the short name of your key.

```bash
ssh-keygen -lf ~/.ssh/id_ed25519.pub
```

**Question 6.** Type the first 8 characters after `SHA256:` in the fingerprint of 7.3 on the `ANSWER-6` line (copy them
exactly: capital letters and signs count).

**7.4** Ask GitHub who you are. The first time, ssh asks `Are you sure you want to continue connecting`: type `yes` and press
`Enter`. GitHub answers `Hi <your user name>! You've successfully authenticated, but GitHub does not provide shell access.`
That sounds like an error, but it is success.

```bash
ssh -T git@github.com
```

**Question 7.** Type your GitHub user name, as GitHub greets you in 7.4, on the `ANSWER-7` line.

If the connection hangs or is refused, your network may block port 22: use `ssh -T -p 443 git@ssh.github.com`, which
works the same way.

---

## Marks

| Task | Topic | Marks |
|---|---|---|
| 1 | Is Git here | 8 |
| 2 | Who are you | 14 |
| 3 | Defaults | 12 |
| 4 | Where do the values come from | 16 |
| 5 | Two emails, one folder | 14 |
| 6 | Shortcuts | 16 |
| 7 | SSH key | 20 |

About two thirds of the marks come from the text you pasted. The rest is checked against this computer: that your Git settings
file holds your name, your email, the editor, the first branch name, the pull strategy and the aliases, that the lab folder
no longer holds the lab-only email, and that your public key is the one you pasted, with a private key that only you can read.
Run `python3 ~/git-setup-lab/tests/grade.py` to see every check.

## If something goes wrong

* **`git: command not found`.** Git is not installed: see the end of Task 1.
* **`fatal: not in a git repository` or `not a git repository`.** You are not in the lab folder. Run the task's **Start
  here** line and try again.
* **You typed the wrong name or email.** Run 2.1 or 2.2 again with the right one: `git config --global` replaces the value.
* **The lab-only email is still there.** Run 5.4 again, then `git config user.email` must print your own email.
* **`git config --global --edit` opens a strange editor** (a screen full of `~`, called vi). The editor was not set: leave with
  `Esc`, then `:q!` and `Enter`, run 3.1, and start 6.2 again.
* **At 6.2 the file looks different from what you expected.** That is fine: your computer may have other settings in it. Type
  your two lines at the very top.
* **`Overwrite (y/n)?` at 7.1.** You already have a key. Answer `n` and keep it (see the box at the start of Task 7).
* **`Permission denied (publickey)` at 7.4.** GitHub does not know your key yet, or the line was pasted incomplete. Open
  Settings, *SSH and GPG keys* on GitHub, check the key of step 7.2 is there (the whole line), and run 7.4 again.
* **`Host key verification failed` or ssh asks a yes or no question.** Answer `yes` in full (not `y`).
* **The grader says a pasted fingerprint is not this computer's key.** The outputs in `submission/outputs.txt` were not
  produced on this computer or this account. Redo the steps here and paste again.
* **You want to undo the lab afterwards.** These commands remove what the lab set (keep the key if you use it):

  ```text
  git config --global --unset alias.st
  git config --global --unset alias.lg
  git config --global --unset alias.ci
  git config --global --unset core.editor
  ```
