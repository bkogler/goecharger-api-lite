from setuptools import setup  # type: ignore

setup(
    name='goecharger',
    version='1.0.0',
    packages=['goecharger'],
    url='https://github.com/bkogler/goecharger',
    license='MIT',
    author='bkogler',
    author_email='',
    description='Lightweight Python API for accessing go-eCharger EV wallboxes using local HTTP API v2',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="go-e EV wallbox Gemini flex HOMEfix HOME+ HTTP API v2",
    python_requires='>=3.10',
    install_requires=[
        'requests'
    ]
)
