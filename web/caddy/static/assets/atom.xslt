<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC
         "-//W3C//ENTITIES HTML MathML Set//EN//XML"
         "https://www.w3.org/2003/entities/2007/htmlmathml-f.ent"
       >
<!-- Source Code for maxchernoff.ca
     https://github.com/gucci-on-fleek/maxchernoff.ca
     SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
     SPDX-FileCopyrightText: 2025 Max Chernoff -->
<xsl:stylesheet
    version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:atom="http://www.w3.org/2005/Atom"
>
    <xsl:output method="html" encoding="UTF-8" indent="yes" />

    <xsl:template match="/">
        {{- include "/includes/base.html" (dict
            "title"         "Atom Feed"
            "title-trailer" ("&hairsp;&mdash;&hairsp;Max Chernoff")
            "body"          `
                    <h2>About</h2>
                    <p>This is a preview of the <a
                    href="https://en.wikipedia.org/wiki/Atom_(web_standard)">Atom feed</a>
                    for my website. You can browse this page with your web
                    browser if you like, but you'll have a better experience
                    using a <a
                    href="https://en.wikipedia.org/wiki/Feed_reader">feed
                    reader</a>.</p>

                    <p>The articles on this page may render incorrectly, so if
                    you <em>don't</em> have a feed reader, then I recommend that
                    you read my posts via the links on the <a href="/">home
                    page</a> instead.</p>

                    <h2>Posts</h2>
                    <xsl:apply-templates select="atom:feed/atom:entry" />
            `
            "date"          ""
            "description"   "This is an Atom feed for Max Chernoff's website."
        ) | trimPrefix "<!DOCTYPE html>"
        | replace "</html>" `<script type="module" src="/assets/atom.js" async="async"></script></html>`
        -}}
    </xsl:template>

    <xsl:template match="atom:entry">
        <article>
            <header>
                <h3>
                    <a>
                        <xsl:attribute name="href">
                            <xsl:value-of select="atom:link/@href"/>
                        </xsl:attribute>
                        <xsl:value-of select="atom:title"/>
                    </a>
                </h3>
                <p><date><xsl:value-of select="substring-before(atom:published, 'T')" /></date></p>
            </header>
            <details class="atom">
                <summary class="atom">
                    <xsl:value-of
                        select="atom:summary"
                        disable-output-escaping="yes"
                    />
                </summary>
                <xsl:value-of
                    select="atom:content"
                    disable-output-escaping="yes"
                />
            </details>
        </article>
    </xsl:template>

</xsl:stylesheet>
