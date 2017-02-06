"""Sitemap and sitemap index building.

See also
--------
`sitemaps.org protocol <https://www.sitemaps.org/protocol.html>`_
has more information on format of XML this module generates.

"""

import os
import enum
import datetime

from six.moves.urllib.parse import urljoin
from lxml import etree as ET


PER_MAP = PER_INDEX = 50000
"""Maximum number of items."""

XMLNS = "http://www.sitemaps.org/schemas/sitemap/0.9"


class ChangefreqEnum(enum.Enum):
    """How frequently page is going to change."""

    always = 1
    hourly = 2
    daily = 3
    weekly = 4
    monthly = 5
    yearly = 6
    never = 7


class Context:
    """Incrementally constructs and saves sitemaps and indexes of them.

    This builder has few limitations:

    * sitemap indexes are used for any number of URLs, even below
      :py:const:`PER_MAP`
    * currently only counts of items inside sitemaps and indexes are
      considered (total size limitations are not respected yet)

    """

    changefreq = ChangefreqEnum

    def __init__(self, fs_root, base_url):
        """Create builder with FS root path and base URL.

        Parameters
        ----------
        fs_root: str
            Path to root dir for generated sitemaps and sitemap indexes.
        base_url: str
            URL of site these sitemaps and sitemap indexes belong to
            (e.g. ``http://example.org/``).

        """
        self.fs_root = fs_root
        self.base_url = base_url

        self._items = []
        self._items_count = 0

        self._num_maps = 1
        self._num_indexes = 1

    def add(self, path, lastmod=None, changefreq=None, priority=None):
        """Add page to sitemap.

        Parameters
        ----------
        path: str
            URL path of page (e.g. ``/something/``).
        lastmod: datetime.datetime
            Date & time of the last modification (must be UTC).
        changefreq: ChangefreqEnum
            How frequently page is likely to change.
        priority: float or str
            Priority of this path relative to other paths.

        """
        item = {"p": path}

        if lastmod:
            item["l"] = lastmod

        if changefreq:
            item["c"] = changefreq

        if priority is not None:
            if isinstance(priority, (float, int)):
                priority = "{:.1f}".format(priority)
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
        """Finish writing to file system.

        Make sure you always close builder, as this method
        ensures current in-memory data (if any) is also written.

        """
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
                lastmod_el.text = _format_dt(lastmod)
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
            _make_sitemap_name(self._num_indexes, self._num_maps))
        ET.ElementTree(root_el).write(
            fs_path, encoding="utf-8", xml_declaration=True)

    def _write_index(self):
        # Build XML.
        root_el = ET.Element("sitemapindex", {"xmlns": XMLNS})

        for i in range(1, self._num_maps + 1):
            name = _make_sitemap_name(self._num_indexes, i)

            map_el = ET.Element("sitemap")

            loc_el = ET.Element("loc")
            loc_el.text = urljoin(self.base_url, name)
            map_el.append(loc_el)

            lastmod_el = ET.Element("lastmod")
            lastmod_el.text = _format_dt(datetime.datetime.utcnow())
            map_el.append(lastmod_el)

            root_el.append(map_el)

        # Save XML.
        fs_path = os.path.join(
            self.fs_root, "i{}.xml".format(self._num_indexes))
        ET.ElementTree(root_el).write(
            fs_path, encoding="utf-8", xml_declaration=True)


def _format_dt(dt_obj):
    return dt_obj.strftime("%Y-%m-%dT%H:%M:%SZ")


def _make_sitemap_name(index_idx, map_idx):
    return "s{}-{}.xml".format(index_idx, map_idx)
