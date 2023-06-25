---
name: Panel Index
title: NODEYEZ Panels
layout: default
groups:
  - Informational Panels
  - Bitcoin Panels
  - Lightning Panels
  - Mining Panels
  - Other Fun Panels
  - Composite Displays
---

# Panel Index

Click the links for panels you want more guidance on for configuring and running.

{% for groupname in page.groups %}
## {{ groupname }}

<table>

{% for item in site.docs %}
{% if item.panelgroup %}
{% unless page.name == item.name %}
{% if item.panelgroup == groupname %}
<tr>
<td width="65%"><a href="{{ item.url }}"><b>{{ item.name }}</b></a></td>
<td rowspan="2">
{% if item.imageurl %}
<img src="{{ item.imageurl }}" />
{% else %}
{% if item.images %}
{% for imageurl in item.images %}
<img src="{{ imageurl }}" />
{% endfor %}
{% else %}
no image defined
{% endif %}
{% endif %}
</td>
</tr>
<tr>
<td>
{% if item.description %}
{{ item.description }}
{% else %}
<i>no description for this panel is defined yet</i>
{% endif %}
</td>
</tr>
{% endif %}
{% endunless %}
{% endif %}
{% endfor %}

</table>

{% endfor %}


[Home](../) | [Back to Nodeyez User and Code]({% link _install_steps/4nodeyez.md %}) | [Continue to Slideshow]({% link _install_steps/6slideshow.md %})

