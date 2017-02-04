"""Helpers related to robots.txt format."""

import os
import glob

from six.moves.urllib.parse import urljoin


def gen_sitemap_lines(context):
    """Generate lines for robots.txt.

    Warning
    -------
    Context passed to this function must be closed
    (via :py:meth:`paka.sitemaps.Context.close`).

    Parameters
    ----------
    context: paka.sitemaps.Context
        Context to take information from.

    Yields
    ------
    str
        Lines that reference sitemap indexes generated by
        context and are suitable for putting into robots.txt.

    See also
    --------
    `Specifying the sitemap location via robots.txt
    <https://www.sitemaps.org/protocol.html#submit_robots>`_

    """
    indexes = range(
        1, len(glob.glob(os.path.join(context.fs_root, "i*"))) + 1)
    for i in indexes:
        yield "Sitemap: {}".format(
            urljoin(context.base_url, "i{}.xml".format(i)))
