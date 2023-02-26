---
name: Panel Index
layout: default
groups:
  - Informational Panels
  - Bitcoin Panels
  - Lightning Panels
  - Mining Panels
  - Other Fun Panels
---

# Panel Index

You can click links for panels you are interested in configuring and running.

{% for groupname in page.groups %}
## {{ groupname }}

<table>

{% for item in site.docs %}
{% if item.panelgroup %}
{% unless page.name == item.name %}
{% if item.panelgroup == groupname %}
<tr>
<td><a href="{{ item.url }}">{{ item.name }}</a></td>
<td rowspan="2">
{% if item.imageurl %}
<img src="{{ item.imageurl }}" />
{% else %}
no image defined
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

