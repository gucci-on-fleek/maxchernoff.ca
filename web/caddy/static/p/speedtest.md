---
title: "Caddy Speedtest"
description: "A Caddy speedtest module"
inject-head: |
    <meta name="go-import" content="maxchernoff.ca/tools/speedtest git https://github.com/gucci-on-fleek/caddy-speedtest.git">
---

{{- /* Source Code for maxchernoff.ca
     https://github.com/gucci-on-fleek/maxchernoff.ca
     SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
     SPDX-FileCopyrightText: 2025 Max Chernoff */ -}}

This is a Caddy module that provides a basic <abbr>HTTP</abbr> speed
test service, intended to be used via command-line programs like `curl`
or `wget`.


Installation
------------

- Using [`xcaddy`](https://github.com/caddyserver/xcaddy):

  ```console
  $ xcaddy build --with maxchernoff.ca/tools/speedtest
  ```

- Using `caddy add-package` ([not
  recommended](https://github.com/caddyserver/caddy/issues/7010)):

  ```console
  $ caddy add-package maxchernoff.ca/tools/speedtest
  ```

- Manually, by visiting
  [`caddyserver.com/download`](https://caddyserver.com/download) and
  selecting `maxchernoff.ca/tools/speedtest` from the list of
  plugins.


Usage
-----

### Server

Add the following to your `Caddyfile`:

```caddyfile
example.com {
	speedtest /speedtest
}
```

### Client

To test download speed:

```console
$ curl --output /dev/null --progress-meter https://example.com/speedtest?bytes=100MB
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 95.3M  100 95.3M    0     0   410M      0 --:--:-- --:--:-- --:--:--  411M
```

To test upload speed:

```console
$ head --bytes=100M /dev/urandom | curl --output /dev/null --progress-meter --form file=@- https://example.com/speedtest
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  100M  100    23  100  100M    149   651M --:--:-- --:--:-- --:--:--  649M
```

### Hosted Service

A public instance of this service is hosted on my personal server. The
server is fairly slow, so **under no circumstances** should you use it
in any scripts or include its <abbr>URL</abbr> in any lists of speed
test services. However, feel free to use it for manually by typing a
`curl`/`wget` command into your terminal.

As long as you follow the usage instructions above, you can access it at
[`www.maxchernoff.ca/tools/speedtest`](https://www.maxchernoff.ca/tools/speedtest).


Why does this exist?
--------------------

There are a plethora of speed test services available online, but none
of them meet _all_ the following criteria:

- Must be directly usable from `curl`.

- Must support uploading files of arbitrary size.

- Must have a well-defined geographical location (no anycast).

Since I'm already using Caddy for other purposes, the easiest solution
was to write a Caddy module that provides this functionality.

Source Code
-----------

The source code for this module is hosted on GitHub at
[`github.com/gucci-on-fleek/caddy-speedtest`](https://github.com/gucci-on-fleek/caddy-speedtest).

Licence
-------

[Apache License, Version 2.0 or
later](https://www.apache.org/licenses/LICENSE-2.0).

