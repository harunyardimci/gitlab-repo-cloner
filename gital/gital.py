# -*- coding: utf-8  -*-
#
# Released under the terms of the MIT License. See LICENSE for details.

import sys
import os
import requests
import git
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

API_TIMEOUT = 10

def _getCurrentFolder():
    """Returns list of the folders of the current working directory"""

    print('Current working directory is ' + GREEN + os.getcwd())
    return os.getcwd()

def _cloneRepos(group, projects, currentFolder):
    """Clone if the repository is not exists"""

    groupDirectory = os.path.join(currentFolder, group)
    if not os.path.exists(groupDirectory):
        os.mkdir(groupDirectory)
        print(GREEN + group + RESET + ' directory created.')
    else:
        print(BLUE + group + RESET + ' directory already exists.')

    for project in projects:

        repoPath = os.path.join(currentFolder, group , project['path'])

        if not os.path.exists(repoPath):
            print(GREEN + project['name'] + RESET + ' is cloning.')
            repo = git.Repo.clone_from(project['ssh_url_to_repo'], repoPath, branch='master')
            print(GREEN + project['name'] + RESET + ' clone process is completed.')
        else:
            print(BLUE + project['name'] + RESET + ' is already exists. Skipping this repository.')


def _getProjectsOfGroup(group=None):
    """Get the list of projects in the given group"""

    if not group:
        print(ERROR + 'You need to specify a group name')
        exit(1)

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
                exit(1)

            return projectList
        else:
            print(ERROR + 'Group project list API returned with the following code: %s ' % result.status_code)
            return False
    except rest_exceptions.Timeout:
        print(ERROR + 'Couldn\'t send request to or receive response from GitLab API within ' + API_TIMEOUT + ' seconds.')
    except rest_exceptions.ConnectionError:
        print(ERROR + 'Couldn\'t connect to GitLab API.')
    except:
        print(ERROR + 'GitLab API call failed.')


def main(argv):

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

   if len(sys.argv) == 1:
       print (ERROR + 'Please provide group key.')
       exit(1)
   else:
       group = sys.argv[1]
       print('===============================')
       print(BOLD + ' Group name is: ' + GREEN + group)
       print('===============================')
       print('')


   projects = _getProjectsOfGroup(group)

   if not projects:
       exit(1)

   currentFolder = _getCurrentFolder()

   _cloneRepos(group, projects, currentFolder)


def run():
    """
    Wrapper for main() to catch KeyboardInterrupts.
    """
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print('Interrupted.')
