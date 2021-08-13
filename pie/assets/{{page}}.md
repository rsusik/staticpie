---
route: ~~BASE_URL~~/{{page_name}}
title: {{page_name}} # provide the title
template: index.html # provide jinja2 template for this website
author: YOU
menu: 
    label: {{page_name}} # this label will appear in menu
    order: 2
panel:
  - type: toc # toc will be available
tags: 
  - put
  - some
  - tags
summary: Write some summary here
date: {{date}}
---

# Header

Some content

## Section 1

Some content

## Section 2

### Subsection 2.1

Some content

### Subsection 2.2

Some content