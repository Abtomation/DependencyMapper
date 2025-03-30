from setuptools import setup, find_packages

setup(
    name="dependency-mapper",
    version="0.1.0",
    description="A tool to analyze and visualize dependencies between Python files",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/dependency-mapper",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "visualization": ["networkx>=2.5", "matplotlib>=3.3.0"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "dependency-mapper=dependency_mapper_ui:main",
        ],
    },
)