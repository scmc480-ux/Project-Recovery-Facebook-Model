from __future__ import annotations

from html.parser import HTMLParser


class TextOnlyHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if text:
            self.parts.append(text)


def html_to_lines(html_text: str) -> list[str]:
    parser = TextOnlyHTMLParser()
    parser.feed(html_text)
    lines: list[str] = []
    for part in parser.parts:
        if not lines or lines[-1] != part:
            lines.append(part)
    return lines
