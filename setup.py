from setuptools import setup, find_packages

setup(
    name='netatmo-shut-the-door',
    version='1.0.0',
    author_email='javier.ramirez.leiva0@gmail.com',
    description='CLI/Pip package for netatmo able to retrieve temperature from a netatmo room',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'netatmo = netatmo:cli.main' 
        ],
    },
    # Include additional package data (e.g., non-Python files)
    package_data={
        'configuration': ['configuration/*'],
    },
)