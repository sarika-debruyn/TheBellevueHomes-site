#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

PAGES = [
    {
        "label": "Home",
        "file": "site/index.html",
        "canonical": "https://thebellavuegroup.com/",
        "title": "Luxury Home Builders in Chicago | The Bellavue Group",
        "description": "The Bellavue Group builds refined custom homes and bespoke residences in Chicago, combining architectural detail, craftsmanship, and elevated residential design.",
        "h1": "Luxury Home Builders in Chicago",
        "links": ["/portfolio-1", "/gallery", "/contact"],
        "schema": {"Organization", "WebSite", "WebPage"},
    },
    {
        "label": "About",
        "file": "site/about.html",
        "canonical": "https://thebellavuegroup.com/about",
        "title": "About Our Chicago Luxury Home Builders | The Bellavue Group",
        "description": "Learn about The Bellavue Group, a Chicago residential development team creating refined custom homes with thoughtful design, craftsmanship, and enduring elegance.",
        "h1": "About The Bellavue Group",
        "links": ["/portfolio-1", "/contact"],
        "schema": {"WebPage", "BreadcrumbList"},
    },
    {
        "label": "Portfolio",
        "file": "site/portfolio-1.html",
        "canonical": "https://thebellavuegroup.com/portfolio-1",
        "title": "Chicago Luxury Home Portfolio | The Bellavue Group",
        "description": "View featured Bellavue Group homes in Lakeview and Lincoln Square, including completed and under-construction luxury residences in Chicago.",
        "h1": "Featured Chicago Luxury Home Projects",
        "links": ["/gallery", "/contact"],
        "schema": {"WebPage", "BreadcrumbList"},
    },
    {
        "label": "Gallery",
        "file": "site/gallery.html",
        "canonical": "https://thebellavuegroup.com/gallery",
        "title": "Luxury Home Design Gallery | The Bellavue Group",
        "description": "Explore Bellavue Group interiors, kitchens, bedrooms, bathrooms, living spaces, and custom residential details from luxury homes in Chicago.",
        "h1": "Luxury Home Design Gallery",
        "links": ["/portfolio-1", "/contact"],
        "schema": {"WebPage", "BreadcrumbList"},
    },
    {
        "label": "Testimonials",
        "file": "site/testimonials.html",
        "canonical": "https://thebellavuegroup.com/testimonials",
        "title": "Client Testimonials | The Bellavue Group",
        "description": "Read testimonials from buyers, brokers, and design professionals about The Bellavue Group’s craftsmanship, design vision, and Chicago luxury homes.",
        "h1": "Bellavue Group Testimonials",
        "links": ["/portfolio-1", "/contact"],
        "schema": {"WebPage", "BreadcrumbList"},
    },
    {
        "label": "Contact",
        "file": "site/contact.html",
        "canonical": "https://thebellavuegroup.com/contact",
        "title": "Contact The Bellavue Group | Chicago Luxury Home Builders",
        "description": "Contact The Bellavue Group to inquire about custom homes, luxury residential projects, and refined homebuilding in Chicago.",
        "h1": "Contact The Bellavue Group",
        "links": ["/portfolio-1", "/gallery"],
        "schema": {"WebPage", "BreadcrumbList"},
    },
]

APPROVED_ROUTES = {
    "/",
    "/about",
    "/portfolio-1",
    "/gallery",
    "/testimonials",
    "/contact",
    "/portfolio-collections/my-portfolio/custom-homes-showcase/",
    "/portfolio-collections/my-portfolio/house/",
    "/portfolio-collections/my-portfolio/wilson-2/",
    "/portfolio-collections/my-portfolio/wilson-1/",
    "/portfolio-collections/my-portfolio/oakdale-house/",
}

EXPECTED_SITEMAP_URLS = [
    "https://thebellavuegroup.com/",
    "https://thebellavuegroup.com/about",
    "https://thebellavuegroup.com/portfolio-1",
    "https://thebellavuegroup.com/gallery",
    "https://thebellavuegroup.com/testimonials",
    "https://thebellavuegroup.com/contact",
]

GENERIC_ALTS = {
    "image",
    "photo",
    "picture",
    "kitchen",
    "bedroom",
    "bathroom",
    "living room",
    "family room",
    "interior",
    "exterior",
}

FORBIDDEN_SCHEMA = {
    "LocalBusiness",
    "HomeAndConstructionBusiness",
    "Review",
    "AggregateRating",
    "FAQPage",
    "Service",
    "Product",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.in_title = False
        self.description = None
        self.canonical = None
        self.og = {}
        self.twitter = {}
        self.h1s = []
        self.in_h1 = False
        self.hrefs = []
        self.imgs = []
        self.ld_json = []
        self.in_ld = False
        self.ld_buffer = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        tag = tag.lower()
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            if attrs.get("name") == "description":
                self.description = attrs.get("content")
            if attrs.get("property", "").startswith("og:"):
                self.og[attrs["property"]] = attrs.get("content")
            if attrs.get("name", "").startswith("twitter:"):
                self.twitter[attrs["name"]] = attrs.get("content")
        elif tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        elif tag == "h1":
            self.in_h1 = True
            self.h1s.append("")
        elif tag == "a":
            href = attrs.get("href")
            if href:
                self.hrefs.append(href)
        elif tag == "img":
            self.imgs.append(attrs)
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


def normalized_text(value):
    return " ".join((value or "").split())


def add_issue(issues, file_path, message):
    issues.append(f"{file_path}: {message}")


def walk_json(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def schema_types(doc):
    found = set()
    for item in walk_json(doc):
        value = item.get("@type")
        if isinstance(value, str):
            found.add(value)
        elif isinstance(value, list):
            found.update(v for v in value if isinstance(v, str))
    return found


def jsonld_domain_values(doc):
    values = []
    for item in walk_json(doc):
        for key, value in item.items():
            if key in {"@id", "url", "item"} and isinstance(value, str) and "thebellavuegroup.com" in value:
                values.append(value)
    return values


def is_internal_href(href):
    parsed = urlparse(href)
    return not parsed.scheme and not parsed.netloc and href.startswith("/")


def audit_pages(issues):
    high_priority = []
    parsed_pages = []

    for page in PAGES:
        file_path = ROOT / page["file"]
        if not file_path.exists():
            add_issue(issues, page["file"], "page file is missing")
            continue

        parser = PageParser()
        parser.feed(file_path.read_text(encoding="utf-8"))
        parsed_pages.append((page, parser))

        if normalized_text(parser.title) != page["title"]:
            add_issue(issues, page["file"], f"title mismatch: {normalized_text(parser.title)!r}")
        if parser.description != page["description"]:
            add_issue(issues, page["file"], "meta description mismatch")
        if parser.canonical != page["canonical"]:
            add_issue(issues, page["file"], f"canonical mismatch: {parser.canonical!r}")
        if parser.og.get("og:title") != page["title"]:
            add_issue(issues, page["file"], "og:title mismatch")
        if parser.og.get("og:description") != page["description"]:
            add_issue(issues, page["file"], "og:description mismatch")
        if parser.og.get("og:url") != page["canonical"]:
            add_issue(issues, page["file"], "og:url mismatch")
        if parser.twitter.get("twitter:title") != page["title"]:
            add_issue(issues, page["file"], "twitter:title mismatch")
        if parser.twitter.get("twitter:description") != page["description"]:
            add_issue(issues, page["file"], "twitter:description mismatch")

        h1s = [normalized_text(h1) for h1 in parser.h1s]
        if len(h1s) != 1:
            add_issue(issues, page["file"], f"expected exactly one h1, found {len(h1s)}")
        elif h1s[0] != page["h1"]:
            add_issue(issues, page["file"], f"h1 mismatch: {h1s[0]!r}")

        hrefs = set(parser.hrefs)
        for required in page["links"]:
            if required not in hrefs:
                add_issue(issues, page["file"], f"missing required contextual/internal link href {required}")

        for href in parser.hrefs:
            if "www.thebellavuegroup.com" in href:
                add_issue(issues, page["file"], f"href uses www host: {href}")
            if is_internal_href(href):
                route = href.split("#", 1)[0].split("?", 1)[0]
                if route.endswith(".html"):
                    add_issue(issues, page["file"], f"internal href points to .html URL: {href}")
                if route in {"/assets/styles.css", "/assets/site.js"}:
                    continue
                if route.startswith("/assets/"):
                    continue
                if route not in APPROVED_ROUTES:
                    add_issue(issues, page["file"], f"internal href points to unapproved/missing route: {href}")

        for img in parser.imgs:
            src = img.get("src", "(missing src)")
            if "alt" not in img:
                add_issue(issues, page["file"], f"img missing alt: {src}")
            elif img.get("alt", "").strip().lower() in GENERIC_ALTS:
                add_issue(issues, page["file"], f"img has generic alt: {src}")
            if img.get("decoding") != "async":
                add_issue(issues, page["file"], f"img missing decoding=\"async\": {src}")
            if not img.get("width") or not img.get("height"):
                add_issue(issues, page["file"], f"img missing width/height: {src}")
            if img.get("fetchpriority") == "high":
                high_priority.append((page["file"], src, img.get("loading")))

        if len(parser.ld_json) != 1:
            add_issue(issues, page["file"], f"expected exactly one JSON-LD block, found {len(parser.ld_json)}")
        else:
            try:
                doc = json.loads(parser.ld_json[0])
            except json.JSONDecodeError as exc:
                add_issue(issues, page["file"], f"JSON-LD does not parse: {exc}")
            else:
                found_types = schema_types(doc)
                missing = page["schema"] - found_types
                if missing:
                    add_issue(issues, page["file"], f"JSON-LD missing schema types: {', '.join(sorted(missing))}")
                forbidden = found_types & FORBIDDEN_SCHEMA
                if forbidden:
                    add_issue(issues, page["file"], f"JSON-LD has forbidden schema types: {', '.join(sorted(forbidden))}")
                for value in jsonld_domain_values(doc):
                    if not value.startswith("https://thebellavuegroup.com"):
                        add_issue(issues, page["file"], f"JSON-LD URL/id is not canonical apex https: {value}")
                    if "www.thebellavuegroup.com" in value:
                        add_issue(issues, page["file"], f"JSON-LD URL/id uses www: {value}")

    if len(high_priority) != 1:
        add_issue(issues, "scoped HTML", f"expected exactly one fetchpriority=\"high\" image, found {len(high_priority)}")
    elif high_priority[0][2] != "eager":
        add_issue(issues, high_priority[0][0], f"priority image must use loading=\"eager\": {high_priority[0][1]}")

    return parsed_pages


def audit_robots(issues):
    path = SITE / "robots.txt"
    if not path.exists():
        add_issue(issues, "site/robots.txt", "file is missing")
        return
    text = path.read_text(encoding="utf-8")
    for required in [
        "User-agent: *",
        "Allow: /",
        "Sitemap: https://thebellavuegroup.com/sitemap.xml",
    ]:
        if required not in text:
            add_issue(issues, "site/robots.txt", f"missing required line: {required}")
    if "Disallow: /" in text:
        add_issue(issues, "site/robots.txt", "must not contain Disallow: /")


def audit_sitemap(issues):
    path = SITE / "sitemap.xml"
    if not path.exists():
        add_issue(issues, "site/sitemap.xml", "file is missing")
        return
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        add_issue(issues, "site/sitemap.xml", f"XML does not parse: {exc}")
        return
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [loc.text for loc in root.findall("sm:url/sm:loc", ns)]
    if urls != EXPECTED_SITEMAP_URLS:
        add_issue(issues, "site/sitemap.xml", f"loc values mismatch: {urls!r}")
    for url in urls:
        if "www.thebellavuegroup.com" in url:
            add_issue(issues, "site/sitemap.xml", f"contains www URL: {url}")
        if ".html" in url:
            add_issue(issues, "site/sitemap.xml", f"contains .html URL: {url}")


def audit_firebase(issues):
    path = ROOT / "firebase.json"
    if not path.exists():
        add_issue(issues, "firebase.json", "file is missing")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        add_issue(issues, "firebase.json", f"JSON does not parse: {exc}")
        return

    hosting = data.get("hosting")
    if isinstance(hosting, list):
        site_hosting = next((item for item in hosting if item.get("public") == "site"), None)
    elif isinstance(hosting, dict) and hosting.get("public") == "site":
        site_hosting = hosting
    else:
        site_hosting = None

    if not site_hosting:
        add_issue(issues, "firebase.json", "missing hosting configuration with public directory site")
        return
    if site_hosting.get("cleanUrls") is not True:
        add_issue(issues, "firebase.json", "hosting.cleanUrls must be true")
    if site_hosting.get("trailingSlash") is not False:
        add_issue(issues, "firebase.json", "hosting.trailingSlash must be false")


def main():
    issues = []
    audit_pages(issues)
    audit_robots(issues)
    audit_sitemap(issues)
    audit_firebase(issues)

    if issues:
        for issue in issues:
            print(f"FAIL: {issue}")
        print(f"SEO audit failed: {len(issues)} issue(s).")
        return 1

    print("SEO audit passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
