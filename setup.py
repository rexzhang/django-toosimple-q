import os
import re

from setuptools import find_packages, setup


def get_version(*file_paths):
    """Retrieves the version from django_toosimple_q/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="django-toosimple-q",
    version=get_version("django_toosimple_q", "__init__.py"),
    description="""A simplistic task queue and cron-like scheduler for Django""",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Olivier Dalang",
    author_email="olivier.dalang@gmail.com",
    url="https://github.com/olivierdalang/django-toosimple-q",
    packages=find_packages(),
    include_package_data=True,
    # TODO : once https://github.com/taichino/croniter/pull/171 is merged and requirements.txt is updated, re-enable parsing requirements.txt
    # install_requires=open("requirements.txt").readlines(),
    install_requires=[
        "django>=2.0",
        "django-picklefield~=2.0",
        "croniter @ https://github.com/olivierdalang/croniter/archive/f390dc00f41ef0b1cea7eec1ba328f1650d6c8dd.zip",
    ],
    license="MIT",
    zip_safe=False,
    keywords="django-toosimple-q",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django :: 2.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)
