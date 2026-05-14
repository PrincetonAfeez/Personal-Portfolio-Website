"""Sitemaps for the core app."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return ["home", "projects:index", "about", "contact:index", "resume"]

    def location(self, item):
        return reverse(item)
