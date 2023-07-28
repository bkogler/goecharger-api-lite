from setuptools import setup # type: ignore

# read the contents of README.md file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='goecharger-api-lite',
    version='1.5.1',
    packages=['goecharger_api_lite'],
    url='https://github.com/bkogler/goecharger-api-lite',
    license='MIT',
    author='Bernhard Kogler',
    author_email='bernhard.kogler@supersonnig.org',
    description='Lightweight Python API for accessing go-eCharger EV wallboxes using local HTTP API v2',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="go-e EV wallbox electric charger Gemini flex HOMEfix HOME+ HTTP API v2",
    python_requires='>=3.10',
    install_requires=[
        'aiohttp',
        'aiodns',
    ]
)
