from setuptools import setup, find_packages

VERSION = "0.1"

options = dict(
    name='scurvysin',
    version=VERSION,
    packages=find_packages(),
    license='MIT',
    description='Pip & conda wrapper / warper.',
    #long_description=__doc__.strip(),
    author='',
    author_email='',
    url='https://github.com/pythomec/scurvysin',
    # install_requires = [],
    python_requires="~=3.6",
    entry_points = {
        'console_scripts' : [
            "scurvy=scurvysin.cli:main"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ]
)
setup(**options)

