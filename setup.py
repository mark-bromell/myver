import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='myver',
    version='0.0.1',
    author='Mark Bromell',
    author_email='markbromell.business@gmail.com',
    description='Development tool for configuring and altering software '
                'versions.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mark-bromell/myver',
    project_urls={
        'Issue Tracker': 'https://github.com/mark-bromell/myver/issues',
        'Source Code': 'https://github.com/mark-bromell/simbak',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'myver = myver.__main__:main',
        ],
    },
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'ruamel.yaml==0.17.17',
    ],
)
