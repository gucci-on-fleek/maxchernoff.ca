// Source Code for maxchernoff.ca
// https://github.com/gucci-on-fleek/maxchernoff.ca
// SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
// SPDX-FileCopyrightText: 2024 Max Chernoff

/////////////
/// Setup ///
/////////////

// Select our DNS providers
var DSP_KNOT = NewDnsProvider("knot")
var REG_MONITOR = NewRegistrar("DoH")

// Define our IP addresses
var IPv4 = "!!network.ipv4!!"
var IPv6 = "!!network.ipv6!!"

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

// Configure subdomains to not have email
var MAIL_ALLOWED = []
function no_mail(name) {
    if (!(MAIL_ALLOWED.indexOf(name) >= 0)) {
        return [
            TXT(name, "v=spf1 -all"), // Prevent sending email
            MX(name, 0, "."),         // Prevent receiving email
        ]
    } else {
        return []
    }
}

// Create the DNS records needed for a web server hosted on this server
function web(name) {
    var out = [
        A(name, IPv4),    // IPv4 Address
        AAAA(name, IPv6), // IPv6 Address

        // HTTPS Records
        // HTTPS(
        //     name,                      // Domain
        //     1,                         // Priority
        //     ".",                       // Target Domain (this domain)
        //     "alpn=h3,h2 " +            // Protocols supported (HTTP/2 and HTTP/3)
        //     "ipv4hint=" + IPv4 + " " + // IPv4 Address
        //     "ipv6hint=" + IPv6         // IPv6 Address
        //     // "tls-supported-groups=29,23" // x25519, secp256r1 // TODO: Enable this when DNSControl supports it
        // ),
        IGNORE(name, "HTTPS"), // TODO Not ideal, but good enough for now
    ]

    // DANE
    if (name == "@") {
        out.push(dane("_443._tcp"))
        out.push(dane("_443._quic"))
    } else {
        out.push(dane("_443._tcp." + name))
        out.push(dane("_443._quic." + name))
    }

    // Prevent email on this domain
    out.push(no_mail(name))

    return out
}

// Primary domain: maxchernoff.ca
MAIL_ALLOWED = ["@", "noreply"]
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

    // ECH Domain
    web("ech"),

    // Grafana dashboard
    web("grafana"),

    // Hosts an Overleaf instance
    web("overleaf"),

    // Prometheus metrics
    web("prometheus"),

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

    // DKIM reporting
    TXT("_report._domainkey",
        "ra=mail-reports " + // Send reports to this address
        "rr=all "            // Report on all emails
    ),

    // DKIM ADSP (Obsolete, but maybe still used somewhere)
    TXT("_adsp._domainkey",
        "dkim=unknown " +    // Mailman will break any DKIM signatures
        "ra=mail-reports " + // Send reports to this address
        "rr=all"             // Report on all emails
    ),

    // SPF (restricts outgoing mail's IP addresses)
    TXT("@",
        "v=spf1 " +     // Version (always 1)
        "include:spf.migadu.com " + // Allow Migadu to send mail
        "mx:tug.org " + // Also allow the TUG Mailman to forward my emails
        "~all"          // Send all other mail to spam (soft fail)
    ),

    // DMARC (tells receiving servers to reject spoofed emails)
    DMARC_BUILDER({
        // Send anything that fails to spam
        policy: "quarantine",
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

    // Outgoing transactional email server
    web("noreply"),
    TXT("noreply",
        "v=spf1 " + // Version (always 1)
        "a " +      // Allow the IP address of this server
        "-all"      // Reject all other mail
    ),

    MX("noreply", 0, "."), // Prevent receiving email

    TXT("default._domainkey.noreply", "v=DKIM1 k=rsa p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnT+imAGiJsBFdKU16lCvOwSsTOxEnQHrbr5JYvJYcdcYD+D5zYb7o6E6NvEYih7+BEQkAXA5viwABQFD5PQ/6d76w2z/UFB76jN2H2HMRhH/GxCK0RN5SPZNHfsLkGQKrZWsgm4UI4YHTDxqO1N1ILazVFiDOqsxIe3Z6EufZfayfjbaSYl66ZXu0ZDyYgsH7BjhoYggStvsbFnd100FbSx+8Oc66JSr5PRxThJoBBX0Ranr/R/+hhk2/oQH2W2Nnsc6VHHgVhPvV1o3pGFyCNDmP+vsxX4GozsgUEVIGvJ6CEbEBkqEjN/sHSY2bCuLsPoG+NO+AKKmAWthQNl+JQIDAQAB"),

    DMARC_BUILDER({
        "label": "noreply",
        // Send anything that fails to spam
        policy: "reject",
        subdomainPolicy: "reject",

        // Send reports to these addresses
        rua: ["mailto:mail-reports@maxchernoff.ca"],
        ruf: ["mailto:mail-reports@maxchernoff.ca"],
        failureOptions: "1", // Report if any part of DMARC fails

        // Require strict SPF and DKIM matching
        alignmentSPF: "relaxed",
        alignmentDKIM: "strict",
    }),
    TXT("noreply.maxchernoff.ca._report._dmarc", "v=DMARC1;"),
    TXT("duck.tel._report._dmarc", "v=DMARC1;"),

    /////////////////////
    /// Miscellaneous ///
    /////////////////////

    // Google Search Console ownership verification
    TXT("@",
        "google-site-verification=gWIJ3Mg-zy1MuwAJHw8PkhOEENqOmLxUNslbQ4ZPfAE"),

    CNAME("red-deer", "rd.duck.tel."),

    // dnssecuritytxt, see https://github.com/disclose/dnssecuritytxt/
    TXT("@", "security_contact=mailto:security@maxchernoff.ca"),
    TXT("@", "security_contact=https://www.maxchernoff.ca/#contact"),

    // Geographical location of the server
    LOC_BUILDER_DD({
        label: "@",
        x: 38.747494,
        y: -77.531749,
        alt: 70.48,
        horizontal_precision: 100,
        vertical_precision: 10,
        size: 100,
    }),
)

// Secondary domain: duck.tel
MAIL_ALLOWED = ["@"]
D("duck.tel", REG_MONITOR,
    DnsProvider(DSP_KNOT, 0),
    DefaultTTL("1d"),

    ////////////////////
    /// Name Servers ///
    ////////////////////

    NAMESERVER_TTL("1d"),

    // The master nameserver
    NAMESERVER("ns.maxchernoff.ca."),

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


    ///////////////////
    /// Dynamic DNS ///
    ///////////////////

    // Dynamic DNS to my home server
    IGNORE("rd", "A,AAAA"),
    IGNORE("_acme-challenge.*.rd", "TXT"),
    no_mail("rd"),

    CAA_BUILDER({
        label: "rd",
        iodef: "mailto:acme-certificates@maxchernoff.ca",
        issue: [ // Restrict to only DNS validation
            "letsencrypt.org" +
            ";validationmethods=dns-01"
        ],
        issuewild: "none",
        issue_critical: true, // Mark all records as critical
        iodef_critical: true,
        issuewild_critical: true,
    }),

    LOC_BUILDER_DD({
        label: "rd",
        x: 52.3,
        y: -113.8,
        alt: 800,
        horizontal_precision: 20e3,
        vertical_precision: 100,
        size: 10,
    }),

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

     /////////////
    /// Email ///
    /////////////

    // Migadu ownership verification
    TXT("@", "hosted-email-verify=4c9llzmf"),

    // Mailbox receiving servers
    MX("@", 10, "aspmx1.migadu.com."),
    MX("@", 20, "aspmx2.migadu.com."),

    // DKIM (signs outgoing mail)
    CNAME("key1._domainkey", "key1.duck.tel._domainkey.migadu.com."),
    CNAME("key2._domainkey", "key2.duck.tel._domainkey.migadu.com."),
    CNAME("key3._domainkey", "key3.duck.tel._domainkey.migadu.com."),

    // DKIM reporting
    TXT("_report._domainkey",
        "ra=mail-reports " + // Send reports to this address
        "rr=all"             // Report on all emails
    ),

    // DKIM ADSP (Obsolete, but maybe still used somewhere)
    TXT("_adsp._domainkey",
        "dkim=discardable " + // No mailing lists here, so we can be strict
        "ra=mail-reports " +  // Send reports to this address
        "rr=all"              // Report on all emails
    ),

    // SPF (restricts outgoing mail's IP addresses)
    TXT("@",
        "v=spf1 " +                 // Version (always 1)
        "include:spf.migadu.com " + // Allow Migadu to send mail
        "-all"                      // Reject all other mail
    ),

    // DMARC (tells receiving servers to reject spoofed emails)
    DMARC_BUILDER({
        // Send anything that fails to spam
        policy: "reject", // No mailing lists here, so we can be strict
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
    TXT("_mta-sts", "v=STSv1; id=1"),
    TXT("_smtp._tls", "v=TLSRPTv1; rua=mailto:tls-reports@maxchernoff.ca"),

    /////////////////////
    /// Miscellaneous ///
    /////////////////////

    // Google Search Console ownership verification
    TXT("@",
        "google-site-verification=AF_OhBzlGPeUXXBkZcv4D-yBvXCUibw9hNd8OoRK2Cw"),
)
