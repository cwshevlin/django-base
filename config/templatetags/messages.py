from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_block_tag(takes_context=True)
def message_box(context, content, level):
    format_kwargs = {
        "level": level.lower(),
        "level_title": level.capitalize(),
        "content": content,
        "site": context.get("site", None),
    }
    result = """<div class="message-box message-box-{level}">
    <summary class="message-box-summary">{level_title}</summary>
    <div class="message-box-content">
        <p>{content}</p>
    </div>
</div>"""
    return format_html(result, **format_kwargs)
