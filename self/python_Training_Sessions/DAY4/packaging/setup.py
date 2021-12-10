from setuptools import find_packages, setup
setup(
    name='flaskr',
    version='1.0.0',
    #Please keep in mind that you have to list subpackages explicitly. 
    #If you want setuptools to lookup the packages for you automatically
    #which py pkg to package, based on current dir 
    packages=find_packages(),
    include_package_data=True,  # checks  MANIFEST.in
    zip_safe=False, #setuptools to install your project as a directory rather than as a zipfile
    install_requires=[
        'flask',
    ],
)
