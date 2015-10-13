# -*- coding: utf-8  -*-
#
# Released under the terms of the MIT License. See LICENSE for details.

import sys
import os
import requests
import git
import argparse
from colorama import init as color_init, Fore, Style
from . import __version__
from .config import URL, POSTFIX, PRIVATE_TOKEN
from requests import exceptions as rest_exceptions

# Color definitions
BOLD = Style.BRIGHT
BLUE = Fore.BLUE + BOLD
GREEN = Fore.GREEN + BOLD
RED = Fore.RED + BOLD
YELLOW = Fore.YELLOW + BOLD
RESET = Style.RESET_ALL
ERROR = RED + "Error: " + RESET
LINE = "======================================="

API_TIMEOUT = 10

def _getCurrentFolder():
    """Returns list of the folders of the current working directory"""

    print('Current working directory is ' + GREEN + os.getcwd())
    return os.getcwd()


def _fetchRemotes(remotes):
    """Fetch a list of remotes, displaying progress info along the way."""
    def _get_name(ref):
        """Return the local name of a remote or tag reference."""
        return ref.remote_head if isinstance(ref, git.RemoteReference) else ref.name

    info = [("NEW_HEAD", "new branch", "new branches"),
            ("NEW_TAG", "new tag", "new tags"),
            ("FAST_FORWARD", "branch update", "branch updates")]
    up_to_date = BLUE + "Up to date" + RESET

    for remote in remotes:
        print(GREEN + "Fetching " + remote.name)

        if not remote.config_reader.has_option("fetch"):
            print(YELLOW + "Skipped:" + RESET + " No configured refspec.")
            continue

        try:
            results = remote.fetch()
        except git.exc.GitCommandError as err:
            msg = err.command[0].replace("Error when fetching: ", "")
            if not msg.endswith("."):
                msg += "."
            print(ERROR + msg)
            return
        except AssertionError:  # Seems to be the result of a bug in GitPython
            # This happens when git initiates an auto-gc during fetch:
            print(ERROR + "Something went wrong in GitPython but the fetch might have been successful.")
            return
        rlist = []
        for attr, singular, plural in info:
            names = [_get_name(res.ref)
                     for res in results if res.flags & getattr(res, attr)]
            if names:
                desc = singular if len(names) == 1 else plural
                colored = GREEN + desc + RESET
                rlist.append("{0} ({1})".format(colored, ", ".join(names)))
        print((", ".join(rlist) if rlist else up_to_date) + ".")


def _updateBranch(repo, branch, is_active=False):
    """Update a single branch."""

    print(GREEN + "Updating " + branch.name)

    upstream = branch.tracking_branch()
    if not upstream:
        print(YELLOW + "Skipped:" + RESET + " No upstream is tracked.")
        return

    try:
        branch.commit
    except ValueError:
        print(YELLOW + "Skipped:" + RESET + " Branch has no revisions.")
        return
    try:
        upstream.commit
    except ValueError:
        print(YELLOW + "Skipped:" + RESET + " Upstream does not exist.")
        return

    base = repo.git.merge_base(branch.commit, upstream.commit)
    if repo.commit(base) == upstream.commit:
        print(BLUE + "Up to date")
        return

    if is_active:
        try:
            repo.git.merge(upstream.name, ff_only=True)
            print(GREEN + "Done")

        except git.exc.GitCommandError as err:
            msg = err.stderr
            if "local changes" in msg and "would be overwritten" in msg:
                print(YELLOW + "Skipped:" + RESET + " Uncommitted changes.")
            else:
                print(YELLOW + "Skipped:" + RESET + " Not possible to fast-forward.")
    else:
        status = repo.git.merge_base(
            branch.commit, upstream.commit, is_ancestor=True,
            with_extended_output=True, with_exceptions=False)[0]
        if status != 0:
            print(YELLOW + "Skipped:" + RESET + " Not possible to fast-forward.")
        else:
            repo.git.branch(branch.name, upstream.name, force=True)
            print(GREEN + "Done")


def _updateExistingRepo(path):
    """
    Updates repository
    :param path: Repo Path
    :return: Boolean
    """
    try:
        repo = git.Repo(path)
    except git.exc.NoSuchPathError:
        print(ERROR + path + " doesn't exist!")
        return False
    else:

        try:
            active = repo.active_branch
        except TypeError:  # if HEAD is detached, throws exception
            active = None

        remotes = repo.remotes

        if not remotes:
            print(ERROR + "There is no remote to fetch.")
            return False
        _fetchRemotes(remotes)

        for branch in sorted(repo.heads, key=lambda b: b.name):
            _updateBranch(repo, branch, branch == active)

        return True


def _cloneRepos(group, projects, currentFolder, update):
    """Clone if the repository is not exists"""

    groupDirectory = os.path.join(currentFolder, group)
    if not os.path.exists(groupDirectory):
        os.mkdir(groupDirectory)
        print(GREEN + group + RESET + ' directory created.')
    else:
        print(BLUE + group + RESET + ' directory already exists.')

    print(LINE)
    print('')

    for project in projects:

        repoPath = os.path.join(currentFolder, group, project['path'])

        print(BLUE + "Path: " + repoPath)
        if not os.path.exists(repoPath):
            print(GREEN + project['name'] + RESET + ' is cloning.')
            repo = git.Repo.clone_from(project['ssh_url_to_repo'], repoPath, branch='master')
            print(GREEN + project['name'] + RESET + ' clone process is completed.')
        else:
            if not update:
                print(BLUE + project['name'] + RESET + ' is already exists. Skipping this repository.')
            else:
                print(BLUE + project['name'] + RESET + ' is already exists.' + GREEN + ' Updating the repo.')
                _updateExistingRepo(repoPath)

        print(LINE+LINE)
        print(" ")



def _getProjectsOfGroup(group=None):
    """Get the list of projects in the given group"""

    if not group:
        print(ERROR + 'You need to specify a group name')
        return False

    # /groups/:id
    url = URL + POSTFIX + 'groups/' + group

    try:
        HEADERS = {'PRIVATE-TOKEN': PRIVATE_TOKEN}

        print('Making request for the group ' + BLUE + group)
        print(BOLD + 'Request URL: ' + url)
        result = requests.get(url, headers=HEADERS, timeout=API_TIMEOUT)

        if result.status_code == 200:

            projectList = result.json()['projects']

            if len(projectList) > 0:
                print(GREEN + str(len(projectList)) + ' projects found.')
            else:
                print(ERROR + ' no projects found.')
                return False

            return projectList
        else:
            print(ERROR + 'Group project list API returned with the following code: %s ' % result.status_code)
            return False
    except rest_exceptions.Timeout:
        print(ERROR + 'Couldn\'t send request to or receive response from GitLab API within ' + API_TIMEOUT + ' seconds.')
        return False
    except rest_exceptions.ConnectionError:
        print(ERROR + 'Couldn\'t connect to GitLab API.')
        return False
    except:
        print(ERROR + 'GitLab API call failed.')
        return False


def main():

    color_init(autoreset=True)

    if not URL:
        print(ERROR + 'You need to specify gitlab url.')
        exit(1)

    if not POSTFIX:
        print(ERROR + 'You need to specify gitlab url postfix.')
        exit(1)

    if not PRIVATE_TOKEN:
        print(ERROR + 'You need to specify your gitlab user\'s PRIVATE_TOKEN in the config file.')
        exit(1)

    parser = argparse.ArgumentParser(
         description="Clone GitLab repositories at once.")

    parser.add_argument('group', nargs='?', default=False, help='Provide project group key.')
    parser.add_argument('-u', '--update', action='store_true', default=False, help='Update the existing repositories.')

    args = parser.parse_args()

    if not args.group:
        print (ERROR + 'Please provide group key.')
        exit(1)
    else:
        print(LINE)
        print(BOLD + ' Group name is: ' + GREEN + args.group)
        print(BOLD + ' Update: ' + 'True' if args.update is True else 'False')
        print(LINE)
        print('')


    projects = _getProjectsOfGroup(args.group)

    if not projects:
        exit(1)

    currentFolder = _getCurrentFolder()
    print('')

    _cloneRepos(args.group, projects, currentFolder, update=args.update)


def run():
    """
    Wrapper for main() to catch KeyboardInterrupts.
    """
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted.')
