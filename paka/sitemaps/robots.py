import os
import glob

from six.moves.urllib.parse import urljoin


def gen_sitemap_lines(context):
    for i in range(
        1,
        len(glob.glob(os.path.join(context.fs_root, "i*"))) + 1
    ):
        yield "Sitemap: {}".format(
            urljoin(context.base_url, "i{}.xml".format(i)))
