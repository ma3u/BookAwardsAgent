from setuptools import setup, find_packages

setup(
    name="bookawards",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.1',
        'beautifulsoup4>=4.9.3',
        'python-dotenv>=0.15.0',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'bookawards=src.main:main',
        ],
    },
)
