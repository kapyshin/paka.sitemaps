import sys
import setuptools


PY2 = sys.version_info.major == 2


def _get_install_requirements():
    requirements = ["six", "lxml"]
    if PY2:
        requirements.append("enum34")
    return requirements


def _get_testing_requirements():
    return ["backports.tempfile"] if PY2 else []


setuptools.setup(
    name="paka.sitemaps",
    version="1.2.4",
    packages=setuptools.find_packages(),
    install_requires=_get_install_requirements(),
    extras_require={"testing": _get_testing_requirements()},
    include_package_data=True,
    namespace_packages=["paka"],
    zip_safe=False,
    url="https://github.com/PavloKapyshin/paka.sitemaps",
    keywords="sitemap robots",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy"],
    license="BSD",
    author="Pavlo Kapyshin",
    author_email="i@93z.org")
