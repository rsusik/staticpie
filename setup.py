import io
from setuptools import setup, find_packages
from pie.pie import __version__

setup(
    name="staticpie",
    version=__version__,
    author="Robert Susik",
    author_email="robert.susik@gmail.com",
    options={"bdist_wheel": {"universal": True}},    
    license="GPLv3",
    description=(
        """."""
    ),
    long_description=io.open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    entry_points={},
    package_data={'': ['blog/*']},
    #include_package_data=True,
    package_dir={"": "."},
    packages=find_packages(where="."),
    url="https://github.com/rsusik/staticpie",
    classifiers=[
        "Topic :: Utilities",
    ],
)