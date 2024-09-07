---
title: Overleaf Instance
date: "2024-09-03"
description: >-
    An introduction to the Overleaf instance hosted on maxchernoff.ca.
---

{{- /* Source Code for maxchernoff.ca
     https://github.com/gucci-on-fleek/maxchernoff.ca
     SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
     SPDX-FileCopyrightText: 2024 Max Chernoff */ -}}

<style>
     dt {
          display: list-item;
     }
     dl {
          padding-left: 40px;
     }
</style>

{{- define "overleaf" -}}
    [`overleaf.maxchernoff.ca`](https://overleaf.maxchernoff.ca)
{{- end -}}

{{- define "email" -}}
    [`overleaf@maxchernoff.ca`](mailto:overleaf@maxchernoff.ca?subject=Overleaf%20Registration)
{{- end }}


About
-----

At {{ template "overleaf" }}, I'm hosting an instance of the open-source
[Overleaf Community Edition](https://github.com/overleaf/overleaf/).
This instance is (somewhat) open to the public, but all registrations
must be manually processed.

If you're too lazy to read further, then email {{ template "email" }} to
request an account. But you really should keep reading for some
important caveats.


Features and Limitations
------------------------

<dl>
<dt>Up-to-date TeX Live
<dd>

The TeX Live distribution at {{ template "overleaf" }} is updated daily,
while [`overleaf.com`](https://overleaf.com) only updates their TeX Live
distribution once a year. This means that your documents will always
compile using the latest package updates, but it also means that a
document that compiled one day might not compile the next.

<dt>Unlimited compile times
<dd>

There is no time limit on the compile time of your documents, so you can
easily compile large documents that contain many Ti*k*Z pictures. This
also means that a buggy document might never finish compiling, so you
should keep an eye on your compiler progress.

<dt>Unlimited collaborators
<dd>

There are no restrictions on the number of people that you can share
your projects with, provided that everyone has an account on {{ template
"overleaf" }}.

<dt>Ran on a single server
<dd>

All of [`maxchernoff.ca`](https://www.maxchernoff.ca)
is hosted on a single server and isn't backed up anywhere, so if the
server goes down, then you're out of luck. That being said, the
server is located in a dedicated data center and uses a fairly
robust configuration, so you'll _probably_ be fine.

<dt>Ran by a single person
<dd>

I'm the only one who has access to the server, so if something breaks
while I'm busy with schoolwork, then it might be a while before I have
time to fix it. This also means that if I lose interest in maintaining
the server, then it might go down forever.

</dl>


User Requirements
-----------------

To request an account, you must meet **one** of the following criteria:

- I personally know you somehow. We don't need to be close, but I should
  at least recognize your name.

- You're a Math or Physics student at the University of Calgary. In this
  case, please send your account request from your `@ucalgary.ca`
  address.

- You're an active member of the TeX community. This is awfully vague,
  but if this applies, you should generally be able to send me a link to
  one of your packages on [<abbr>CTAN</abbr>](https://ctan.org), a
  publication in [*TUGboat*](https://tug.org/TUGboat), a link to your
  [TeX Stack Exchange](https://tex.stackexchange.com) profile, or
  something similar.

If you're unsure, just ask and I'll probably say yes.


Policies
--------

Once you have an account, you're free to use the service however you
want, whether it be for school, work, or personal projects. Of course,
the standard disclaimer still applies: if you somehow annoy me, then I
might disable your account.

Also, the server isn't very secure, so please don't use it to mine
Bitcoin 😀.


Registration
------------

Still interested? To register for an account, please **email me at {{
template "email" }}** and I'll register an account for you. Keep in mind
that I need to manually register each account, so it might take a day or
two for me to get back to you.
