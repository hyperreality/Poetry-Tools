from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='poetrytools',
      version='0.2',
      description='Analyse rhyme scheme, metre and form of poems',
      long_description=readme(),
      author='L Tennant',
      url='http://github.com/hyperreality/Poetry-Tools',
      license='MIT',
      packages=['poetrytools'],
      install_requires=['python-levenshtein'],
      include_package_data=True
)
