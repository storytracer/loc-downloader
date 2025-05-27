from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="loc-downloader",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A CLI tool and library for downloading metadata and files from loc.gov",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/loc-downloader",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "pyrate-limiter>=3.0",
        "pydantic>=2.0",
        "tqdm>=4.65",
        "aiofiles>=23.0",
        "httpx>=0.24",
    ],
    entry_points={
        "console_scripts": [
            "loc-downloader=loc_downloader.cli:main",
        ],
    },
)