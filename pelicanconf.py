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
        ('b.android.com', 'http://b.android.com'),
        ('d.android.com', 'https://d.android.com'),
        ('r.android.com', 'https://r.android.com'),
        ('s.android.com', 'https://s.android.com'),
        ('Andy Figure', 'https://shop.deadzebra.com/andy-green-edition-by-android-foundry/'),
)

# Social widget
SOCIAL = (('github', 'http://github.com/ganadist'),
          ('slideshare', 'https://www.slideshare.net/ganachoco/presentations'),
          ('linkedin', 'http://www.linkedin.com/in/ganadist'),
          )

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

THEME = 'themes/Flex'
#THEME = 'themes/blueidea'
DISQUS_SITENAME = 'ganadist-github-io'
#SLUGIFY_SOURCE = 'basename'
TYPOGRIFY = True
DEFAULT_DATE_FORMAT = '%m/%d/%Y'
#DEFAULT_DATE_FORMAT = '%c'
GOOGLE_ANALYTICS = 'UA-120269954-1'

STATIC_PATHS = ['static', ]

PLUGIN_PATHS = ['pelican-plugins']
PLUGINS = [
    'cjk-auto-spacing',
    'pelican_gist',
]

CJK_AUTO_SPACING_TITLE = True
