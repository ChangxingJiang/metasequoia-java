from distutils.core import setup

from setuptools import find_packages

with open("README.md", "r", encoding="UTF-8") as file:
    long_description = file.read()

setup(
    name="metasequoia-java",
    version="0.1.1",
    description="水杉 Java 解析器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="changxing",
    author_email="1278729001@qq.com",
    url="https://github.com/ChangxingJiang/metasequoia-sql",
    install_requires=[],
    license="MIT License",
    packages=[package for package in find_packages()
              if package.startswith("metasequoia_java") and not package.endswith("_test")],
    platforms=["all"],
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Natural Language :: Chinese (Simplified)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries"
    ]
)
