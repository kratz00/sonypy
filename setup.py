from setuptools import setup


setup(name="sonypy",
      version='0.1',
      description='Remote Control of Sony Cameras',
      long_description='',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
      ],
      keywords='sony camera remote control a7 nex',
      url='http://github.com/storborg/sonypy',
      author='Scott Torborg',
      author_email='scott@cartlogic.com',
      install_requires=['requests'],
      license='MIT',
      packages=['sonypy'],
      zip_safe=False)
