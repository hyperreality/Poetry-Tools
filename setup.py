from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='poetrytools',
      version='0.1',
      description='Functions for working with poetry',
      long_description=readme(),
      author='L Tennant',
      author_email='l.tennant@rocketmail.com',
      url='http://github.com/hyperreality/Poetry-Tools',
      license='GPL',
      packages=['poetrytools'],
      install_requires=['python-levenshtein'],
      include_package_data=True
)