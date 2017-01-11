import os
import enum
import datetime

from six.moves.urllib.parse import urljoin
from lxml import etree as ET


PER_MAP = PER_INDEX = 50000
XMLNS = "http://www.sitemaps.org/schemas/sitemap/0.9"


class ChangefreqEnum(enum.Enum):
    always = 1
    hourly = 2
    daily = 3
    weekly = 4
    monthly = 5
    yearly = 6
    never = 7


class Context:
    """Incrementally constructs and saves sitemaps and indexes of them.
    Note: it targets large websites (> PER_MAP URLs), that's why it uses
    sitemap indexes initially. Small websites do not need sitemaps, anyway.

    """
    changefreq = ChangefreqEnum

    def __init__(self, fs_root, base_url):
        """
        Arguments (both required):
        fs_root: root dir for generated sitemaps and sitemap indexes
        base_url: URL of site these sitemaps and sitemap indexes belong to

        """
        self.fs_root = fs_root
        self.base_url = base_url

        self._items = []
        self._items_count = 0

        self._num_maps = 1
        self._num_indexes = 1

    def add(self, path, lastmod=None, changefreq=None, priority=None):
        """Add path to sitemap.

        Arguments:
        path: URL path (not URL; required)
        lastmod: date of the last modification (datetime; must be UTC)
        changefreq: how frequently page is likely to change
        priority: priority of this path relative to other paths

        """
        item = {"p": path}

        if lastmod:
            item["l"] = lastmod

        if changefreq:
            item["c"] = changefreq

        if priority:
            item["y"] = priority

        if self._items_count == PER_MAP:
            self._update()
        self._items.append(item)
        self._items_count += 1

    def _update(self, force=False):
        self._write_map()
        self._items = []
        self._items_count = 0

        if self._num_maps == PER_INDEX:
            self._write_index()
            self._num_indexes += 1
            self._num_maps = 1
        else:
            if force:
                self._write_index()
            self._num_maps += 1

    def close(self):
        self._update(force=True)

    def _write_map(self):
        # Build XML.
        root_el = ET.Element("urlset", {"xmlns": XMLNS})
        for item in self._items:
            url_el = ET.Element("url")

            loc_el = ET.Element("loc")
            loc_el.text = urljoin(self.base_url, item["p"])
            url_el.append(loc_el)

            lastmod = item.get("l")
            if lastmod:
                lastmod_el = ET.Element("lastmod")
                # Must be UTC.
                lastmod_el.text = self._format_dt(lastmod)
                url_el.append(lastmod_el)

            changefreq = item.get("c")
            if changefreq:
                changefreq_el = ET.Element("changefreq")
                changefreq_el.text = changefreq.name  # name of enum member
                url_el.append(changefreq_el)

            priority = item.get("y")
            if priority:
                priority_el = ET.Element("priority")
                priority_el.text = priority
                url_el.append(priority_el)

            root_el.append(url_el)

        # Save XML.
        fs_path = os.path.join(
            self.fs_root,
            self._make_sitemap_name(self._num_indexes, self._num_maps),
        )
        ET.ElementTree(root_el).write(
            fs_path,
            encoding="utf-8",
            xml_declaration=True,
        )

    def _format_dt(self, dt):
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _make_sitemap_name(self, idx, map):
        return "s{}-{}.xml".format(idx, map)

    def _write_index(self):
        # Build XML.
        root_el = ET.Element("sitemapindex", {"xmlns": XMLNS})

        for i in range(1, self._num_maps + 1):
            name = self._make_sitemap_name(self._num_indexes, i)

            map_el = ET.Element("sitemap")

            loc_el = ET.Element("loc")
            loc_el.text = urljoin(self.base_url, name)
            map_el.append(loc_el)

            lastmod_el = ET.Element("lastmod")
            lastmod_el.text = self._format_dt(datetime.datetime.utcnow())
            map_el.append(lastmod_el)

            root_el.append(map_el)

        # Save XML.
        fs_path = os.path.join(
            self.fs_root,
            "i{}.xml".format(self._num_indexes),
        )
        ET.ElementTree(root_el).write(
            fs_path,
            encoding="utf-8",
            xml_declaration=True,
        )
