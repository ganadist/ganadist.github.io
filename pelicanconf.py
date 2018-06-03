#!/usr/bin/env python
# -*- coding: utf-8 -*- #
# vim: ts=4 sw=4 sts=4 et ai

from __future__ import unicode_literals

AUTHOR = 'YOUNG HO CHA'
SITENAME = "Ganachoco's Blog"
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Asia/Seoul'

DEFAULT_LANG = 'ko'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
)

# Social widget
SOCIAL = (('github', 'http://github.com/ganadist'),
        ('slideshare', 'https://www.slideshare.net/ganachoco'),
        ('linkedin', 'http://www.linkedin.com/in/ganadist'),
        ('g+', 'https://plus.google.com/+YoungHoCha'),
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

THEME = 'themes/Flex'
#THEME = 'themes/blueidea'
DISQUS_SITENAME = 'ganadist-github-io'
SLUGIFY_SOURCE = 'basename'
TYPOGRIFY = True
DEFAULT_DATE_FORMAT = '%m/%d/%Y'
#DEFAULT_DATE_FORMAT = '%c'
GOOGLE_ANALYTICS = 'UA-120269954-1'

