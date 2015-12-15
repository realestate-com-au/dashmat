from setuptools import setup, find_packages
from python_dashing import VERSION

setup(
      name = "python-dashing"
    , version = VERSION
    , packages = find_packages('python_dashing', exclude=['tests'])
    , include_package_data = True

    , install_requires =
      [ "delfick_app==0.6.9"
      , "option_merge==0.9.9.2.2"
      , "input_algorithms==0.4.5.1"

      , "six"
      , "redis"
      , "croniter"
      , "requests"
      , "slumber"

      , "Flask==0.10.1"
      , "tornado==4.3"
      , "pyjade==3.1.0"
      , "pyYaml==3.10"
      ]

    , extras_require =
      { "tests":
        [ "noseOfYeti>=1.5.0"
        , "nose"
        , "mock==1.0.1"
        , "tox"
        ]
      }

    , entry_points =
      { 'console_scripts' :
        [ 'python-dashing = python_dashing.executor:main'
        ]
      }

    # metadata for upload to PyPI
    , url = "https://github.com/realestate-com-au/python-dashing"
    , author = "Stephen Moore"
    , author_email = "stephen.moore@rea-group.com"
    , description = "Application that reads yaml and serves up a pretty dashboard"
    , license = "MIT"
    , keywords = "dashboard"
    )

