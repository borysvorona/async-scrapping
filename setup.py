from distutils.core import Extension, setup
from Cython.Build import cythonize

extensions = [
    Extension('extentions.patterns', ['./extentions/patterns.pyx'])
]

setup(
    name='App',
    ext_modules=cythonize(extensions)
)