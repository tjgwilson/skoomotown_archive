from setuptools import setup, find_packages

setup(
    name='skoomtown_archive',
    version='0.1.0',
    packages=find_packages(where='packages'),
    package_dir={'': 'packages'},
    install_requires=[
        'rich>=13.0.0',
        'blessed>=1.20.0',
    ],
    entry_points={
        'console_scripts': [
            'skoomtown-archive=scripts.main:main',
        ],
    },
    python_requires='>=3.10',
)
