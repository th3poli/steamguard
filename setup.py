from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='steamguard',
    version='1.0.6',
    description='Simple Python module to add a phone number to your steam account and enable mobile authentication. It also generates Steam Guard codes, send and confirm tradeoffer and much more!',
    long_description=readme,
    long_description_content_type="text/markdown",
    license='MIT',
    author='th3poli',
    author_email='',
    keywords=['steam', 'mobile', 'auth', 'guard', 'steamcommunity', 'tradeoffer'],
    url='https://github.com/th3poli/steamguard',
    install_requires=['requests', 'rsa', 'beautifulsoup4']
)

# python setup.py sdist bdist_wheel
# pip install ./dist/steamguard-1.0.5.tar.gz --no-cache-dir
# python -m twine upload .\dist\*
