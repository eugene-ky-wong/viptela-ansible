import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ansible-viptela",
    version="0.0.1",
    author="Eugene KY Wong",
    author_email="morphyme@gmail.com",
    description="This is the Cisco Viptela Ansible SDK",
    long_description=This is the Cisco Viptela Ansible SDK which allows execution through Ansible,
    long_description_content_type="text/markdown",
    url="https://github.com/eugene-ky-wong/viptela-ansible",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: BSD-3-Clause",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        "requests",
        "viptela-python>=0.0.1",
        "ansible"
    ],
    python_requires='~=2.7'
)

