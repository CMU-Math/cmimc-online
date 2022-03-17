from setuptools import setup

setup(
    name='cmimc_programming_grading', 
    version='1.0.0',
    packages=['cmimc_programming_grading', 'cmimc_programming_grading.protos'],
    entry_points= {
        'console_scripts': [
            'cmimc_programming_grading_server = cmimc_programming_grading.server:main'
        ]
    },
    install_requires = [
        'grpcio',
    ]
)