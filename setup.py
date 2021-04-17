from setuptools import setup, find_packages

VERSION = '0.0.20'
DESCRIPTION = 'Python package meant to serialize/deserialize network packets.'
LONG_DESCRIPTION = 'Python package meant to serialize/deserialize network packets sent over the network. By specifying' \
                   'a format, the package will automatically extract data from a packet or insert data into a packet.'

# Setting up
setup(
    name="serializeme",
    version=VERSION,
    author="Jack Gisel, Justin Roosenschoon, Thai Truong",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],

    keywords=['python', 'network', 'packet', 'serialize', 'networking'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
