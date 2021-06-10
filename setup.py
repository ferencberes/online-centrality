from setuptools import find_packages, setup

install_requires=[
'numpy',
'pandas',
'scipy',
'networkx',
'matplotlib',
'seaborn',
'datetime',
'numexpr',#?
'editdistance',#?
'pytz',#?
]

setup_requires = ['pytest-runner']

tests_require = [
#'codecov',
'pytest',
'pytest-cov',
]

setup(
  name='temporalkatz',
  packages = find_packages(),
  version='0.1.0',
  description='Temporal-Katz centrality research related code repository',
  url='https://link.springer.com/article/10.1007/s41109-018-0080-5',
  author='Ferenc Beres',
  author_email='fberes@info.ilab.sztaki.hu',
  install_requires=install_requires,
  setup_requires=setup_requires,
  tests_require=tests_require,
)
