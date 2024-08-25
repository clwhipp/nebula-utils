from setuptools import setup, find_packages

setup(
    name='Nebula Utils',
    version='0.1',
    description='Contains scripting to support maintenance of Nebula PKI.',
    long_description='',
    url='https://github.com/clwhipp/nebula-utils',
    packages=find_packages(
        exclude=['tests*']
    ),
    entry_points = {
        'console_scripts': [
            'nutils=nebula.command_line:main'
        ]
    },
    install_requires=[
        'click',
        'pyinstaller',
        'ruamel.yaml'
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-bdd"
        ]
    }
)