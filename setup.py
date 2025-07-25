from setuptools import setup, find_packages

with open("requirements.txt") as requirements_file:
    requirements = [line.strip() for line in requirements_file if line.strip() and not line.startswith("#")]

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='Opera_Data_Processor',
    version='1.1.0',
    author=['Ross Scrimgeour', 'Emma Westlund'],
    author_email='your@email.com',
    description='Short description of your package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/your_project',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'Opera_Processor = OperaPhenixDataHandler.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
    ],
)
