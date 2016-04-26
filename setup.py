from setuptools import setup

setup(name='cesm',
      version='0.1.0',
      description="cesm utilities",
      url='',
      author='Mathias Hauser',
      author_email='mathias.hauser@env.ethz.ch',
      license='MIT',
      packages=['cesm'],
      install_requires=['numpy',
                        'PyYaml'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
