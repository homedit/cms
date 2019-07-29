import os
import re
from setuptools import setup, find_packages

pip_requires = os.path.join(os.getcwd(), 'requirements.txt')

REQUIRES=[
    'requests',
    'boto3',
    'flask',
    'flask-cors',
    'zappa'
]

setup(
    name='cms',
    version='0.0.1',
    license='MIT License',
    author='Amit Gandhi (DrawBuildPlay, LLC)',
    author_email='amit@drawbuildplay.com',
    keywords='Static Page Hugo CMS Editor, Amazon Cognito Authentication, Git Based CMS Backend',
    description='A Python API for content managing a Hugo based static website.',
    url='https://github.com/homedit/cms',
    install_requires=REQUIRES,
    packages = find_packages(),
    entry_points={
        'console_scripts': [
            'cms = cms.cmd:main'
        ]
    }
)
    
