# CMIMC Online
A website for the CMIMC Programming Competition and CMIMC 2021, which will be held online.

## Setup Instructions (now with Docker!)
1. Make sure you have [Python](https://www.python.org/downloads/) (and pip) installed on your computer.
2. Install [Docker](https://docs.docker.com/get-docker/).
3. Clone this repository: `git clone https://github.com/CMU-Math/cmimc-online.git`. The rest of the commands should be run within the newly created folder.
4. Run `./setup.sh`. A local version of the site should be running on [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
5. Run `./setup-admin.sh` (while `./setup.sh` is still running) to create a Django Admin user.

## Contributing Code
1. On the Trello page, add yourself to any projects you want to work on
2. Each project should have its own branch. Either create a new branch with `git checkout -b new-branch-name` or pull from an existing remote branch.
3. Once the changes are ready to be merged into the main branch, submit a pull request with Github's online interface.
