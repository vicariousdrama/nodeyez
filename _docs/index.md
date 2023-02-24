---
name: Documentation Index
layout: default
---

# Documentation Index

<ol>
{% for item in site.docs %}
{% if item.panelgroup %}
{% unless page.name == item.name %}
| {{ item.panelgroup }} | <a href="{{ item.url }}">{{ item.name }}</a> |
{% endunless %}
{% else %}
{% unless page.name == item.name %}
| {{ item.panelgroup }} | <a href="{{ item.url }}">{{ item.name }}</a> |
{% endunless %}
{% endif %}
{% endfor %}
</ol>


