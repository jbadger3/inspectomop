import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

#load version info
with open('inspectomop/VERSION.txt') as fh:
	version = fh.read().strip()
print(version)
setuptools.setup(
        #descriptors
        name='inspectomop',
        version=version,
        description='Database query tool for the OMOP Common Data Model',
        long_description=long_description,
        long_description_content_type="text/markdown",
        author='Jonathan Badger',
        author_email='jonathancbadger@gmail.com',
        url='https://github.com/jbadger3/inspectomop',
        classifiers=[
            'Programming Language :: Python :: 3',
            'Operating System :: OS Independent',
            'License :: OSI Approved :: GNU Affero General Public License v3',
            'Development Status :: 4 - Beta'
            ],

        #extra_inclustions
        packages=setuptools.find_packages(),
        package_data={'inspectomop': ['VERSION.txt','test/*.sqlite3']},

        #requirements/dependencies
        python_requires='>=3.0',
        install_requires=['sqlalchemy>=1.2','pandas'],

        )
