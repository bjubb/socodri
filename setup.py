from setuptools import setup, find_packages
import socodri

setup(name='socodri',
      version=socodri.__version__,
      description='DR Insights by Socialcode Labs',
      author='Brennan Jubb',
      author_email='labs@socialcode.com',
      url='http://labs.socialcode.com',
      packages=find_packages(),
      classifiers=[
          'Framework :: Flask',
          'Development Status :: 1 - Alpha',
          'Environment :: Web Environment',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules', ],
      include_package_data=True,
      zip_safe=False,
      )
