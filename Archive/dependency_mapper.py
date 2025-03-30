"""
Dependency Mapper

This script analyzes Python files to create a dependency map.
It starts from main.py and recursively maps all dependencies.
"""

import os
import re
import json
import ast
from typing import Dict, List, Set, Any, Optional, Tuple

class DependencyMapper:
    """Maps dependencies between Python files in a project."""

    def __init__(self, root_dir: str):
        """
        Initialize the dependency mapper.

        Args:
            root_dir: The root directory of the project
        """
        self.root_dir = root_dir
        self.dependency_map = {}
        self.processed_files = set()

        # Standard library modules to ignore
        self.std_lib_modules = {
            'os', 'sys', 'time', 'datetime', 'tkinter', 'sqlite3',
            'json', 're', 'ast', 'typing', 'calendar', 'pandas',
            'docx', 'pdfkit', 'smtplib', 'email', 'tempfile',
            'webbrowser', 'subprocess', 'math', 'random', 'logging',
            'collections', 'functools', 'itertools', 'pathlib',
            'shutil', 'glob', 'argparse', 'configparser', 'csv',
            'hashlib', 'uuid', 'socket', 'threading', 'multiprocessing',
            'queue', 'urllib', 'http', 'ftplib', 'ssl', 'xml', 'html',
            'unittest', 'pytest', 'doctest', 'pdb', 'traceback',
            'warnings', 'contextlib', 'abc', 'copy', 'enum', 'io',
            'pickle', 'shelve', 'dbm', 'zlib', 'gzip', 'zipfile',
            'tarfile', 'platform', 'ctypes', 'gc', 'inspect',
            'importlib', 'pkg_resources', 'setuptools', 'distutils',
            'venv', 'virtualenv', 'pip', 'wheel', 'base64', 'bz2',
            'codecs', 'crypt', 'curses', 'decimal', 'difflib',
            'filecmp', 'fnmatch', 'fractions', 'getopt', 'getpass',
            'gettext', 'grp', 'gzip', 'heapq', 'hmac', 'imaplib',
            'imp', 'keyword', 'linecache', 'locale', 'lzma',
            'mailbox', 'mimetypes', 'mmap', 'modulefinder', 'netrc',
            'numbers', 'operator', 'optparse', 'os.path', 'pprint',
            'pwd', 'py_compile', 'quopri', 'reprlib', 'rlcompleter',
            'sched', 'secrets', 'selectors', 'signal', 'site',
            'smtpd', 'sndhdr', 'spwd', 'statistics', 'string',
            'stringprep', 'struct', 'subprocess', 'sunau', 'symbol',
            'symtable', 'sysconfig', 'tabnanny', 'telnetlib', 'tempfile',
            'textwrap', 'this', 'timeit', 'token', 'tokenize', 'trace',
            'tty', 'turtle', 'types', 'unicodedata', 'uu', 'wave',
            'weakref', 'webbrowser', 'wsgiref', 'xdrlib', 'zipapp',
            'zipimport'
        }

        # Common third-party packages to ignore
        self.third_party_modules = {
            'numpy', 'pandas', 'matplotlib', 'seaborn', 'scipy', 'sklearn',
            'tensorflow', 'torch', 'keras', 'django', 'flask', 'fastapi',
            'requests', 'beautifulsoup4', 'bs4', 'lxml', 'sqlalchemy',
            'pymongo', 'redis', 'celery', 'pytest', 'unittest', 'nose',
            'pillow', 'opencv', 'cv2', 'pydantic', 'click', 'typer',
            'rich', 'tqdm', 'boto3', 'botocore', 'awscli', 'azure',
            'google', 'firebase', 'pymysql', 'psycopg2', 'pyodbc',
            'cx_Oracle', 'pyyaml', 'toml', 'configparser', 'dotenv',
            'pytest', 'unittest', 'mock', 'faker', 'factory_boy',
            'coverage', 'flake8', 'pylint', 'mypy', 'black', 'isort',
            'docx', 'pdfkit', 'reportlab', 'openpyxl', 'xlrd', 'xlwt',
            'xlsxwriter', 'pywin32', 'pyinstaller', 'cx_Freeze',
            'py2exe', 'pyqt5', 'pyside2', 'wxpython', 'kivy', 'pygame',
            'pyglet', 'pycairo', 'pygtk', 'pycrypto', 'cryptography',
            'bcrypt', 'passlib', 'jwt', 'oauth2', 'oauthlib', 'authlib',
            'scrapy', 'selenium', 'splinter', 'mechanize', 'twisted',
            'tornado', 'aiohttp', 'asyncio', 'uvicorn', 'gunicorn',
            'waitress', 'werkzeug', 'jinja2', 'mako', 'chameleon',
            'pyramid', 'zope', 'plone', 'wagtail', 'ckan', 'odoo',
            'sentry_sdk', 'raven', 'loguru', 'structlog', 'logging',
            'alembic', 'peewee', 'pony', 'tortoise', 'gino', 'piccolo',
            'marshmallow', 'cerberus', 'voluptuous', 'jsonschema',
            'graphene', 'strawberry', 'ariadne', 'graphql', 'grpc',
            'protobuf', 'thrift', 'avro', 'msgpack', 'cbor2', 'ujson',
            'orjson', 'simplejson', 'rapidjson', 'pyarrow', 'fastavro',
            'dask', 'xarray', 'numba', 'cython', 'pypy', 'jax', 'mxnet',
            'theano', 'caffe', 'paddlepaddle', 'transformers', 'spacy',
            'nltk', 'gensim', 'textblob', 'polyglot', 'stanfordnlp',
            'allennlp', 'fairseq', 'huggingface', 'tokenizers', 'sentencepiece',
            'wordcloud', 'networkx', 'igraph', 'pydot', 'pygraphviz',
            'plotly', 'bokeh', 'altair', 'ggplot', 'folium', 'geopandas',
            'shapely', 'fiona', 'pyproj', 'rasterio', 'gdal', 'cartopy',
            'basemap', 'osmnx', 'pysal', 'geopy', 'geocoder', 'reverse_geocoder',
            'pymc3', 'pystan', 'fbprophet', 'statsmodels', 'lifelines',
            'sympy', 'sage', 'mpmath', 'gmpy2', 'pycryptodome', 'paramiko',
            'fabric', 'invoke', 'ansible', 'salt', 'puppet', 'chef',
            'docker', 'kubernetes', 'openshift', 'helm', 'terraform',
            'pulumi', 'troposphere', 'cloudformation', 'boto', 'libcloud',
            'azure-sdk', 'google-cloud', 'firebase-admin', 'suds', 'zeep',
            'spyne', 'soaplib', 'pysimplesoap', 'pysftp', 'ftputil',
            'pyftpdlib', 'pyinotify', 'watchdog', 'pywin32', 'winreg',
            'win32api', 'win32con', 'win32gui', 'win32process', 'win32service',
            'pyautogui', 'pynput', 'pyperclip', 'clipboard', 'pyaudio',
            'sounddevice', 'pygame.mixer', 'simpleaudio', 'pydub', 'librosa',
            'ffmpeg', 'imageio', 'moviepy', 'opencv-python', 'scikit-image',
            'scikit-learn', 'xgboost', 'lightgbm', 'catboost', 'h2o',
            'pyspark', 'dask', 'ray', 'modin', 'vaex', 'datatable',
            'polars', 'cudf', 'cuml', 'cugraph', 'cuspatial', 'cupy',
            'jaxlib', 'tensorflow-gpu', 'torch.cuda', 'horovod', 'petastorm',
            'mlflow', 'wandb', 'tensorboard', 'sacred', 'neptune', 'comet_ml',
            'optuna', 'hyperopt', 'ray.tune', 'skopt', 'nevergrad', 'ax',
            'botorch', 'gpytorch', 'pyro', 'pymc', 'edward', 'zhusuan',
            'pystan', 'emcee', 'pomegranate', 'pgmpy', 'bayespy', 'pymc3',
            'pyro', 'numpyro', 'tensorflow_probability', 'pystan', 'arviz',
            'corner', 'getdist', 'astropy', 'sunpy', 'astroquery', 'astroml',
            'astropy.io', 'astropy.table', 'astropy.units', 'astropy.constants',
            'astropy.coordinates', 'astropy.time', 'astropy.wcs', 'astropy.io.fits',
            'astropy.io.ascii', 'astropy.io.votable', 'astropy.io.misc',
            'astropy.io.registry', 'astropy.io.fits', 'astropy.io.ascii',
            'astropy.io.votable', 'astropy.io.misc', 'astropy.io.registry',
            'astropy.io.fits', 'astropy.io.ascii', 'astropy.io.votable',
            'astropy.io.misc', 'astropy.io.registry', 'astropy.io.fits',
            'astropy.io.ascii', 'astropy.io.votable', 'astropy.io.misc',
            'astropy.io.registry', 'astropy.io.fits', 'astropy.io.ascii',
            'astropy.io.votable', 'astropy.io.misc', 'astropy.io.registry'
        }

    def get_absolute_path(self, file_path: str) -> str:
        """
        Get the absolute path for a file.

        Args:
            file_path: The file path, which may be relative

        Returns:
            The absolute path
        """
        if os.path.isabs(file_path):
            return file_path
        return os.path.abspath(os.path.join(self.root_dir, file_path))

    def get_relative_path(self, file_path: str) -> str:
        """
        Get the path relative to the root directory.

        Args:
            file_path: The file path

        Returns:
            The relative path
        """
        abs_path = self.get_absolute_path(file_path)
        rel_path = os.path.relpath(abs_path, self.root_dir)
        return rel_path

    def is_external_module(self, module_name: str) -> bool:
        """
        Check if a module is an external module (standard library or third-party).

        Args:
            module_name: The module name

        Returns:
            True if the module is external, False otherwise
        """
        # Check if the module is in the standard library or third-party packages
        first_part = module_name.split('.')[0]
        return first_part in self.std_lib_modules or first_part in self.third_party_modules

    def resolve_import_path(self, import_name: str, current_file: str) -> Optional[str]:
        """
        Resolve an import name to a file path.

        Args:
            import_name: The import name (e.g., 'ui.ui')
            current_file: The file containing the import

        Returns:
            The resolved file path, or None if not found
        """
        # Skip external modules
        if self.is_external_module(import_name):
            return None

        # Try different possible file paths
        possible_paths = []

        # 1. Direct import (module.py)
        possible_paths.append(f"{import_name.replace('.', '/')}.py")

        # 2. Package import (module/__init__.py)
        possible_paths.append(f"{import_name.replace('.', '/')}/__init__.py")

        # 3. From current directory
        current_dir = os.path.dirname(current_file)
        possible_paths.append(os.path.join(current_dir, f"{import_name.split('.')[-1]}.py"))

        # 4. Relative import (from parent directory)
        if '.' in current_file:
            parent_dir = os.path.dirname(current_file)
            possible_paths.append(os.path.join(parent_dir, f"{import_name.split('.')[-1]}.py"))

        # Check if any of the possible paths exist
        for path in possible_paths:
            abs_path = self.get_absolute_path(path)
            if os.path.exists(abs_path):
                return self.get_relative_path(abs_path)

        # If we couldn't resolve the import, log it
        print(f"Could not resolve import '{import_name}' in file '{current_file}'")
        return None

    def extract_imports(self, file_path: str) -> List[str]:
        """
        Extract imports from a Python file.

        Args:
            file_path: The path to the Python file

        Returns:
            A list of imported module names
        """
        abs_path = self.get_absolute_path(file_path)
        if not os.path.exists(abs_path):
            print(f"File not found: {abs_path}")
            return []

        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the file with ast
            tree = ast.parse(content)
            imports = []

            for node in ast.walk(tree):
                # Handle 'import x' and 'import x.y'
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)

                # Handle 'from x import y' and 'from x.y import z'
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            return imports

        except Exception as e:
            print(f"Error extracting imports from {file_path}: {str(e)}")
            return []

    def map_dependencies(self, start_file: str) -> Dict[str, List[str]]:
        """
        Map dependencies starting from a file.

        Args:
            start_file: The file to start mapping from

        Returns:
            A dictionary mapping files to their dependencies
        """
        rel_start_file = self.get_relative_path(start_file)
        self._map_dependencies_recursive(rel_start_file)
        return self.dependency_map

    def _map_dependencies_recursive(self, file_path: str) -> None:
        """
        Recursively map dependencies.

        Args:
            file_path: The file to map dependencies for
        """
        # Skip if already processed
        if file_path in self.processed_files:
            return

        # Mark as processed
        self.processed_files.add(file_path)

        # Extract imports
        imports = self.extract_imports(file_path)
        dependencies = []

        # Resolve imports to file paths
        for import_name in imports:
            resolved_path = self.resolve_import_path(import_name, file_path)
            if resolved_path and resolved_path != file_path:  # Avoid self-references
                dependencies.append(resolved_path)

        # Store dependencies
        self.dependency_map[file_path] = dependencies

        # Recursively map dependencies
        for dependency in dependencies:
            self._map_dependencies_recursive(dependency)

def main():
    """Main function to run the dependency mapper."""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Create a dependency mapper
    mapper = DependencyMapper(current_dir)

    # Map dependencies starting from main.py
    dependency_map = mapper.map_dependencies('main.py')

    # Save the dependency map to a JSON file
    output_file = 'dependency_map.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dependency_map, f, indent=2, sort_keys=True)

    print(f"Dependency map saved to {output_file}")

if __name__ == "__main__":
    main()