---
title: "Home"
description: "Max Chernoff's personal website"
---

{{- /* Source Code for maxchernoff.ca
     https://github.com/gucci-on-fleek/maxchernoff.ca
     SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
     SPDX-FileCopyrightText: 2025 Max Chernoff */ -}}

{{- define "toc-item" -}}
    {{- $path := printf "/p/%s.md" . -}}
    {{- $meta := (include $path | splitFrontMatter).Meta -}}
    - [{{ $meta.title }}&emsp;_({{ $meta.date }})_](/p/{{ . }})
{{- end -}}

About
-----

Hi, I'm Max Chernoff. I'm currently a Physics & Math student, although I
spend most of my time working on various TeX projects.


Posts
-----

<nav>

{{ template "toc-item" "overleaf" }}

{{ template "toc-item" "server-installation" }}

{{ template "toc-item" "luatex-vulnerabilities" }}

</nav>


Tools
-----

<nav>

- [Atom Feed](/atom.xml)

- [Overleaf](https://overleaf.maxchernoff.ca/login)

- [Woodpecker <abbr>CI</abbr>](https://woodpecker.maxchernoff.ca/login)

- [Stardew Valley Item Finder](/tools/Stardew-Valley-Item-Finder/)

</nav>


TeX Projects
------------

### Memberships

- [<abbr>TUG</abbr> Board Member](https://tug.org/board.html) (2023–)

- [TeX Live Committer](https://git.texlive.info/texlive/commit/Master/tlpkg/bin?id=f136d5) (2024–)

### Packages

- [`lua-widow-control`](https://ctan.org/pkg/lua-widow-control)

- [`extractbb.lua`](https://www.ctan.org/pkg/extractbb)

- [`luatex-syntax-highlighter`](https://github.com/gucci-on-fleek/luatex-syntax-highlighter)&emsp;(unreleased)

- [`luatools`](https://github.com/gucci-on-fleek/luatools)&emsp;(unreleased)

- [`unnamed-emoji`](https://github.com/gucci-on-fleek/unnamed-emoji)&emsp;(unreleased)


### Publications

- Automatically removing widows and orphans with `lua-widow-control`.
  *TUGboat*, 43(1), 28–39.
  [<abbr>DOI</abbr>:&#8239;`10.47397/tb/43-1/tb133chernoff-widows`](//tug.org/TUGboat/tb43-1/tb133chernoff-widows.html).
  (2022-05)
- Comparing TeX engines and formats.\
  Abstract: *TUGboat*, 43(2), 209.
  [<abbr>DOI</abbr>:&#8239;`10.47397/tb/43-2/tb134abstracts`](//tug.org/TUGboat/tb43-2/tb134abstracts.html).
  (2022-08)\
  [Video](//youtu.be/MNdAoza8VHU) and
  [slides](//tug.org/tug2022/assets/served/Max_Chernoff-TUG2022-chernoff-engines-slides.pdf).
  (2022-07)
- Automatically removing widows and orphans with `lua-widow-control`.
  *Zpravodaj Československého sdružení uživatelů TeXu*, 2022(1–4),
  49–76.
  [<abbr>DOI</abbr>:&#8239;`10.5300/2022-1-4/49`](//dml.cz/handle/10338.dmlcz/151108).
  (2022-11)
- Updates to "Automatically removing widows and orphans with
  `lua-widow-control`". *TUGboat*, 43(3), 340–342.
  [<abbr>DOI</abbr>:&#8239;`10.47397/tb/43-3/tb135chernoff-lwc`](//tug.org/TUGboat/tb43-3/tb135chernoff-lwc.html).
  (2022-12)

### Profiles

- [GitHub](https://github.com/gucci-on-fleek)

- [CTAN](https://ctan.org/author/chernoff)

- [TeX Stack Exchange](https://tex.stackexchange.com/users/270600/max-chernoff)


Contact
-------

[`website@maxchernoff.ca`](mailto:website@maxchernoff.ca)
