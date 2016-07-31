from setuptools import setup, find_packages

setup(name='cesm',
      version='0.1.0',
      description="cesm utilities",
      url='',
      author='Mathias Hauser',
      author_email='mathias.hauser@env.ethz.ch',
      license='MIT',
      packages=find_packages(),
      install_requires=['numpy',
                        'PyYaml'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
