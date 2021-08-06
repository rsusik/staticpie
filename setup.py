import io
from setuptools import setup, find_packages
from pie.pie import __version__

def get_requirements():
    with open("requirements.txt") as fp:
        return [req for req in (line.strip() for line in fp) if req and not req.startswith("#")]


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
    entry_points={
        "console_scripts": [
            "pie=pie:main",
        ],
    },
    package_data={'': ['blog/*']},
    install_requires=get_requirements(),
    package_dir={"": "."},
    packages=find_packages(where="."),
    url="https://github.com/rsusik/staticpie",
    classifiers=[
        "Topic :: Utilities",
    ],
)