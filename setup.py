from setuptools import setup

setup(
    name='steamguard',
    version='1.0.2',
    description='Simple python module to add a phone number to your steam account and enable mobile auth. Also generate steam guard codes.',
    license='MIT',
    author='th3poli',
    author_email='',
    keywords=['steam', 'mobile', 'auth', 'guard', 'steamcommunity'],
    url='https://github.com/th3poli/steamguard',
    install_requires=['requests', 'rsa']
)

# python setup.py sdist bdist_wheel
# pip install ./dist/steamguard-1.0.2.tar.gz --no-cache-dir
# python -m twine upload .\dist\*
