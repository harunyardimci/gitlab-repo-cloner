**gital** (gitlab repository cloner)

**gital** is a very simple tool to clone all projects in a [gitlab](http://www.gitlab.com) group.

gital works on OS X, Linux, and Windows Python 2.7 or Python 3 installed.

#Installation

Clone the repository:

    git clone git@github.com:harunyardimci/gitlab-repo-cloner.git
    cd gitlab-repo-cloner

Edit `config.py` file and add your gitlab url and your personal PRIVATE_TOKEN,

    URL             = 'http://your-gitlab-host.org'
    POSTFIX         = '/api/v3/'
    PRIVATE_TOKEN   = 'your-private-key'

Start Installation

    sudo python setup.py install


#Usage

It is very simple to use. You just need to pass the group name (or id) as an argument to the `gital`

    gital my-group

This command will create a directory called `my-group` in the current directory and will clone all projects into that. If you already cloned some of the repositories, `gital` will skip those and continue with others. 
