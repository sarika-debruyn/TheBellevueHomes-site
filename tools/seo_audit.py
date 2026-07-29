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
        "canonical": "https://thebellevuehomes.com/",
        "title": "Luxury Home Builders in Chicago | The Bellevue Homes",
        "description": "The Bellevue Homes builds refined custom homes and bespoke residences in Chicago, combining architectural detail, craftsmanship, and elevated residential design.",
        "h1": "Luxury Home Builders in Chicago",
        "links": ["/portfolio-1", "/gallery", "/contact"],
        "schema": {"Organization", "WebSite", "WebPage", "FAQPage"},
    },
    {
        "label": "About",
        "file": "site/about.html",
        "canonical": "https://thebellevuehomes.com/about",
        "title": "About Our Chicago Luxury Home Builders | The Bellevue Homes",
        "description": "Learn about The Bellevue Homes, a Chicago residential development team creating refined custom homes with thoughtful design, craftsmanship, and enduring elegance.",
        "h1": "About The Bellevue Homes",
        "links": ["/portfolio-1", "/contact"],
        "schema": {"WebPage", "BreadcrumbList", "Person"},
    },
    {
        "label": "Portfolio",
        "file": "site/portfolio-1.html",
        "canonical": "https://thebellevuehomes.com/portfolio-1",
        "title": "Chicago Luxury Home Portfolio | The Bellevue Homes",
        "description": "View featured Bellevue Homes residences in Lakeview and Lincoln Square, including completed and under-construction luxury home projects in Chicago.",
        "h1": "Featured Chicago Luxury Home Projects",
        "links": ["/gallery", "/contact"],
        "schema": {"WebPage", "BreadcrumbList"},
    },
    {
        "label": "Gallery",
        "file": "site/gallery.html",
        "canonical": "https://thebellevuehomes.com/gallery",
        "title": "Luxury Home Design Gallery | The Bellevue Homes",
        "description": "Explore Bellevue Homes interiors, kitchens, bedrooms, bathrooms, living spaces, and custom residential details from luxury homes in Chicago.",
        "h1": "Luxury Home Design Gallery",
        "links": ["/portfolio-1", "/about", "/contact"],
        "schema": {"WebPage", "BreadcrumbList"},
    },
    {
        "label": "Testimonials",
        "file": "site/testimonials.html",
        "canonical": "https://thebellevuehomes.com/testimonials",
        "title": "Client Testimonials | The Bellevue Homes",
        "description": "Read testimonials from buyers, brokers, and design professionals about The Bellevue Homes' craftsmanship, design vision, and Chicago luxury homes.",
        "h1": "Bellevue Homes Testimonials",
        "links": ["/portfolio-1", "/gallery", "/about", "/contact"],
        "schema": {"WebPage", "BreadcrumbList"},
    },
    {
        "label": "Contact",
        "file": "site/contact.html",
        "canonical": "https://thebellevuehomes.com/contact",
        "title": "Contact The Bellevue Homes | Chicago Luxury Home Builders",
        "description": "Contact The Bellevue Homes to inquire about custom homes, luxury residential projects, and refined homebuilding in Chicago.",
        "h1": "Contact The Bellevue Homes",
        "links": ["/portfolio-1", "/gallery"],
        "schema": {"WebPage", "BreadcrumbList"},
    },
]

PROJECT_PAGES = [
    {
        "label": "Lakeview Custom Home Project",
        "file": "site/portfolio-collections/my-portfolio/custom-homes-showcase/index.html",
        "canonical": "https://thebellevuehomes.com/portfolio-collections/my-portfolio/custom-homes-showcase/",
        "title": "Lakeview Custom Home Project | The Bellevue Homes",
        "description": "View a Lakeview Bellevue Homes project with 4,400 square feet, 6 bedrooms, 4.5 baths, and published under-construction project details.",
        "h1": "Lakeview",
    },
    {
        "label": "Lakeview Completed Residence",
        "file": "site/portfolio-collections/my-portfolio/house/index.html",
        "canonical": "https://thebellevuehomes.com/portfolio-collections/my-portfolio/house/",
        "title": "Lakeview Completed Residence | The Bellevue Homes",
        "description": "View a completed Lakeview Bellevue Homes residence with 4,400 square feet, 6 bedrooms, 4.5 baths, and published portfolio imagery.",
        "h1": "Lakeview",
    },
    {
        "label": "Lincoln Square Residence Completed",
        "file": "site/portfolio-collections/my-portfolio/oakdale-house/index.html",
        "canonical": "https://thebellevuehomes.com/portfolio-collections/my-portfolio/oakdale-house/",
        "title": "Lincoln Square Residence Completed | The Bellevue Homes",
        "description": "View an under-construction Lincoln Square Bellevue Homes residence with 5,620 square feet, 6 bedrooms, and 5.5 baths.",
        "h1": "Lincoln Square",
    },
    {
        "label": "Lincoln Square 5,500 Sq Ft Residence",
        "file": "site/portfolio-collections/my-portfolio/wilson-1/index.html",
        "canonical": "https://thebellevuehomes.com/portfolio-collections/my-portfolio/wilson-1/",
        "title": "Lincoln Square 5,500 Sq Ft Residence | The Bellevue Homes",
        "description": "View a completed Lincoln Square Bellevue Homes residence with 5,500 square feet, 6 bedrooms, 5.5 baths, and published project imagery.",
        "h1": "Lincoln Square",
    },
    {
        "label": "Lincoln Square 6,200 Sq Ft Residence",
        "file": "site/portfolio-collections/my-portfolio/wilson-2/index.html",
        "canonical": "https://thebellevuehomes.com/portfolio-collections/my-portfolio/wilson-2/",
        "title": "Lincoln Square 6,200 Sq Ft Residence | The Bellevue Homes",
        "description": "View a completed Lincoln Square Bellevue Homes residence with 6,200 square feet, 7 bedrooms, 5.5 baths, and published project imagery.",
        "h1": "Lincoln Square",
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
    "https://thebellevuehomes.com/",
    "https://thebellevuehomes.com/about",
    "https://thebellevuehomes.com/portfolio-1",
    "https://thebellevuehomes.com/gallery",
    "https://thebellevuehomes.com/testimonials",
    "https://thebellevuehomes.com/contact",
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

def joined(*parts):
    return "".join(parts)


BLOCKED_SOURCE_STRINGS = [
    joined("OWNER", "_", "FULL", "_", "NAME"),
    joined("OWNER", "_", "ROLE", "_", "TITLE"),
    joined("OWNER", "_", "SHORT", "_", "BIO"),
    joined("OWNER", "_", "SAME", "_", "AS", "_", "URLS"),
    joined("REAL", "_", "OWNER", "_", "FULL", "_", "NAME"),
    joined("REAL", "_", "OWNER", "_", "ROLE", "_", "TITLE"),
    joined("REAL", "_", "OWNER", "_", "SHORT", "_", "BIO"),
    joined("REAL", "_", "OWNER", "_", "SAME", "_", "AS", "_", "URLS"),
    joined("APPROVED", "_", "OWNER", "_", "FULL", "_", "NAME"),
    joined("APPROVED", "_", "OWNER", "_", "ROLE", "_", "TITLE"),
    joined("APPROVED", "_", "OWNER", "_", "SHORT", "_", "BIO"),
    joined("APPROVED", "_", "OWNER", "_", "SAME", "_", "AS", "_", "URLS"),
    joined("place", "holder"),
    joined("red", "acted"),
    joined("T", "BD"),
    joined("TO", "DO"),
]

BLOCKED_OLD_BRAND_STRINGS = [
    joined("the", "bella", "vue", "group"),
    joined("The ", "Bella", "vue", " Group"),
    joined("Bella", "vue"),
]

OWNER_ENCODING_MARKERS = [
    joined("\\u005f", "OWNER"),
    joined("&#95;", "OWNER"),
    joined("_", "OWNER", "_"),
]

SOURCE_SCAN_SUFFIXES = {".html", ".json", ".py", ".md", ".txt"}

OWNER_NAME = "Anita Goyal"
OWNER_JOB_TITLE = "Designer and Real Estate Developer"
OWNER_DESCRIPTION = "Anita Goyal is a designer and real estate developer who leads The Bellevue Homes with a focus on refined residential design, thoughtful spatial planning, and elegant modern living. Her work brings together development discipline and a designer's eye for light, flow, proportion, and warmth, creating homes that feel sophisticated, functional, and deeply livable."
OWNER_ID = "https://thebellevuehomes.com/#owner"
ORGANIZATION_ID = "https://thebellevuehomes.com/#organization"

TESTIMONIALS_REQUIRED_COPY = [
    "Client Confidence in Design-Led Homes",
    "design-led residential development",
    "featured portfolio projects",
    "luxury home design gallery",
    "Anita Goyal",
    "contact The Bellevue Homes",
]

GALLERY_REQUIRED_COPY = [
    "Refined Interiors",
    "Kitchens and Gathering Spaces",
    "Baths and Finishes",
    "light, flow, proportion, and warmth",
    "design-led residential development",
]

HOME_FAQ_QUESTIONS = [
    "What types of homes does The Bellevue Homes create?",
    "What does designer-led residential development mean?",
    "Does The Bellevue Homes work on custom homes and transformations?",
    "Where can I see completed and in-progress projects?",
    "How do I start a conversation about a project?",
    "Who leads The Bellevue Homes?",
]

HOME_FAQ_ANSWERS = [
    "The Bellevue Homes creates custom estates, bespoke residences, and transformations for refined residential living in Chicago.",
    "Designer-led residential development brings planning, proportion, flow, and refined material thinking into the development process from the beginning.",
    "Yes. The Bellevue Homes presents custom estates, bespoke residences, and transformative renovations as part of its residential work.",
    "You can view published portfolio projects in Lakeview and Lincoln Square on the Chicago portfolio page and explore interior details in the luxury home design gallery.",
    "Use the contact page to inquire about custom homes, bespoke residences, transformations, or residential development opportunities.",
    "The Bellevue Homes is led by Anita Goyal, Designer and Real Estate Developer.",
]

FORBIDDEN_SCHEMA = {
    "LocalBusiness",
    "HomeAndConstructionBusiness",
    "Review",
    "AggregateRating",
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
        self.h2s = []
        self.in_h1 = False
        self.in_h2 = False
        self.hrefs = []
        self.imgs = []
        self.ld_json = []
        self.in_ld = False
        self.ld_buffer = []
        self.text_parts = []
        self.in_script = False
        self.in_style = False

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
        elif tag == "h2":
            self.in_h2 = True
            self.h2s.append("")
        elif tag == "a":
            href = attrs.get("href")
            if href:
                self.hrefs.append(href)
        elif tag == "img":
            self.imgs.append(attrs)
        elif tag == "script":
            self.in_script = True
            if attrs.get("type") == "application/ld+json":
                self.in_ld = True
                self.ld_buffer = []
        elif tag == "style":
            self.in_style = True

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
        elif tag == "h2":
            self.in_h2 = False
        elif tag == "script":
            if self.in_ld:
                self.ld_json.append("".join(self.ld_buffer))
                self.in_ld = False
            self.in_script = False
        elif tag == "style":
            self.in_style = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_h1 and self.h1s:
            self.h1s[-1] += data
        if self.in_h2 and self.h2s:
            self.h2s[-1] += data
        if self.in_ld:
            self.ld_buffer.append(data)
        elif not self.in_script and not self.in_style and data.strip():
            self.text_parts.append(data.strip())


def normalized_text(value):
    text = " ".join((value or "").split())
    for punct in (".", ",", ";", ":", "?", "!"):
        text = text.replace(f" {punct}", punct)
    return text


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
            if key in {"@id", "url", "item"} and isinstance(value, str) and "thebellevuehomes.com" in value:
                values.append(value)
    return values



def find_person_entity(doc):
    for item in walk_json(doc):
        item_type = item.get("@type")
        types = item_type if isinstance(item_type, list) else [item_type]
        if "Person" in types and item.get("@id") == OWNER_ID:
            return item
    return None


def entity_refers_to_org(value):
    if isinstance(value, dict):
        return value.get("@id") == ORGANIZATION_ID
    if isinstance(value, list):
        return any(entity_refers_to_org(item) for item in value)
    if isinstance(value, str):
        return value == ORGANIZATION_ID
    return False

def is_internal_href(href):
    parsed = urlparse(href)
    return not parsed.scheme and not parsed.netloc and href.startswith("/")


def source_files_to_scan():
    skip_dirs = {".git", ".claude", "node_modules", "__pycache__", joined("www.", "the", "bella", "vue", "group", ".com")}
    for item in ROOT.rglob("*"):
        if not item.is_file():
            continue
        if any(part in skip_dirs for part in item.parts):
            continue
        if item.suffix in SOURCE_SCAN_SUFFIXES or item.name in {"firebase.json", "package.json", ".firebaserc"}:
            yield item


def audit_source_owner_tokens(issues):
    for file_path in source_files_to_scan():
        rel_path = str(file_path.relative_to(ROOT))
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        for blocked in BLOCKED_SOURCE_STRINGS:
            if blocked in text:
                add_issue(issues, rel_path, "blocked owner source token is present")
        for marker in OWNER_ENCODING_MARKERS:
            if marker in text:
                add_issue(issues, rel_path, "encoded or constructed owner marker is present")
        text_lower = text.lower()
        for blocked in BLOCKED_OLD_BRAND_STRINGS:
            if blocked.lower() in text_lower:
                add_issue(issues, rel_path, "old brand/domain reference is present")
        if file_path.suffix == ".js" and "owner" in text.lower():
            if any(marker in text for marker in ("innerHTML", "textContent", "insertAdjacentHTML")):
                add_issue(issues, rel_path, "owner text appears to be injected by script")


def audit_pages(issues):
    high_priority = []
    parsed_pages = []

    for page in PAGES:
        file_path = ROOT / page["file"]
        if not file_path.exists():
            add_issue(issues, page["file"], "page file is missing")
            continue

        html = file_path.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(html)
        parsed_pages.append((page, parser))

        if page["label"] == "About":
            if OWNER_NAME not in html:
                add_issue(issues, page["file"], f"missing visible owner name: {OWNER_NAME}")
            if OWNER_JOB_TITLE not in html:
                add_issue(issues, page["file"], "missing visible owner job title")
            if OWNER_DESCRIPTION not in html:
                add_issue(issues, page["file"], "missing visible owner description")

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

        if page["label"] == "Home":
            visible_text = normalized_text(" ".join(parser.text_parts))
            if "Frequently Asked Questions" not in visible_text:
                add_issue(issues, page["file"], "missing homepage FAQ heading")
            for question in HOME_FAQ_QUESTIONS:
                if question not in visible_text:
                    add_issue(issues, page["file"], f"missing visible FAQ question: {question}")
            for answer in HOME_FAQ_ANSWERS:
                if answer not in visible_text:
                    add_issue(issues, page["file"], f"missing visible FAQ answer: {answer}")
        elif page["label"] == "Gallery":
            visible_text = normalized_text(" ".join(parser.text_parts))
            for required in GALLERY_REQUIRED_COPY:
                if required not in visible_text:
                    add_issue(issues, page["file"], f"missing required Gallery copy: {required}")
        elif page["label"] == "Testimonials":
            visible_text = normalized_text(" ".join(parser.text_parts))
            for required in TESTIMONIALS_REQUIRED_COPY:
                if required not in visible_text:
                    add_issue(issues, page["file"], f"missing required Testimonials copy: {required}")

        hrefs = set(parser.hrefs)
        for required in page["links"]:
            if required not in hrefs:
                add_issue(issues, page["file"], f"missing required contextual/internal link href {required}")

        for href in parser.hrefs:
            if "www.thebellevuehomes.com" in href:
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
                if page["label"] == "Home":
                    faq_entities = [
                        item for item in walk_json(doc)
                        if item.get("@type") == "FAQPage"
                    ]
                    if len(faq_entities) != 1:
                        add_issue(issues, page["file"], f"expected one FAQPage entity, found {len(faq_entities)}")
                    else:
                        questions = []
                        answers = []
                        for entity in faq_entities[0].get("mainEntity", []):
                            if isinstance(entity, dict) and entity.get("@type") == "Question":
                                questions.append(entity.get("name"))
                                answer = entity.get("acceptedAnswer", {})
                                if answer.get("@type") != "Answer" or not answer.get("text"):
                                    add_issue(issues, page["file"], f"FAQ question missing acceptedAnswer text: {entity.get('name')}")
                                else:
                                    answers.append(answer.get("text"))
                        if questions != HOME_FAQ_QUESTIONS:
                            add_issue(issues, page["file"], "FAQPage JSON-LD questions do not match visible FAQ questions")
                        if answers != HOME_FAQ_ANSWERS:
                            add_issue(issues, page["file"], "FAQPage JSON-LD answers do not match visible FAQ answers")
                elif "FAQPage" in found_types:
                    add_issue(issues, page["file"], "FAQPage JSON-LD is only expected on the homepage")
                if page["label"] == "About":
                    person = find_person_entity(doc)
                    if person is None:
                        add_issue(issues, page["file"], "JSON-LD missing Anita Goyal Person entity")
                    else:
                        if person.get("name") != OWNER_NAME:
                            add_issue(issues, page["file"], "owner Person name mismatch")
                        if person.get("jobTitle") != OWNER_JOB_TITLE:
                            add_issue(issues, page["file"], "owner Person jobTitle mismatch")
                        if person.get("description") != OWNER_DESCRIPTION:
                            add_issue(issues, page["file"], "owner Person description mismatch")
                        if "sameAs" in person:
                            add_issue(issues, page["file"], "owner Person must not include sameAs without approved URLs")
                        connected = any(
                            entity_refers_to_org(person.get(key))
                            for key in ("worksFor", "memberOf", "affiliation")
                        )
                        if not connected:
                            add_issue(issues, page["file"], "owner Person is not connected to The Bellevue Homes organization")

                for value in jsonld_domain_values(doc):
                    if not value.startswith("https://thebellevuehomes.com"):
                        add_issue(issues, page["file"], f"JSON-LD URL/id is not canonical apex https: {value}")
                    if "www.thebellevuehomes.com" in value:
                        add_issue(issues, page["file"], f"JSON-LD URL/id uses www: {value}")

    if len(high_priority) != 1:
        add_issue(issues, "scoped HTML", f"expected exactly one fetchpriority=\"high\" image, found {len(high_priority)}")
    elif high_priority[0][2] != "eager":
        add_issue(issues, high_priority[0][0], f"priority image must use loading=\"eager\": {high_priority[0][1]}")

    return parsed_pages



def audit_project_pages(issues):
    for page in PROJECT_PAGES:
        file_path = ROOT / page["file"]
        if not file_path.exists():
            add_issue(issues, page["file"], "project page file is missing")
            continue

        html = file_path.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(html)

        if normalized_text(parser.title) != page["title"]:
            add_issue(issues, page["file"], f"project title mismatch: {normalized_text(parser.title)!r}")
        if parser.description != page["description"]:
            add_issue(issues, page["file"], "project meta description mismatch")
        if parser.canonical != page["canonical"]:
            add_issue(issues, page["file"], f"project canonical mismatch: {parser.canonical!r}")

        h1s = [normalized_text(h1) for h1 in parser.h1s]
        if len(h1s) != 1:
            add_issue(issues, page["file"], f"expected exactly one project h1, found {len(h1s)}")
        elif h1s[0] != page["h1"]:
            add_issue(issues, page["file"], f"project h1 mismatch: {h1s[0]!r}")

        h2s = [normalized_text(h2) for h2 in parser.h2s if normalized_text(h2)]
        if not h2s:
            add_issue(issues, page["file"], "project page must include at least one h2")

        hrefs = set(parser.hrefs)
        for required in {"/portfolio-1", "/contact"}:
            if required not in hrefs:
                add_issue(issues, page["file"], f"missing project internal link href {required}")

        if len(parser.ld_json) != 1:
            add_issue(issues, page["file"], f"expected exactly one project JSON-LD block, found {len(parser.ld_json)}")
            continue

        try:
            doc = json.loads(parser.ld_json[0])
        except json.JSONDecodeError as exc:
            add_issue(issues, page["file"], f"project JSON-LD does not parse: {exc}")
            continue

        found_types = schema_types(doc)
        for required_type in {"WebPage", "BreadcrumbList"}:
            if required_type not in found_types:
                add_issue(issues, page["file"], f"project JSON-LD missing {required_type}")
        forbidden = found_types & FORBIDDEN_SCHEMA
        if forbidden:
            add_issue(issues, page["file"], f"project JSON-LD has forbidden schema types: {', '.join(sorted(forbidden))}")
        if "FAQPage" in found_types:
            add_issue(issues, page["file"], "FAQPage JSON-LD is only expected on the homepage")
        for value in jsonld_domain_values(doc):
            if not value.startswith("https://thebellevuehomes.com"):
                add_issue(issues, page["file"], f"project JSON-LD URL/id is not canonical apex https: {value}")
            if "www.thebellevuehomes.com" in value:
                add_issue(issues, page["file"], f"project JSON-LD URL/id uses www: {value}")


def audit_robots(issues):
    path = SITE / "robots.txt"
    if not path.exists():
        add_issue(issues, "site/robots.txt", "file is missing")
        return
    text = path.read_text(encoding="utf-8")
    for required in [
        "User-agent: *",
        "Allow: /",
        "Sitemap: https://thebellevuehomes.com/sitemap.xml",
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
        if "www.thebellevuehomes.com" in url:
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
    audit_source_owner_tokens(issues)
    audit_pages(issues)
    audit_project_pages(issues)
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
