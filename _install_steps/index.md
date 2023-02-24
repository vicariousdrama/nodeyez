---
name: Install Steps
layout: default
---

# {{ page.name }}

<ol>
{% for item in site.install_steps %}
{% unless page.name == item.name %}
<li class="tag-h1"><a href="{{ item.url }}">{{ item.name }}</a></li>
{% endunless %}
{% endfor %}
</ol>

