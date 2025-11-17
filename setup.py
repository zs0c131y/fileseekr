"""Setup script for FileSeekr."""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

# Read requirements
requirements_file = Path(__file__).parent / 'requirements.txt'
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r') as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith('#')
        ]

setup(
    name='fileseekr',
    version='1.0.0',
    description='A smart search application for cross-device file searching',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='FileSeekr Team',
    author_email='',
    url='https://github.com/yourusername/fileseekr',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.8,<3.12',
    entry_points={
        'console_scripts': [
            'fileseekr=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Desktop Environment :: File Managers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    keywords='file search finder indexing nlp',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/fileseekr/issues',
        'Source': 'https://github.com/yourusername/fileseekr',
    },
)
