// Source Code for maxchernoff.ca
// https://github.com/gucci-on-fleek/maxchernoff.ca
// SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
// SPDX-FileCopyrightText: 2024 Max Chernoff

/////////////
/// Setup ///
/////////////

// Select our DNS providers
var DSP_KNOT = NewDnsProvider("knot");
var REG_MONITOR = NewRegistrar("DoH");

// Define our IP addresses
var IPv4 = "152.53.36.213"
var IPv6 = "2a0a:4cc0:2000:172::1"

// Begin the domain
D("maxchernoff.ca", REG_MONITOR,
    DnsProvider(DSP_KNOT, 0),
    DefaultTTL("1h"),

    ////////////////////
    /// Name Servers ///
    ////////////////////

    // The master nameserver
    CNAME("ns.maxchernoff.ca.", "@"),
    NAMESERVER("ns.maxchernoff.ca."),

    // Use Hurricane Electric for the public nameservers
    NAMESERVER("ns2.he.net."),
    NAMESERVER("ns3.he.net."),
    NAMESERVER("ns4.he.net."),
    NAMESERVER("ns5.he.net."),

    ////////////////////
    /// IP Addresses ///
    ////////////////////

    A("@", IPv4), // IPv4
    AAAA("@", IPv6), // IPv6

    // HTTPS Records
    HTTPS(
        "@", // Domain
        1,   // Priority
        ".", // Target Domain (this domain)
        "alpn=h3,h2 " +            // Protocols supported (HTTP/2 and HTTP/3)
        "ipv4hint=" + IPv4 + " " + // IPv4 Address
        "ipv6hint=" + IPv6         // IPv6 Address
    ),

    //////////////////
    /// Web Server ///
    //////////////////

    // Generic Flask API backend
    CNAME("api", "maxchernoff.ca."),

    // Hosts an Overleaf instance
    CNAME("overleaf", "@"),

    // Dynamic DNS to home router
    CNAME("red-deer", "gucci-on-fleek.duckdns.org."),

    // Container Registry
    CNAME("registry", "maxchernoff.ca."),

    // Needed for GitHub to offer a server-side redirect from GitHub Pages
    CNAME("stardew-valley-item-finder", "maxchernoff.ca."),
    TXT("_github-pages-challenge-gucci-on-fleek",
        "66b26f150db40469b0d311fdc9dc79"),

    // Woodpecker CI instance
    CNAME("woodpecker", "maxchernoff.ca."),

    // The primary web domain
    CNAME("www", "@"),

    ////////////////////
    /// Certificates ///
    ////////////////////

    CAA_BUILDER({
        label: "@", // Apply this to the root domain
        iodef: "mailto:acme-certificates@maxchernoff.ca", // Email Address
        issue: [ "letsencrypt.org" ], // Allowed certificate issuers
        issuewild: "none", // No wildcard certificates
        issue_critical: true, // Mark all records as critical
        iodef_critical: true,
        issuewild_critical: true,
    }),

    /////////////
    /// Email ///
    /////////////

    // Migadu ownership verification
    TXT("@", "hosted-email-verify=ghwfivk6"),

    // Mailbox receiving servers
    MX("@", 10, "aspmx1.migadu.com."),
    MX("@", 20, "aspmx2.migadu.com."),
    MX("*", 10, "aspmx1.migadu.com."),
    MX("*", 20, "aspmx2.migadu.com."),

    // DKIM (signs outgoing mail)
    CNAME("key1._domainkey", "key1.maxchernoff.ca._domainkey.migadu.com."),
    CNAME("key2._domainkey", "key2.maxchernoff.ca._domainkey.migadu.com."),
    CNAME("key3._domainkey", "key3.maxchernoff.ca._domainkey.migadu.com."),

    // SPF (restricts outgoing mail's IP addresses)
    TXT("@",
        "v=spf1 " + // Version (always 1)
        "include:spf.migadu.com " + // Allow Migadu to send mail
        "mx:tug.org " + // Also allow the TUG Mailman to forward my emails
        "-all" // Reject all other mail
    ),

    // DMARC (tells receiving servers to reject spoofed emails)
    DMARC_BUILDER({
        // Reject anything that fails DMARC
        policy: "reject",
        subdomainPolicy: "reject",

        // Send reports to these addresses
        rua: ["mailto:mail-reports@maxchernoff.ca"],
        ruf: ["mailto:mail-reports@maxchernoff.ca"],
        failureOptions: "1", // Report if any part of DMARC fails

        // Require strict SPF and DKIM matching
        alignmentSPF: "strict",
        alignmentDKIM: "strict",
    }),

    // MTA-STS (tells receiving servers to use TLS)
    CNAME("mta-sts", "maxchernoff.ca."),
    TXT("_mta-sts", "v=STSv1; id=2"),
    TXT("_smtp._tls", "v=TLSRPTv1; rua=mailto:tls-reports@maxchernoff.ca"),

    // Mail server access (IMAP, SMTP, etc.)
    SRV("_autodiscover._tcp", 0, 1, 443, "autodiscover.migadu.com."),
    SRV("_imaps._tcp", 0, 1, 993, "imap.migadu.com."),
    SRV("_submissions._tcp", 0, 1, 465, "smtp.migadu.com."),

    /////////////////////
    /// Miscellaneous ///
    /////////////////////

    // Google Search Console ownership verification
    TXT("@",
        "google-site-verification=gWIJ3Mg-zy1MuwAJHw8PkhOEENqOmLxUNslbQ4ZPfAE"),
END);
