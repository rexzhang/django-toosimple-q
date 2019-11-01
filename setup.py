import os
import re

from setuptools import setup, find_packages


def get_version(*file_paths):
    """Retrieves the version from django_toosimple_q/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("django_toosimple_q", "__init__.py")

setup(
    name='django-toosimple-q',
    version=version,
    description="""A simplistic task queue and cron-like scheduler for Django""",
    author='Olivier Dalang',
    author_email='olivier.dalang@gmail.com',
    url='https://github.com/olivierdalang/django-toosimple-q',
    packages=find_packages(),
    include_package_data=True,
    install_requires=open('requirements.txt').readlines(),
    license="MIT",
    zip_safe=False,
    keywords='django-toosimple-q',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
)
