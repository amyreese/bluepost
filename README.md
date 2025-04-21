# bluepost

bluesky bot: repost everything another account posts/reposts

[![version](https://img.shields.io/pypi/v/bluepost.svg)](https://pypi.org/project/bluepost)
[![license](https://img.shields.io/pypi/l/bluepost.svg)](https://github.com/amyreese/bluepost/blob/main/LICENSE)

This bot automates the process of reposting everything from a secondary Bluesky
account to a primary Bluesky account.

I use this to reposting everything from my [Bridgy Fed](https://fed.brid.gy)
account to my standard Bluesky account, so that I don't need to use a special
crossposting app (like [Croissant](https://croissantapp.com)) or manually 
repost everything myself.


Install
-------

Install with pip:

```shell-session
$ pip install bluepost
```

Or run with uv:

```shell-session
$ uvx bluepost ...
```


Usage
-----

Run bluepost with the username/password, and a target handle:

```shell-session
$ bluepost --username <USERNAME> --password <PASSWORD> --target <HANDLE> ...
```

Alternately, set environment variables:

```shell-session
$ env BLUEPOST_USERNAME= BLUEPOST_PASSWORD= BLUEPOST_TARGET= bluepost ...
```

Use the `run` command to repost once and exit:

```shell-session
$ bluepost run
```

Or use the `serve` command to start a long-running process:

```shell-session
$ bluepost serve --interval <MINUTES>
```


License
-------

bluepost is copyright Amethyst Reese, and licensed under the MIT license.
