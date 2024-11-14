// Source Code for maxchernoff.ca
// https://github.com/gucci-on-fleek/maxchernoff.ca
// SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
// SPDX-FileCopyrightText: 2024 Max Chernoff

var DSP_KNOT = NewDnsProvider("knot");
var REG_MONITOR = NewRegistrar("DoH");

D("maxchernoff.ca", REG_MONITOR,
    DnsProvider(DSP_KNOT),
    DefaultTTL(600),
    A("@", "152.53.36.213"),
    AAAA("@", "2a0a:4cc0:2000:172::1"),
    CAA("@", "issue", "letsencrypt.org"),
    CAA("@", "issue", "sectigo.com"),
    CAA("@", "issuewild", ";"),
    CNAME("api", "maxchernoff.ca."),
    CNAME("key1._domainkey", "key1.maxchernoff.ca._domainkey.migadu.com."),
    CNAME("key2._domainkey", "key2.maxchernoff.ca._domainkey.migadu.com."),
    CNAME("key3._domainkey", "key3.maxchernoff.ca._domainkey.migadu.com."),
    CNAME("mta-sts", "maxchernoff.ca."),
    CNAME("overleaf", "maxchernoff.ca."),
    CNAME("red-deer", "gucci-on-fleek.duckdns.org."),
    CNAME("registry", "maxchernoff.ca."),
    CNAME("stardew-valley-item-finder", "maxchernoff.ca."),
    CNAME("woodpecker", "maxchernoff.ca."),
    CNAME("www", "maxchernoff.ca."),
    HTTPS("@", 1, ".", 'alpn="h3,h2" ipv4hint="152.53.36.213" ipv6hint="2a0a:4cc0:2000:172::1"'),
    MX("@", 10, "aspmx1.migadu.com."),
    MX("@", 20, "aspmx2.migadu.com."),
    MX("*", 10, "aspmx1.migadu.com."),
    MX("*", 20, "aspmx2.migadu.com."),
    SRV("_autodiscover._tcp", 0, 1, 443, "autodiscover.migadu.com."),
    SRV("_imaps._tcp", 0, 1, 993, "imap.migadu.com."),
    SRV("_submissions._tcp", 0, 1, 465, "smtp.migadu.com."),
    TXT("_dmarc", "v=DMARC1; p=reject; rua=mailto:mail-reports@maxchernoff.ca; ruf=mailto:mail-reports@maxchernoff.ca; fo=1; adkim=s; aspf=s;"),
    TXT("_github-pages-challenge-gucci-on-fleek", "66b26f150db40469b0d311fdc9dc79"),
    TXT("_mta-sts", "v=STSv1; id=2"),
    TXT("_smtp._tls", "v=TLSRPTv1; rua=mailto:tls-reports@maxchernoff.ca"),
    TXT("@", "google-site-verification=gWIJ3Mg-zy1MuwAJHw8PkhOEENqOmLxUNslbQ4ZPfAE"),
    TXT("@", "hosted-email-verify=ghwfivk6"),
    TXT("@", "v=spf1 include:spf.migadu.com mx:tug.org -all"),
END);
