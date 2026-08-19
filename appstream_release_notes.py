#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


class ReleaseNotesError(ValueError):
    pass


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_releases(text: str) -> list[ET.Element]:
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        fragment = re.sub(r"^\s*<\?xml[^>]*\?>", "", text, count=1)
        try:
            root = ET.fromstring(f"<releases>{fragment}</releases>")
        except ET.ParseError as error:
            raise ReleaseNotesError(f"could not parse AppStream XML: {error}") from error

    if local_name(root.tag) == "release":
        return [root]
    return [element for element in root.iter() if local_name(element.tag) == "release"]


def element_text(element: ET.Element) -> str:
    return " ".join("".join(element.itertext()).split())


def find_description(release: ET.Element) -> ET.Element | None:
    descriptions = [
        child for child in release if local_name(child.tag) == "description"
    ]
    if not descriptions:
        return None

    xml_lang = "{http://www.w3.org/XML/1998/namespace}lang"
    return next(
        (description for description in descriptions if xml_lang not in description.attrib),
        descriptions[0],
    )


def description_to_markdown(description: ET.Element) -> str:
    children = list(description)
    blocks: list[str] = []

    for index, child in enumerate(children):
        tag = local_name(child.tag)
        if tag == "p":
            text = element_text(child)
            if not text:
                continue
            next_tag = (
                local_name(children[index + 1].tag)
                if index + 1 < len(children)
                else None
            )
            if text.endswith(":") and next_tag in {"ul", "ol"}:
                blocks.append(f"### {text.removesuffix(':')}")
            else:
                blocks.append(f"- {text}")
        elif tag in {"ul", "ol"}:
            items = [
                element_text(item)
                for item in child
                if local_name(item.tag) == "li" and element_text(item)
            ]
            if not items:
                continue
            if tag == "ol":
                blocks.append("\n".join(f"{index}. {item}" for index, item in enumerate(items, 1)))
            else:
                blocks.append("\n".join(f"- {item}" for item in items))

    return "\n\n".join(blocks)


def extract_release_notes(version: str, text: str) -> str:
    version = version.removeprefix("v")
    releases = parse_releases(text)
    release = next(
        (release for release in releases if release.get("version") == version), None
    )
    if release is None:
        available = ", ".join(
            release.get("version", "<missing>") for release in releases
        )
        detail = f"; available versions: {available}" if available else ""
        raise ReleaseNotesError(f"release {version} was not found{detail}")

    description = find_description(release)
    markdown = description_to_markdown(description) if description is not None else ""
    return markdown or f"Release {version}."


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert one AppStream release description to Markdown."
    )
    parser.add_argument("--file", required=True, type=Path, help="AppStream XML path")
    parser.add_argument("--version", required=True, help="release version")
    parser.add_argument("--output", type=Path, help="write Markdown to this path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        text = args.file.read_text(encoding="utf-8")
        markdown = extract_release_notes(args.version, text)
        if args.output is None:
            print(markdown)
        else:
            if args.file.resolve() == args.output.resolve():
                raise ReleaseNotesError("input and output paths must differ")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(f"{markdown}\n", encoding="utf-8")
    except (OSError, ReleaseNotesError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
