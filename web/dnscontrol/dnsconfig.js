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

// Handle the DANE TLSA records
function dane(name) {
    return [
        TLSA(
            name, // Port + Protocol + Domain
            0,    // Certificate Usage: CA Constraint
            1,    // Selector: Public Key
            1,    // Matching Type: SHA-256
                  // ISRG Root X1 (Let's Encrypt RSA)
            "0b9fa5a59eed715c26c1020c711b4f6ec42d58b0015e14337a39dad301c5afc3"
        ),
        TLSA(
            name, // Port + Protocol + Domain
            0,    // Certificate Usage: CA Constraint
            1,    // Selector: Public Key
            1,    // Matching Type: SHA-256
                  // ISRG Root X2 (Let's Encrypt ECDSA)
            "762195c225586ee6c0237456e2107dc54f1efc21f61a792ebd515913cce68332"
        ),
    ]
}

// Create the DNS records needed for a web server hosted on this server
function web(name) {
    return [
        A(name, IPv4),    // IPv4 Address
        AAAA(name, IPv6), // IPv6 Address

        // HTTPS Records
        HTTPS(
            name,                      // Domain
            1,                         // Priority
            ".",                       // Target Domain (this domain)
            "alpn=h3,h2 " +            // Protocols supported (HTTP/2 and HTTP/3)
            "ipv4hint=" + IPv4 + " " + // IPv4 Address
            "ipv6hint=" + IPv6         // IPv6 Address
        ),

        // DANE
        dane(
            name == "@" ?
            "_443._tcp" :
            "_443._tcp." + name
        ),
    ]
}

// Begin the domain
D("maxchernoff.ca", REG_MONITOR,
    DnsProvider(DSP_KNOT, 0),
    DefaultTTL("1d"),

    ////////////////////
    /// Name Servers ///
    ////////////////////

    NAMESERVER_TTL("1d"),

    // The master nameserver
    NAMESERVER("ns.maxchernoff.ca."),

    // Master nameserver configuration
    web("ns"),
    SVCB(
        "_dns.ns",                 // Domain + Protocol
        1,                         // Priority
        ".",                       // Target Domain (this domain)
        "alpn=dot " +              // Protocols supported (DNS-over-TLS)
        "ipv4hint=" + IPv4 + " " + // IPv4 Address
        "ipv6hint=" + IPv6         // IPv6 Address
    ),
    dane("_853._tcp.ns"),

    // Use Hurricane Electric for the public nameservers
    NAMESERVER("ns2.he.net."),
    NAMESERVER("ns3.he.net."),
    NAMESERVER("ns4.he.net."),
    NAMESERVER("ns5.he.net."),

    //////////////////
    /// Web Server ///
    //////////////////

    // Root domain
    web("@"),

    // Generic Flask API backend
    web("api"),

    // Hosts an Overleaf instance
    web("overleaf"),

    // Container Registry
    web("registry"),

    // Needed for GitHub to offer a server-side redirect from GitHub Pages
    web("stardew-valley-item-finder"),
    TXT("_github-pages-challenge-gucci-on-fleek",
        "66b26f150db40469b0d311fdc9dc79"),

    // Woodpecker CI instance
    web("woodpecker"),

    // The primary web domain
    web("www"),

    ////////////////////
    /// Certificates ///
    ////////////////////

    // Limits the CAs permitted to issue certificates
    CAA_BUILDER({
        label: "@", // Apply this to the root domain
        iodef: "mailto:acme-certificates@maxchernoff.ca", // Email Address
        issue: [ "letsencrypt.org" ], // Allowed certificate issuers
        issuewild: "none", // No wildcard certificates
        issue_critical: true, // Mark all records as critical
        iodef_critical: true,
        issuewild_critical: true,
    }),

    // SSH fingerprint
    SSHFP("@",
        4, // Key Algorithm: Ed25519
        2, // Hash Algorithm: SHA-256
        "6d270177a80068335a4f80983ab964f803c40581d94feccca8896a1101925a01"
    ),

    /////////////
    /// Email ///
    /////////////

    // Migadu ownership verification
    TXT("@", "hosted-email-verify=ghwfivk6"),

    // Mailbox receiving servers
    MX("@", 10, "aspmx1.migadu.com."),
    MX("@", 20, "aspmx2.migadu.com."),

    // DKIM (signs outgoing mail)
    CNAME("key1._domainkey", "key1.maxchernoff.ca._domainkey.migadu.com."),
    CNAME("key2._domainkey", "key2.maxchernoff.ca._domainkey.migadu.com."),
    CNAME("key3._domainkey", "key3.maxchernoff.ca._domainkey.migadu.com."),

    // SPF (restricts outgoing mail's IP addresses)
    TXT("@",
        "v=spf1 " + // Version (always 1)
        "include:spf.migadu.com " + // Allow Migadu to send mail
        "mx:tug.org " + // Also allow the TUG Mailman to forward my emails
        "mx:ntg.nl " + // Also allow the NTG Mailman to forward my emails
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
    web("mta-sts"),
    TXT("_mta-sts", "v=STSv1; id=2"),
    TXT("_smtp._tls", "v=TLSRPTv1; rua=mailto:tls-reports@maxchernoff.ca"),

    // Mail server access (IMAP, SMTP, etc.)
    SRV("_autodiscover._tcp", 0, 1, 443, "autodiscover.migadu.com."),
    SRV("_imaps._tcp", 0, 1, 993, "imap.migadu.com."),
    SRV("_submissions._tcp", 0, 1, 465, "smtp.migadu.com."),
    SRV("_sieve._tcp", 0, 1, 4190, "imap.migadu.com."),

    /////////////////////
    /// Miscellaneous ///
    /////////////////////

    // Google Search Console ownership verification
    TXT("@",
        "google-site-verification=gWIJ3Mg-zy1MuwAJHw8PkhOEENqOmLxUNslbQ4ZPfAE"),

    // Dynamic DNS to home router
    IGNORE("red-deer", "A,AAAA"),
END);
