#!/usr/bin/env python3
import argparse
import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


DEFAULT_BASE_URL = "https://thebellevuehomes.com"
TIMEOUT = 15

PAGES = [
    {
        "label": "Home",
        "path": "/",
        "canonical": "https://thebellevuehomes.com/",
        "title": "Luxury Home Builders in Chicago | The Bellevue Homes",
        "description": "The Bellevue Homes builds refined custom homes and bespoke residences in Chicago, combining architectural detail, craftsmanship, and elevated residential design.",
        "h1": "Luxury Home Builders in Chicago",
    },
    {
        "label": "About",
        "path": "/about",
        "canonical": "https://thebellevuehomes.com/about",
        "title": "About Our Chicago Luxury Home Builders | The Bellevue Homes",
        "description": "Learn about The Bellevue Homes, a Chicago residential development team creating refined custom homes with thoughtful design, craftsmanship, and enduring elegance.",
        "h1": "About The Bellevue Homes",
    },
    {
        "label": "Portfolio",
        "path": "/portfolio-1",
        "canonical": "https://thebellevuehomes.com/portfolio-1",
        "title": "Chicago Luxury Home Portfolio | The Bellevue Homes",
        "description": "View featured Bellevue Homes homes in Lakeview and Lincoln Square, including completed and under-construction luxury residences in Chicago.",
        "h1": "Featured Chicago Luxury Home Projects",
    },
    {
        "label": "Gallery",
        "path": "/gallery",
        "canonical": "https://thebellevuehomes.com/gallery",
        "title": "Luxury Home Design Gallery | The Bellevue Homes",
        "description": "Explore Bellevue Homes interiors, kitchens, bedrooms, bathrooms, living spaces, and custom residential details from luxury homes in Chicago.",
        "h1": "Luxury Home Design Gallery",
    },
    {
        "label": "Testimonials",
        "path": "/testimonials",
        "canonical": "https://thebellevuehomes.com/testimonials",
        "title": "Client Testimonials | The Bellevue Homes",
        "description": "Read testimonials from buyers, brokers, and design professionals about The Bellevue Homes’s craftsmanship, design vision, and Chicago luxury homes.",
        "h1": "Bellevue Homes Testimonials",
    },
    {
        "label": "Contact",
        "path": "/contact",
        "canonical": "https://thebellevuehomes.com/contact",
        "title": "Contact The Bellevue Homes | Chicago Luxury Home Builders",
        "description": "Contact The Bellevue Homes to inquire about custom homes, luxury residential projects, and refined homebuilding in Chicago.",
        "h1": "Contact The Bellevue Homes",
    },
]

EXPECTED_SITEMAP_URLS = [
    "https://thebellevuehomes.com/",
    "https://thebellevuehomes.com/about",
    "https://thebellevuehomes.com/portfolio-1",
    "https://thebellevuehomes.com/gallery",
    "https://thebellevuehomes.com/testimonials",
    "https://thebellevuehomes.com/contact",
]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.in_title = False
        self.description = None
        self.canonical = None
        self.h1s = []
        self.in_h1 = False
        self.ld_json = []
        self.in_ld = False
        self.ld_buffer = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        tag = tag.lower()
        if tag == "title":
            self.in_title = True
        elif tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content")
        elif tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        elif tag == "h1":
            self.in_h1 = True
            self.h1s.append("")
        elif tag == "script" and attrs.get("type") == "application/ld+json":
            self.in_ld = True
            self.ld_buffer = []

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
        elif tag == "script" and self.in_ld:
            self.ld_json.append("".join(self.ld_buffer))
            self.in_ld = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_h1 and self.h1s:
            self.h1s[-1] += data
        if self.in_ld:
            self.ld_buffer.append(data)


class Results:
    def __init__(self):
        self.passes = 0
        self.warnings = 0
        self.failures = 0

    def pass_(self, message):
        self.passes += 1
        print(f"PASS: {message}")

    def warn(self, message):
        self.warnings += 1
        print(f"WARN: {message}")

    def fail(self, message):
        self.failures += 1
        print(f"FAIL: {message}")


def normalize_base_url(value):
    return value.rstrip("/")


def display_url(url):
    parsed = urlparse(url)
    path = parsed.path or "/"
    if parsed.query:
        path += f"?{parsed.query}"
    return path


def absolute_url(base_url, path):
    return urljoin(base_url + "/", path.lstrip("/"))


def normalized_text(value):
    return " ".join((value or "").split())


def request_once(url):
    opener = build_opener(NoRedirect)
    req = Request(url, headers={"User-Agent": "Bellevue SEO Live Audit/1.0"})
    try:
        with opener.open(req, timeout=TIMEOUT) as response:
            body = response.read()
            final_url = response.geturl()
            return {
                "status": response.getcode(),
                "url": final_url,
                "headers": response.headers,
                "body": body,
                "error": None,
            }
    except HTTPError as exc:
        body = exc.read()
        return {
            "status": exc.code,
            "url": url,
            "headers": exc.headers,
            "body": body,
            "error": None,
        }
    except URLError as exc:
        return {"status": None, "url": url, "headers": {}, "body": b"", "error": str(exc.reason)}


def fetch_with_redirects(url, max_redirects=10):
    chain = []
    current = url
    for _ in range(max_redirects + 1):
        response = request_once(current)
        chain.append(response)
        status = response["status"]
        location = response["headers"].get("Location") if response["headers"] else None
        if response["error"] or status not in {301, 302, 303, 307, 308}:
            return response, chain, False
        if not location:
            return response, chain, False
        next_url = urljoin(current, location)
        if next_url in [item["url"] for item in chain]:
            return response, chain, True
        current = next_url
    return chain[-1], chain, True


def body_text(response):
    content_type = response["headers"].get("Content-Type", "")
    charset = "utf-8"
    if "charset=" in content_type:
        charset = content_type.split("charset=", 1)[1].split(";", 1)[0].strip()
    return response["body"].decode(charset or "utf-8", errors="replace")


def check_canonical_pages(results, base_url):
    print("Canonical Pages")
    for page in PAGES:
        expected_url = page["canonical"]
        request_url = absolute_url(base_url, page["path"])
        response, chain, loop = fetch_with_redirects(request_url)
        label = page["label"]
        final_url = chain[-1]["url"]

        if loop:
            results.fail(f"{label}: redirect loop when requesting {expected_url}")
            continue
        if response["error"]:
            results.fail(f"{label}: request failed for {expected_url}: {response['error']}")
            continue
        if response["status"] != 200:
            results.fail(f"{label}: expected final HTTP 200, got {response['status']}")
            continue
        if final_url != expected_url:
            results.fail(f"{label}: final URL {final_url} does not match canonical {expected_url}")
            continue

        html = body_text(response)
        parser = PageParser()
        parser.feed(html)
        page_failed = False
        checks = [
            (normalized_text(parser.title) == page["title"], f"title mismatch: {normalized_text(parser.title)!r}"),
            (parser.description == page["description"], "meta description mismatch"),
            (parser.canonical == page["canonical"], f"canonical href mismatch: {parser.canonical!r}"),
            (len(parser.h1s) == 1, f"expected exactly one H1, found {len(parser.h1s)}"),
        ]
        h1s = [normalized_text(h1) for h1 in parser.h1s]
        if len(h1s) == 1:
            checks.append((h1s[0] == page["h1"], f"H1 mismatch: {h1s[0]!r}"))
        checks.append((len(parser.ld_json) == 1, f"expected exactly one JSON-LD block, found {len(parser.ld_json)}"))
        if len(parser.ld_json) == 1:
            try:
                json.loads(parser.ld_json[0])
            except json.JSONDecodeError as exc:
                checks.append((False, f"JSON-LD parse failure: {exc}"))

        for ok, message in checks:
            if not ok:
                results.fail(f"{label}: {message}")
                page_failed = True
        if not page_failed:
            results.pass_(f"{label}: {expected_url} returned 200 with expected metadata, H1, and JSON-LD")


def check_redirect_set(results, base_url, label, suffix):
    for page in PAGES[1:]:
        source = absolute_url(base_url, page["path"] + suffix)
        target = page["canonical"]
        response, chain, loop = fetch_with_redirects(source)
        first_status = chain[0]["status"]
        final_url = chain[-1]["url"]
        source_label = display_url(source)

        if loop:
            results.fail(f"{label}: {source_label} creates a redirect loop")
        elif response["error"]:
            results.fail(f"{label}: {source_label} request failed: {response['error']}")
        elif first_status in {301, 308} and final_url == target and response["status"] == 200:
            results.pass_(f"{label}: {source_label} redirects permanently to {target}")
        elif first_status in {302, 307} and final_url == target and response["status"] == 200:
            results.warn(f"{label}: {source_label} redirects temporarily to {target}")
        elif first_status == 200 and final_url == source:
            results.fail(f"{label}: {source_label} returns 200 instead of redirecting to {target}")
        else:
            results.fail(f"{label}: {source_label} expected redirect to {target}, got first {first_status}, final {final_url}")


def check_redirects(results, base_url):
    print("\nRedirects")
    check_redirect_set(results, base_url, ".html variant", ".html")
    check_redirect_set(results, base_url, "Trailing slash variant", "/")


def check_robots(results, base_url):
    print("\nrobots.txt")
    url = absolute_url(base_url, "/robots.txt")
    response, chain, loop = fetch_with_redirects(url)
    if loop:
        results.fail("robots.txt: redirect loop")
        return
    if response["error"]:
        results.fail(f"robots.txt: request failed: {response['error']}")
        return
    if response["status"] != 200:
        results.fail(f"robots.txt: expected HTTP 200, got {response['status']}")
        return
    text = body_text(response)
    failed = False
    for required in [
        "User-agent: *",
        "Allow: /",
        "Sitemap: https://thebellevuehomes.com/sitemap.xml",
    ]:
        if required not in text:
            results.fail(f"robots.txt: missing {required}")
            failed = True
    if "Disallow: /" in text:
        results.fail("robots.txt: contains Disallow: /")
        failed = True
    if not failed:
        results.pass_("robots.txt returned 200 with required crawl directives")


def check_sitemap(results, base_url):
    print("\nsitemap.xml")
    url = absolute_url(base_url, "/sitemap.xml")
    response, chain, loop = fetch_with_redirects(url)
    if loop:
        results.fail("sitemap.xml: redirect loop")
        return
    if response["error"]:
        results.fail(f"sitemap.xml: request failed: {response['error']}")
        return
    if response["status"] != 200:
        results.fail(f"sitemap.xml: expected HTTP 200, got {response['status']}")
        return
    try:
        root = ET.fromstring(response["body"])
    except ET.ParseError as exc:
        results.fail(f"sitemap.xml: XML parse failure: {exc}")
        return

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [loc.text for loc in root.findall("sm:url/sm:loc", ns)]
    failed = False
    if urls != EXPECTED_SITEMAP_URLS:
        results.fail(f"sitemap.xml: loc values mismatch: {urls!r}")
        failed = True
    if any("www.thebellevuehomes.com" in item for item in urls):
        results.fail("sitemap.xml: contains www URL")
        failed = True
    if any(".html" in item for item in urls):
        results.fail("sitemap.xml: contains .html URL")
        failed = True
    if not failed:
        results.pass_("sitemap.xml returned 200 and contains exactly the approved canonical URLs")


def check_www_host(results):
    print("\nwww Host")
    source = "https://www.thebellevuehomes.com/about"
    target = "https://thebellevuehomes.com/about"
    response, chain, loop = fetch_with_redirects(source)
    first_status = chain[0]["status"]
    final_url = chain[-1]["url"]
    if loop:
        results.fail("www host: redirect loop")
    elif response["error"]:
        results.warn(f"www host: failed to resolve/connect: {response['error']}")
    elif first_status in {301, 308} and final_url == target and response["status"] == 200:
        results.pass_("www /about redirects permanently to apex canonical")
    elif first_status in {302, 307} and final_url == target and response["status"] == 200:
        results.warn("www /about redirects temporarily to apex canonical")
    elif first_status == 200 and final_url == source:
        results.fail("www /about returns 200 and may create a duplicate indexable host")
    else:
        results.fail(f"www /about expected redirect to {target}, got first {first_status}, final {final_url}")


def main():
    parser = argparse.ArgumentParser(description="Run production SEO checks against the deployed site.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"Base URL to audit. Default: {DEFAULT_BASE_URL}")
    args = parser.parse_args()

    base_url = normalize_base_url(args.base_url)
    results = Results()

    check_canonical_pages(results, base_url)
    check_redirects(results, base_url)
    check_robots(results, base_url)
    check_sitemap(results, base_url)
    check_www_host(results)

    print("\nSummary")
    print(f"Passes: {results.passes}")
    print(f"Warnings: {results.warnings}")
    print(f"Failures: {results.failures}")
    if results.failures:
        print(f"SEO live audit failed: {results.failures} failure(s), {results.warnings} warning(s).")
        return 1
    print(f"SEO live audit passed: {results.passes} pass(es), {results.warnings} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
