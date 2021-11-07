import setuptools

requirements = ['PyYaml', 'requests']

with open("README.md", 'r', encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name='gigrator',
    version='1.0.2',
    author='K8sCat',
    author_email='k8scat@gmail.com',
    description='Git repositories migration tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/k8scat/gigrator',
    packages=setuptools.find_packages(),
    entry_points={'console_scripts': ['gigrator = gigrator.gigrator:main']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    python_requires='>=3.6',
)
