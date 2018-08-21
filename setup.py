import setuptools
import inspectomop

with open('README.md', 'r') as fh:
    long_description = fh.read()
setuptools.setup(
        #descriptors
        name='inspectomop',
        version=inspectomop.__version__,
        description='Database query tool for the OMOP Common Data Model', 
        long_description=long_description,
        long_description_content_type="text/markdown",
        author='Jonathan Badger',
        author_email='jonathancbadger@gmail.com',
        url='https://github.com/jbadger3/inspectomop',
        classifiers=[
            'Programming Language :: Python :: 3',
            'Operating System :: OS Independent',
            ],

        #requirements/dependencies
        python_requires='>=3.0',
        isntall_requires=['sqlalchemy','pandas'],
        packages=setuptools.find_packages(),
        )

