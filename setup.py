from setuptools import setup, find_packages

setup(
    name="CD_PROJECT",
    version="1.0.0",
    description="A Python-based SLR parser that computes FIRST, FOLLOW sets and generates ACTION and GOTO tables.",
    author="Tony499370",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "streamlit",
        "pandas"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)