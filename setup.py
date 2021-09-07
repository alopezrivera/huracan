import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="huracan",
    version="0.0.a2",
    author="Antonio Lopez Rivera",
    author_email="antonlopezr99@gmail.com",
    description="Open source, 0-dimensional, object-oriented airbreathing engine modelling package for preliminary analysis and design of airbreathing engines, divulgation and educational purposes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alopezrivera/huracan",
    packages=setuptools.find_packages(),
    install_requires=[
        "Python-Alexandria",
        "mpl_plotter"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
