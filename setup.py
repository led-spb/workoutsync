import setuptools
import workoutsync as module

setuptools.setup(
    name=module.__name,
    version=module.__version,
    author='Alexey Ponimash',
    author_email='alexey.ponimash@gmail.com',
    packages=setuptools.find_packages(),
)