"""This module contains HTML utilities."""

from __future__ import annotations
import os
from typing import TextIO


def normalize_path(path: str) -> str:
    """Makes the path HTML readable."""
    return '/'.join(os.path.normpath(path).split(os.sep))


class HTMLWriter:
    """This class writes HTML files with auto indent."""
    def __init__(self, writer: TextIO, indent: int = 4) -> None:
        self.writer = writer
        if indent < 0:
            indent = 4
        self.indent = ' ' * indent
        self.indent_level = 0
        self.is_block = True
        self.has_inline = False

    def open_tag(
            self, tag: str, classes: list = [], **kwargs: str) -> HTMLWriter:
        full_tag = [tag]
        if classes:
            kwargs['class'] = ' '.join(classes)
        for key, value in kwargs.items():
            full_tag.append(f'{key}="{value}"')
        return self._write_text(f"<{' '.join(full_tag)}>")

    def open_block_tag(
            self, tag: str, classes: list = [], **kwargs: str) -> HTMLWriter:
        self._set_block()._write_indent()
        self.indent_level += 1
        return self.open_tag(tag, classes=classes, **kwargs)._write_newline()

    def open_body(self, classes: list = [], **kwargs: str) -> HTMLWriter:
        return self.open_block_tag('body', classes=classes, **kwargs)

    def open_div(self, classes: list = [], **kwargs: str) -> HTMLWriter:
        return self.open_block_tag('div', classes=classes, **kwargs)

    def open_footer(self, classes: list = [], **kwargs: str) -> HTMLWriter:
        return self.open_block_tag('footer', classes=classes, **kwargs)

    def open_head(self, classes: list = [], **kwargs: str) -> HTMLWriter:
        return self.open_block_tag('head', classes=classes, **kwargs)

    def open_heading(
            self, level: int, classes: list = [], **kwargs: str) -> HTMLWriter:
        return self.open_block_tag(f'h{level}', classes=classes, **kwargs)

    def open_horizontal_rule(
            self, classes: list = [], **kwargs: str) -> HTMLWriter:
        return (self.open_block_tag('hr', classes=classes, **kwargs)
                    .self_closing_block_tag())

    def open_html(self, classes: list = [], **kwargs: str) -> HTMLWriter:
        return self.open_block_tag('html', classes=classes, **kwargs)

    def open_paragraph(self, classes: list = [], **kwargs: str) -> HTMLWriter:
        return self.open_block_tag('p', classes=classes, **kwargs)

    def open_inline_tag(
            self, tag: str, classes: list = [], **kwargs: str) -> HTMLWriter:
        return self._set_inline().open_tag(tag, classes=classes, **kwargs)

    def open_hyperlink(
            self, href: str, target: str = '_blank', classes: list = [],
            **kwargs: str) -> HTMLWriter:
        return self.open_inline_tag(
            'a', classes=classes, href=href, target=target, **kwargs)

    def open_icon(
            self, href: str, classes: list = [], **kwargs: str) -> HTMLWriter:
        return (self.open_inline_tag(
                        'link', classes=classes, rel='icon', href=href,
                        type='image/icon type')
                    .self_close_inline_tag()
                    ._write_newline())

    def open_image(
            self, src: str, alt: str, classes: list = [],
            **kwargs: str) -> HTMLWriter:
        return (self.open_inline_tag(
                        'img', classes=classes, src=src, alt=alt, **kwargs)
                    .self_close_inline_tag())

    def open_javascript(
            self, src: str, classes: list = [], **kwargs: str) -> HTMLWriter:
        return self.open_inline_tag('script', classes=classes, src=src, **kwargs)

    def open_meta(self, classes: list = [], **kwargs: str) -> HTMLWriter:
        return (self.open_inline_tag('meta', classes=classes, **kwargs)
                    .self_close_inline_tag()
                    ._write_newline())

    def open_span(self, classes: list = [], **kwargs: str) -> HTMLWriter:
        return self.open_inline_tag('span', classes=classes, **kwargs)

    def open_stylesheet(
            self, href: str, classes: list = [], **kwargs: str) -> HTMLWriter:
        return (self.open_inline_tag(
                        'link', classes=classes, rel='stylesheet',
                        href=href, **kwargs)
                    .self_close_inline_tag()
                    ._write_newline())

    def open_title(self, classes: list = [], **kwargs: str) -> HTMLWriter:
        return self.open_inline_tag('title', classes=classes, **kwargs)

    def close_tag(self, tag: str) -> HTMLWriter:
        return self._write_text(f'</{tag}>')

    def close_block_tag(self, tag: str) -> HTMLWriter:
        return (self.self_closing_block_tag()
                    ._write_indent()
                    .close_tag(tag)
                    ._write_newline())

    def self_closing_block_tag(self) -> HTMLWriter:
        self._set_block()
        self.indent_level -= 1
        return self

    def close_body(self) -> HTMLWriter:
        return self.close_block_tag('body')

    def close_div(self) -> HTMLWriter:
        return self.close_block_tag('div')

    def close_footer(self) -> HTMLWriter:
        return self.close_block_tag('footer')

    def close_head(self) -> HTMLWriter:
        return self.close_block_tag('head')

    def close_heading(self, level: int) -> HTMLWriter:
        return self.close_block_tag(f'h{level}')

    def close_html(self) -> None:
        self.close_block_tag('html')
        self.writer.close()

    def close_paragraph(self) -> HTMLWriter:
        return self.close_block_tag('p')

    def close_inline_tag(self, tag: str) -> HTMLWriter:
        return self._set_inline().close_tag(tag)

    def self_close_inline_tag(self) -> HTMLWriter:
        return self._set_inline()

    def close_hyperlink(self) -> HTMLWriter:
        return self.close_inline_tag('a')

    def close_javascript(self) -> HTMLWriter:
        return self.close_inline_tag('script')._write_newline()

    def close_span(self) -> HTMLWriter:
        return self.close_inline_tag('span')

    def close_title(self) -> HTMLWriter:
        return self.close_inline_tag('title')._write_newline()

    def write_doctype(self) -> HTMLWriter:
        return self._write_text('<!DOCTYPE html>')._write_newline()

    def write_inner_text(self, text: str) -> HTMLWriter:
        return self._set_inline()._write_text(text)

    def _write_indent(self) -> HTMLWriter:
        return self._write_text(self.indent * self.indent_level)

    def _write_newline(self) -> HTMLWriter:
        self.has_inline=False
        return self._write_text('\n')

    def _write_text(self, text: str) -> HTMLWriter:
        self.writer.write(text)
        return self

    def _set_block(self) -> HTMLWriter:
        if self.has_inline:
            self._write_newline()
        self.is_block = True
        self.has_inline = False
        return self

    def _set_inline(self) -> HTMLWriter:
        if not self.has_inline:
            self._write_indent()
        self.is_block = False
        self.has_inline = True
        return self
