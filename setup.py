from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name='FlightHopper',
    version='1.0.0',
    author='Tiancheng Jiao',
    author_email='jtc1246@outlook.com',
    url='https://github.com/jtc1246/FlightHopper',
    description='Search for cheaper transfer fights, where your destination is the transfer city.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['FlightHopper'],
    install_requires=['myHttp>=1.2.0'],
    python_requires='>=3.9',
    platforms=["all"],
    license='GPL-2.0 License'
)
