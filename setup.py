from setuptools import setup, find_packages

setup(
    name             = 'DpmModule',
    version          = '1.0.1',
    description      = 'Python module for Maplestory calculation / simulation',
    author           = 'oleneyl',
    author_email     = 'meson3241@gmail.com',
    url              = 'https://github.com/oleneyl/maplestory_dpm_calc',
    install_requires = [ ],
    packages         = find_packages(),
    keywords         = ['game', 'maplestory', 'simulation'],
    python_requires  = '>=3',
    zip_safe=False,
    classifiers      = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)
