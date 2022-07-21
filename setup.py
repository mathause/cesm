from setuptools import find_packages, setup

# get version
with open("cesm/version.py") as f:
    line = f.readline().strip().replace(" ", "").replace('"', "")
    version = line.split("=")[1]
    __version__ = version

setup(
    name="cesm",
    version=__version__,
    description="cesm utilities",
    url="",
    author="Mathias Hauser",
    author_email="mathias.hauser@env.ethz.ch",
    license="MIT",
    packages=find_packages(),
    install_requires=["numpy", "PyYaml"],
    test_suite="nose.collector",
    tests_require=["nose"],
    zip_safe=False,
)
