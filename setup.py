import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycasso",
    version="0.0.1",
    author="David Dworetzky",
    author_email="djdworetz@gmail.com",
    description="Deep learning server for generating art",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DavidDworetzky/Pycasso",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	install_requires=[
          'tinydb',
		  'torch',
		  'matplotlib',
		  'torchvision'
    ],
)