from setuptools import setup, find_packages

setup(
    name="animation",
    version="0.0.1",
    url="https://github.com/chalk-diagrams/animation",
    author="Dan Oneață",
    author_email="dan.oneata@gmail.com",
    description="Animations in Chalk",
    packages=find_packages(),
    install_requires=["numpy", "chalk-diagrams"],
)
