import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spacys_pos_tagging", version="0.0.1", author="João Barreira, Mafalda Nunes",
    author_email="a73831@alunos.uminho.pt, a77364@alunos.uminho.pt",
    description="Web app and terminal client to use spaCy's features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/barreira/spacys_pos_tagging",
    packages=setuptools.find_packages(),
    scripts=['spacys_pos_tagging/bin/spacys_features.py'],
    include_package_date=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Natural Language Processing"
    ],
    entry_points={
        'console_scripts': [
            'execute=spacys_pos_tagging.app:execute'
        ]
    },
    install_requires=['Flask', 'spacy', 'matplotlib', 'prettytable']
)