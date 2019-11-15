from setuptools import setup

setup(
    name='indexedlist',
    version='0.0.1',
    packages=['indexedlist'],
    url='https://github.com/jrhege',
    license='',
    author='Johnathon Hege',
    author_email='',
    description='Python list allowing for fast searches of elements',
    python_requires='>=3.6',
    install_requires=[
        'sortedcontainers>=2.1.0'
    ]
)
