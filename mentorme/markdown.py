"""Render user Markdown with escaped HTML and safe links."""

import markdown
import nh3


def render_markdown(content):
    renderer = markdown.Markdown()
    # Replace the removed safe_mode='escape' behavior without disabling Markdown.
    renderer.preprocessors.deregister('html_block')
    renderer.inlinePatterns.deregister('html')
    return nh3.clean(renderer.convert(content))
