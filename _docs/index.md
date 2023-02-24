---
name: Documentation Index
layout: default
groups:
  - Informational Panels
  - Bitcoin Panels
  - Lightning Panels
  - Mining Panels
  - Other Fun Panels
---

# Documentation Index

{% for groupname in page.groups %}
## {{ groupname }}

{% for item in site.docs %}
{% if item.panelgroup %}
{% unless page.name == item.name %}
{% if item.panelgroup == groupname %}
-  <a href="{{ item.url }}">{{ item.name }}</a>
{% endif %}
{% endunloess %}
{% endif %}
{% endfor %}
{% endfor %}



