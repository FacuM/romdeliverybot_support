Robbie
======

Say hi to Robbie! I'm a small Telegram bot written entirely in Python, based off two awesome modules: pyTelegramBotAPI and PyGithub.

I'm not very smart, but go ahead, ask me anything, I'll do my best! :)

#### Usage
The usage is pretty simple: feed me up with a bunch of content off the if-else statements. Then, fire up the `main.py` file, located at the root of this project.

Oh, by the way, don't forget to define your Telegram API key! On whatever system you're in, define a shell/environment variable called `API_KEY` and put in there your key.

#### TODO
- [x] ~~Minimize the user activity on internals.~~
- [ ] Improve performance (implement _AsyncTeleBot_).
- [x] ~~Fix a bunch of possible security issues.~~
- [x] ~~Use an actual database and implement OAuth token authentication.~~ (kept username/password auth)
- [ ] Implement fully cloud-managed OAuth authentication.

#### Licensing
Robbie (with exception of its dependencies) is licensed under the [GNU Affero General Public License v3.0](LICENSE).

#### Dependencies
This bot depends of several APIs, libraries and modules, their licensing may vary. The list provided below, specifies each direct dependency. Please note that some other dependencies might be involved of which their licensing be different too.

- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) (_GNU GPL v2.0_) - Python Telegram bot API.
  This API provides the core functionality.

- [PyMySQL](https://github.com/PyMySQL/PyMySQL) (_MIT License_) - Pure Python MySQL Client.
  This API provides support for SQL queries to a MySQL/MariaDB, it's required to read/write the list of messages (to allow purging) and to save the user's personal access tokens to log into the GitHub API.

- [PyGithub](https://github.com/PyGithub/PyGithub) (_GNU LGPL v3.0_) - Typed interactions with the GitHub API v3
  This API provides support for GitHub searches and other general purpose interaction with their API.

- [DuckDuckGo2](https://github.com/FacuM/python-duckduckgo) ([_BSD-style license_](https://github.com/FacuM/python-duckduckgo/blob/master/LICENSE)) - A library for querying the DuckDuckGo API.
  This API provides support for DuckDuckGo searches.
  Please note that this is just a fork and quick port over the [original version](https://github.com/crazedpsyc/python-duckduckgo), just to make it compatible with Python 3.x.
