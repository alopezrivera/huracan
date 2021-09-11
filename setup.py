import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="huracan",
    version="0.0.1.post1",
    author="Antonio Lopez Rivera",
    author_email="antonlopezr99@gmail.com",
    description="Open source, 0-dimensional, object-oriented airbreathing engine modelling package for preliminary analysis and design of airbreathing engines, divulgation and educational purposes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alopezrivera/huracan",
    packages=setuptools.find_packages(),
    install_requires=[
        "numpy>=1.21.2",
        "Python-Alexandria>=2.0.0",
        "mpl_plotter>=4.0.2"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
