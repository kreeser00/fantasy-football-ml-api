from setuptools import setup, find_packages

setup(
    name="ml-fantasy-football-model",
    version="1.0.0",
    author="Ken Reeser",
    author_email="kreeser@hotmail.com",
    description="A machine learning model for predicting my football teams every year.",
    package_dir={'': 'app'},
    packages=find_packages("app"),
    url='https://bitbucket.org/<<appropriate-end-point>>',
    package_data={'data': ['*.pkl']}
)
