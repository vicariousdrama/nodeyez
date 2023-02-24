---
name: Documentation Index
layout: default
---

# Documentation

<ol>
{% for doc in site.docs %}
<li class="tag-h1"><a href="{{ doc.url }}"{{ doc.name }}</a></li>
{% endfor %}
</ol>


1. [Raspberry Pi Node]({% link _install_steps/install-1-raspberrypinode.md %})
2. [Display Screen]({% link _install_steps/install-2-displayscreen.md %})
3. [Python Dependencies]({% link _install_steps/install-3-pythondeps.md %})
4. [Nodeyez User and Config]({% link _install_steps/install-4-nodeyez.md %})
5. [Website Dashbaord]({% link _install_steps/install-5-websitedashboard.md %})
6. [Run at Startup]({% link _install_steps/install-6-runatstartup.md %})

---

[Home](../) | [Continue to Raspberry Pi Node]({% link _install_steps/install-1-raspberrypinode.md %})

