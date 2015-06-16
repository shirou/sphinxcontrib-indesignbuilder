# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
In-Design IDML builder

'''

requires = ['Sphinx>=1.0', 'setuptools']

setup(
    name='sphinxcontrib_indesignbuilder',
    version='0.0.2',
    url='http://github.com/shirou/sphinxcontrib-indesignbuilder',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-indesignbuilder',
    license='BSD',
    author='WAKAYAMA Shirou',
    author_email='shirou.faw@gmail.com',
    description='Sphinx indesign builder',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
