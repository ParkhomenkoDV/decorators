from setuptools import setup, find_packages
import time

name = 'decorators'

version = '2024.09.22.00.00.00'
#Y, m, d, H, M, S = time.strftime('%Y.%m.%d.%H.%M.%S', time.localtime()).split('.')  # конфликт версии .00.
#version = '.'.join([Y, M, d, f'0{str(int(H) + 1)}'[-2:], f'0{str(int(M) + 1)}'[-2:], f'0{str(int(S) + 1)}'[-2:]])

with open('README.md', 'rt', encoding='utf-8') as file:
    long_description = file.read()

with open('requirements.txt', 'rt') as file:
    install_requires = file.readlines()

setup(
    name=name,
    version=version,
    description='lib',
    long_description=long_description,
    long_description_content_type='text/markdown',  # если long_description = .md
    author='Daniil Andryushin',
    author_email='',
    url='https://github.com/ParkhomenkoDV/python_scripts',
    packages=[name],
    python_requires='>=3.8',
    install_requires=install_requires,
)
