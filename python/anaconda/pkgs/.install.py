# (c) 2012-2016 Continuum Analytics, Inc. / http://continuum.io
# All Rights Reserved
#
# conda is distributed under the terms of the BSD 3-clause license.
# Consult LICENSE.txt or http://opensource.org/licenses/BSD-3-Clause.
'''
We use the following conventions in this module:

    dist:        canonical package name, e.g. 'numpy-1.6.2-py26_0'

    ROOT_PREFIX: the prefix to the root environment, e.g. /opt/anaconda

    PKGS_DIR:    the "package cache directory", e.g. '/opt/anaconda/pkgs'
                 this is always equal to ROOT_PREFIX/pkgs

    prefix:      the prefix of a particular environment, which may also
                 be the root environment

Also, this module is directly invoked by the (self extracting) tarball
installer to create the initial environment, therefore it needs to be
standalone, i.e. not import any other parts of `conda` (only depend on
the standard library).
'''
import os
import re
import sys
import json
import shutil
import stat
from os.path import abspath, dirname, exists, isdir, isfile, islink, join
from optparse import OptionParser


on_win = bool(sys.platform == 'win32')
try:
    FORCE = bool(int(os.getenv('FORCE', 0)))
except ValueError:
    FORCE = False

LINK_HARD = 1
LINK_SOFT = 2  # never used during the install process
LINK_COPY = 3
link_name_map = {
    LINK_HARD: 'hard-link',
    LINK_SOFT: 'soft-link',
    LINK_COPY: 'copy',
}
SPECIAL_ASCII = '$!&\%^|{}[]<>~`"\':;?@*#'

# these may be changed in main()
ROOT_PREFIX = sys.prefix
PKGS_DIR = join(ROOT_PREFIX, 'pkgs')
SKIP_SCRIPTS = False
IDISTS = {
  "_license-1.1-py27_1": {
    "md5": "c0a9a25d11c559d3a2897df2f90a0b5c", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/_license-1.1-py27_1.tar.bz2"
  }, 
  "alabaster-0.7.10-py27_0": {
    "md5": "b537800e2ddf47cac2e7167b6b389d46", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/alabaster-0.7.10-py27_0.tar.bz2"
  }, 
  "anaconda-4.4.0-np112py27_0": {
    "md5": "17960aa0e7810b875ecd480a7882804d", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/anaconda-4.4.0-np112py27_0.tar.bz2"
  }, 
  "anaconda-client-1.6.3-py27_0": {
    "md5": "860f070e8f15e264c965cfa57feada52", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/anaconda-client-1.6.3-py27_0.tar.bz2"
  }, 
  "anaconda-navigator-1.6.2-py27_0": {
    "md5": "da4585a2f5de22e282f4c546d57496bc", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/anaconda-navigator-1.6.2-py27_0.tar.bz2"
  }, 
  "anaconda-project-0.6.0-py27_0": {
    "md5": "9acd33d55cfe331c4e13b9341474d2ce", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/anaconda-project-0.6.0-py27_0.tar.bz2"
  }, 
  "appnope-0.1.0-py27_0": {
    "md5": "1779b437f4e168c687106e13215f3bc9", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/appnope-0.1.0-py27_0.tar.bz2"
  }, 
  "appscript-1.0.1-py27_0": {
    "md5": "a1bbb6f9fc4a44223c9feef1cb67ac1e", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/appscript-1.0.1-py27_0.tar.bz2"
  }, 
  "asn1crypto-0.22.0-py27_0": {
    "md5": "1b9ceddc45e828902cd21b5ddac1dfe4", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/asn1crypto-0.22.0-py27_0.tar.bz2"
  }, 
  "astroid-1.4.9-py27_0": {
    "md5": "c902249bcbe125ac254110fa65eb304c", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/astroid-1.4.9-py27_0.tar.bz2"
  }, 
  "astropy-1.3.2-np112py27_0": {
    "md5": "cca5a26bb3e53654aa98837482db0dab", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/astropy-1.3.2-np112py27_0.tar.bz2"
  }, 
  "babel-2.4.0-py27_0": {
    "md5": "0f917dafee23f5d6d753dbaa04d21747", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/babel-2.4.0-py27_0.tar.bz2"
  }, 
  "backports-1.0-py27_0": {
    "md5": "dbb0f413e006ea05e959ed4e684cacfc", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/backports-1.0-py27_0.tar.bz2"
  }, 
  "backports_abc-0.5-py27_0": {
    "md5": "42469ec1262bec55e34044dd84ee0626", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/backports_abc-0.5-py27_0.tar.bz2"
  }, 
  "beautifulsoup4-4.6.0-py27_0": {
    "md5": "16fd50d551dcd00e0f483f1fb307f34b", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/beautifulsoup4-4.6.0-py27_0.tar.bz2"
  }, 
  "bitarray-0.8.1-py27_0": {
    "md5": "75762852faebc0b7dd81923c79347430", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/bitarray-0.8.1-py27_0.tar.bz2"
  }, 
  "blaze-0.10.1-py27_0": {
    "md5": "b0a484333b993af29b0c97c6332d5aff", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/blaze-0.10.1-py27_0.tar.bz2"
  }, 
  "bleach-1.5.0-py27_0": {
    "md5": "04fdb6f5586f7dc67ac6331327fcc60f", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/bleach-1.5.0-py27_0.tar.bz2"
  }, 
  "bokeh-0.12.5-py27_1": {
    "md5": "03b44a1f9c410059e00fcd38ab739bfd", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/bokeh-0.12.5-py27_1.tar.bz2"
  }, 
  "boto-2.46.1-py27_0": {
    "md5": "4a2788a41d3c07f399599dd04b6e1353", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/boto-2.46.1-py27_0.tar.bz2"
  }, 
  "bottleneck-1.2.1-np112py27_0": {
    "md5": "255386ad02344cf7fdefbe65879d29b4", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/bottleneck-1.2.1-np112py27_0.tar.bz2"
  }, 
  "cdecimal-2.3-py27_2": {
    "md5": "5c737d4db9dc88efe9e0018e1ff2042b", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/cdecimal-2.3-py27_2.tar.bz2"
  }, 
  "cffi-1.10.0-py27_0": {
    "md5": "0d833898b30ba31666a2e3b92fb80563", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/cffi-1.10.0-py27_0.tar.bz2"
  }, 
  "chardet-3.0.3-py27_0": {
    "md5": "4560af7a2e9ec7cad6c22b5d22dea822", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/chardet-3.0.3-py27_0.tar.bz2"
  }, 
  "click-6.7-py27_0": {
    "md5": "ce32ef70fbf9094244d7a2af660e62b2", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/click-6.7-py27_0.tar.bz2"
  }, 
  "cloudpickle-0.2.2-py27_0": {
    "md5": "460ae9c209dff3870a12a8b165d06a6e", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/cloudpickle-0.2.2-py27_0.tar.bz2"
  }, 
  "clyent-1.2.2-py27_0": {
    "md5": "26746c8b2621faaf2cd7415a9faa13f6", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/clyent-1.2.2-py27_0.tar.bz2"
  }, 
  "colorama-0.3.9-py27_0": {
    "md5": "62e592c6dc1ef009a3f8883a6390d083", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/colorama-0.3.9-py27_0.tar.bz2"
  }, 
  "conda-4.3.21-py27_0": {
    "md5": "b32ea74a8838f188cfa4bf26c0cc7bfe", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/conda-4.3.21-py27_0.tar.bz2"
  }, 
  "conda-env-2.6.0-0": {
    "md5": "4bcba5618e1c70cbfb5107c3e61f2488", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/conda-env-2.6.0-0.tar.bz2"
  }, 
  "configparser-3.5.0-py27_0": {
    "md5": "c126b6600539747da4e596d5a1c22de3", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/configparser-3.5.0-py27_0.tar.bz2"
  }, 
  "contextlib2-0.5.5-py27_0": {
    "md5": "916b7331d286c6728656bd7c655af4a4", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/contextlib2-0.5.5-py27_0.tar.bz2"
  }, 
  "cryptography-1.8.1-py27_0": {
    "md5": "7bd4458bd184fabc45f4de4bbacca7ee", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/cryptography-1.8.1-py27_0.tar.bz2"
  }, 
  "curl-7.52.1-0": {
    "md5": "d3ec98ab8d47c79644b235cb37cd46e6", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/curl-7.52.1-0.tar.bz2"
  }, 
  "cycler-0.10.0-py27_0": {
    "md5": "f25d391bc6c0db2324e521700dc218bc", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/cycler-0.10.0-py27_0.tar.bz2"
  }, 
  "cython-0.25.2-py27_0": {
    "md5": "a4c3ba9f96c4aa7867d8d6d7a8a03f63", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/cython-0.25.2-py27_0.tar.bz2"
  }, 
  "cytoolz-0.8.2-py27_0": {
    "md5": "6316104b1342a031a13b975f3e9a846a", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/cytoolz-0.8.2-py27_0.tar.bz2"
  }, 
  "dask-0.14.3-py27_1": {
    "md5": "1383bae344dfe49b7e95fc0162728484", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/dask-0.14.3-py27_1.tar.bz2"
  }, 
  "datashape-0.5.4-py27_0": {
    "md5": "d987948d3fd615c4498d780d1b0d931d", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/datashape-0.5.4-py27_0.tar.bz2"
  }, 
  "decorator-4.0.11-py27_0": {
    "md5": "7c29758e98bfe75690b68f1de9a7f63e", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/decorator-4.0.11-py27_0.tar.bz2"
  }, 
  "distributed-1.16.3-py27_0": {
    "md5": "fedaf8704a838f7971125187a7998960", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/distributed-1.16.3-py27_0.tar.bz2"
  }, 
  "docutils-0.13.1-py27_0": {
    "md5": "d2709d43f967fc8706b2436507d4132c", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/docutils-0.13.1-py27_0.tar.bz2"
  }, 
  "entrypoints-0.2.2-py27_1": {
    "md5": "e97afeba2d7202162b488fe6c0cfc522", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/entrypoints-0.2.2-py27_1.tar.bz2"
  }, 
  "enum34-1.1.6-py27_0": {
    "md5": "1a04ba0c440ed5b1c7663d475c27077b", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/enum34-1.1.6-py27_0.tar.bz2"
  }, 
  "et_xmlfile-1.0.1-py27_0": {
    "md5": "e60fa1aa645a09afc72849f45c871f96", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/et_xmlfile-1.0.1-py27_0.tar.bz2"
  }, 
  "fastcache-1.0.2-py27_1": {
    "md5": "94ec892f52e8e11bb8f8a927a22d340c", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/fastcache-1.0.2-py27_1.tar.bz2"
  }, 
  "flask-0.12.2-py27_0": {
    "md5": "8b5e5fe34947cf477b9d063c142aa2e1", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/flask-0.12.2-py27_0.tar.bz2"
  }, 
  "flask-cors-3.0.2-py27_0": {
    "md5": "e56456ccac8cb70e850a2f1c02d75b71", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/flask-cors-3.0.2-py27_0.tar.bz2"
  }, 
  "freetype-2.5.5-2": {
    "md5": "dde9e65b94586ffb83521a3ebb79583c", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/freetype-2.5.5-2.tar.bz2"
  }, 
  "funcsigs-1.0.2-py27_0": {
    "md5": "228dd45c475ee4c409fb3d2c6d6fe4f5", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/funcsigs-1.0.2-py27_0.tar.bz2"
  }, 
  "functools32-3.2.3.2-py27_0": {
    "md5": "748f0e2008f9867c1b771321a9e76ab5", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/functools32-3.2.3.2-py27_0.tar.bz2"
  }, 
  "futures-3.1.1-py27_0": {
    "md5": "ce757397e350fbd0975d12b4f2edf755", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/futures-3.1.1-py27_0.tar.bz2"
  }, 
  "get_terminal_size-1.0.0-py27_0": {
    "md5": "f8138b8c455b89b33adae805ebabab88", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/get_terminal_size-1.0.0-py27_0.tar.bz2"
  }, 
  "gevent-1.2.1-py27_0": {
    "md5": "5843015490471e92324c4ac9a64f1dab", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/gevent-1.2.1-py27_0.tar.bz2"
  }, 
  "greenlet-0.4.12-py27_0": {
    "md5": "e43501a8135985f351dde68b4c16a21e", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/greenlet-0.4.12-py27_0.tar.bz2"
  }, 
  "grin-1.2.1-py27_3": {
    "md5": "8847fe0bbf6068012ea785ee355280c1", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/grin-1.2.1-py27_3.tar.bz2"
  }, 
  "h5py-2.7.0-np112py27_0": {
    "md5": "3d511afb8ee059b35662c790da42b0f3", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/h5py-2.7.0-np112py27_0.tar.bz2"
  }, 
  "hdf5-1.8.17-1": {
    "md5": "6792a8a91a1dc1424eba2770526494b3", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/hdf5-1.8.17-1.tar.bz2"
  }, 
  "heapdict-1.0.0-py27_1": {
    "md5": "0762fd3479deede551f817d16ca4d179", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/heapdict-1.0.0-py27_1.tar.bz2"
  }, 
  "html5lib-0.999-py27_0": {
    "md5": "956db001273e3ff89ac4789118bf3851", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/html5lib-0.999-py27_0.tar.bz2"
  }, 
  "icu-54.1-0": {
    "md5": "a258fa9436d5d314b99c1776b523f3d5", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/icu-54.1-0.tar.bz2"
  }, 
  "idna-2.5-py27_0": {
    "md5": "ec0de88265a831b31a14018bd2500cb4", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/idna-2.5-py27_0.tar.bz2"
  }, 
  "imagesize-0.7.1-py27_0": {
    "md5": "39f2c6c755abe85c587b546b7e07e090", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/imagesize-0.7.1-py27_0.tar.bz2"
  }, 
  "ipaddress-1.0.18-py27_0": {
    "md5": "536ea607c5b6aff00bb7fc609a9a1b12", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/ipaddress-1.0.18-py27_0.tar.bz2"
  }, 
  "ipykernel-4.6.1-py27_0": {
    "md5": "f57fba15497af71fc058feed5a58e98a", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/ipykernel-4.6.1-py27_0.tar.bz2"
  }, 
  "ipython-5.3.0-py27_0": {
    "md5": "0ec9d0d9118e0601446679c3c1969948", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/ipython-5.3.0-py27_0.tar.bz2"
  }, 
  "ipython_genutils-0.2.0-py27_0": {
    "md5": "1ebbf525b53ad0b527d84fe0f2a3c40c", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/ipython_genutils-0.2.0-py27_0.tar.bz2"
  }, 
  "ipywidgets-6.0.0-py27_0": {
    "md5": "290e80eb9d26c91b82853477c05c0d4d", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/ipywidgets-6.0.0-py27_0.tar.bz2"
  }, 
  "isort-4.2.5-py27_0": {
    "md5": "250102095ef045037832cf36c1ea3499", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/isort-4.2.5-py27_0.tar.bz2"
  }, 
  "itsdangerous-0.24-py27_0": {
    "md5": "c2b1a6a2c6200c2af8282993bc59196c", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/itsdangerous-0.24-py27_0.tar.bz2"
  }, 
  "jbig-2.1-0": {
    "md5": "14a3be6a622b2fed0b36430b4b4b544c", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/jbig-2.1-0.tar.bz2"
  }, 
  "jdcal-1.3-py27_0": {
    "md5": "0ea7a323c77cbb52de5095f47db91080", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/jdcal-1.3-py27_0.tar.bz2"
  }, 
  "jedi-0.10.2-py27_2": {
    "md5": "6a84d0fa31d382fd1807505a0044f081", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/jedi-0.10.2-py27_2.tar.bz2"
  }, 
  "jinja2-2.9.6-py27_0": {
    "md5": "a3a57b76e8b4b1360e493c142d88569f", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/jinja2-2.9.6-py27_0.tar.bz2"
  }, 
  "jpeg-9b-0": {
    "md5": "9430f9f41041e43672a4668e7225f6f3", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/jpeg-9b-0.tar.bz2"
  }, 
  "jsonschema-2.6.0-py27_0": {
    "md5": "35f22300bd76c29b94f3ab086b88c6a8", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/jsonschema-2.6.0-py27_0.tar.bz2"
  }, 
  "jupyter-1.0.0-py27_3": {
    "md5": "3f06f79b592a77fab634d40726a66ba9", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/jupyter-1.0.0-py27_3.tar.bz2"
  }, 
  "jupyter_client-5.0.1-py27_0": {
    "md5": "43a2379b25a72c2a37c7c8e80e76f7ee", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/jupyter_client-5.0.1-py27_0.tar.bz2"
  }, 
  "jupyter_console-5.1.0-py27_0": {
    "md5": "9b731d8b1495e90d089612c34948d735", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/jupyter_console-5.1.0-py27_0.tar.bz2"
  }, 
  "jupyter_core-4.3.0-py27_0": {
    "md5": "bf59e3b8f42d57d5a36ae5c1b583c682", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/jupyter_core-4.3.0-py27_0.tar.bz2"
  }, 
  "lazy-object-proxy-1.2.2-py27_0": {
    "md5": "e1c870ce9a7be4c094f890f4da0eec08", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/lazy-object-proxy-1.2.2-py27_0.tar.bz2"
  }, 
  "libiconv-1.14-0": {
    "md5": "7eece6c601d25120570bc50acc185439", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/libiconv-1.14-0.tar.bz2"
  }, 
  "libpng-1.6.27-0": {
    "md5": "f6b16c1a8b9a704fc691baf38256e9a8", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/libpng-1.6.27-0.tar.bz2"
  }, 
  "libtiff-4.0.6-3": {
    "md5": "6de126c5b033d5cf87fc01f7a0e033a1", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/libtiff-4.0.6-3.tar.bz2"
  }, 
  "libxml2-2.9.4-0": {
    "md5": "f1747fbea83ba808267c4ae1c94aa6e5", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/libxml2-2.9.4-0.tar.bz2"
  }, 
  "libxslt-1.1.29-0": {
    "md5": "473b9143e880e223a806f5c668a12dab", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/libxslt-1.1.29-0.tar.bz2"
  }, 
  "llvmlite-0.18.0-py27_0": {
    "md5": "2a972d5ae357b5f907bf16a6494c73a2", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/llvmlite-0.18.0-py27_0.tar.bz2"
  }, 
  "locket-0.2.0-py27_1": {
    "md5": "b3bd9947069b4fc8193beb52b77206e0", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/locket-0.2.0-py27_1.tar.bz2"
  }, 
  "lxml-3.7.3-py27_0": {
    "md5": "df73282a82521560bb3796791cef3f44", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/lxml-3.7.3-py27_0.tar.bz2"
  }, 
  "markupsafe-0.23-py27_2": {
    "md5": "c98957b3b263054827407ba5d7aa1348", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/markupsafe-0.23-py27_2.tar.bz2"
  }, 
  "matplotlib-2.0.2-np112py27_0": {
    "md5": "f6c33cb04af336108c3fbcb18ada3d02", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/matplotlib-2.0.2-np112py27_0.tar.bz2"
  }, 
  "mistune-0.7.4-py27_0": {
    "md5": "af555b84535e1f95d25d0afff8e77985", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/mistune-0.7.4-py27_0.tar.bz2"
  }, 
  "mkl-2017.0.1-0": {
    "md5": "dbcfd6ad6dbde788f147db0093681206", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/mkl-2017.0.1-0.tar.bz2"
  }, 
  "mkl-service-1.1.2-py27_3": {
    "md5": "b5b6c41d085f9b51e21fac8af8711ddb", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/mkl-service-1.1.2-py27_3.tar.bz2"
  }, 
  "mpmath-0.19-py27_1": {
    "md5": "1ffe7eb2f72d657f0527c2b6044ed457", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/mpmath-0.19-py27_1.tar.bz2"
  }, 
  "msgpack-python-0.4.8-py27_0": {
    "md5": "b1199bf927b1da1dffcb69c7f854f985", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/msgpack-python-0.4.8-py27_0.tar.bz2"
  }, 
  "multipledispatch-0.4.9-py27_0": {
    "md5": "0c60cdaa95842c1b1ef06078199305a1", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/multipledispatch-0.4.9-py27_0.tar.bz2"
  }, 
  "navigator-updater-0.1.0-py27_0": {
    "md5": "ea3b9863c32bf61c2a0c23d5efd67c64", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/navigator-updater-0.1.0-py27_0.tar.bz2"
  }, 
  "nbconvert-5.1.1-py27_0": {
    "md5": "1ae3d4f43bcb67d0dcaf58a9c66c1c23", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/nbconvert-5.1.1-py27_0.tar.bz2"
  }, 
  "nbformat-4.3.0-py27_0": {
    "md5": "f7f50eddec45eee94966e51ba03370bd", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/nbformat-4.3.0-py27_0.tar.bz2"
  }, 
  "networkx-1.11-py27_0": {
    "md5": "1c39a13ec184aeac43cb9b08c2f278a4", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/networkx-1.11-py27_0.tar.bz2"
  }, 
  "nltk-3.2.3-py27_0": {
    "md5": "91954797ad5e681d9c7aca0421adc07b", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/nltk-3.2.3-py27_0.tar.bz2"
  }, 
  "nose-1.3.7-py27_1": {
    "md5": "5a95cb8f3f644f6fc3f4a05c3dba0037", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/nose-1.3.7-py27_1.tar.bz2"
  }, 
  "notebook-5.0.0-py27_0": {
    "md5": "e2da6cfd77ab9c3f641f8a99ddb051df", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/notebook-5.0.0-py27_0.tar.bz2"
  }, 
  "numba-0.33.0-np112py27_0": {
    "md5": "7fb3fab900b957f98b6dbda7ad25ba3a", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/numba-0.33.0-np112py27_0.tar.bz2"
  }, 
  "numexpr-2.6.2-np112py27_0": {
    "md5": "6192dea22f250d24254976ae025a9bd1", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/numexpr-2.6.2-np112py27_0.tar.bz2"
  }, 
  "numpy-1.12.1-py27_0": {
    "md5": "a05d79c11ff18b6dbf928cc32115e26e", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/numpy-1.12.1-py27_0.tar.bz2"
  }, 
  "numpydoc-0.6.0-py27_0": {
    "md5": "50eafbf95d32663f9839d62b01db872c", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/numpydoc-0.6.0-py27_0.tar.bz2"
  }, 
  "odo-0.5.0-py27_1": {
    "md5": "bf22fd74cdba7d237ec20f50fde9dc80", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/odo-0.5.0-py27_1.tar.bz2"
  }, 
  "olefile-0.44-py27_0": {
    "md5": "b0e1d5e1f5054dc379c2ddf4dc1bcce0", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/olefile-0.44-py27_0.tar.bz2"
  }, 
  "openpyxl-2.4.7-py27_0": {
    "md5": "b60bbaf1da6c66f4947acb5dcda51ba6", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/openpyxl-2.4.7-py27_0.tar.bz2"
  }, 
  "openssl-1.0.2l-0": {
    "md5": "f821d9e9078c7f56becd5e22646110ca", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/openssl-1.0.2l-0.tar.bz2"
  }, 
  "packaging-16.8-py27_0": {
    "md5": "3e3b88b7b833515437294fc54f96dc0e", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/packaging-16.8-py27_0.tar.bz2"
  }, 
  "pandas-0.20.1-np112py27_0": {
    "md5": "f9101c4fa88b32f98a3b1c875f93b917", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pandas-0.20.1-np112py27_0.tar.bz2"
  }, 
  "pandocfilters-1.4.1-py27_0": {
    "md5": "aafda30d6cbecb77e823ef9b3143bde5", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pandocfilters-1.4.1-py27_0.tar.bz2"
  }, 
  "partd-0.3.8-py27_0": {
    "md5": "beeab6dee0667ea6aa29b0e773657c70", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/partd-0.3.8-py27_0.tar.bz2"
  }, 
  "path.py-10.3.1-py27_0": {
    "md5": "490bfa159ec00032da2c4c175325de97", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/path.py-10.3.1-py27_0.tar.bz2"
  }, 
  "pathlib2-2.2.1-py27_0": {
    "md5": "0447b05ab8abbc2161ae5d485e1c609f", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pathlib2-2.2.1-py27_0.tar.bz2"
  }, 
  "patsy-0.4.1-py27_0": {
    "md5": "1612ecc140bea08513b5eac5f13d59d3", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/patsy-0.4.1-py27_0.tar.bz2"
  }, 
  "pep8-1.7.0-py27_0": {
    "md5": "9cbc7cd79dba4bc4d2e686829e1f94a3", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pep8-1.7.0-py27_0.tar.bz2"
  }, 
  "pexpect-4.2.1-py27_0": {
    "md5": "832a0a8f96666429b09ecbc9ab0d303f", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pexpect-4.2.1-py27_0.tar.bz2"
  }, 
  "pickleshare-0.7.4-py27_0": {
    "md5": "ca8660efc5c44d3ed82225cd4030d562", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pickleshare-0.7.4-py27_0.tar.bz2"
  }, 
  "pillow-4.1.1-py27_0": {
    "md5": "85414864d9fa0b1794c4eea7853a6414", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pillow-4.1.1-py27_0.tar.bz2"
  }, 
  "pip-9.0.1-py27_1": {
    "md5": "b8b89c6ec61a18b86aaa9a156fa2982f", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pip-9.0.1-py27_1.tar.bz2"
  }, 
  "ply-3.10-py27_0": {
    "md5": "437e92567642f08b34dc2e2f8743a947", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/ply-3.10-py27_0.tar.bz2"
  }, 
  "prompt_toolkit-1.0.14-py27_0": {
    "md5": "73a75c12cab2d39b3192aeb288301043", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/prompt_toolkit-1.0.14-py27_0.tar.bz2"
  }, 
  "psutil-5.2.2-py27_0": {
    "md5": "ed486f95729f47b0d9e9b151f501088a", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/psutil-5.2.2-py27_0.tar.bz2"
  }, 
  "ptyprocess-0.5.1-py27_0": {
    "md5": "8d9b601abb7161c9bcea3ae33e314fb7", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/ptyprocess-0.5.1-py27_0.tar.bz2"
  }, 
  "py-1.4.33-py27_0": {
    "md5": "a2f238d796b7fe7038bd315f277f362d", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/py-1.4.33-py27_0.tar.bz2"
  }, 
  "pyaudio-0.2.7-py27_0": {
    "md5": "15a2f07084391414a13b4de26e853552", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pyaudio-0.2.7-py27_0.tar.bz2"
  }, 
  "pycosat-0.6.2-py27_0": {
    "md5": "7873249b468b84ed37a344f928c45266", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pycosat-0.6.2-py27_0.tar.bz2"
  }, 
  "pycparser-2.17-py27_0": {
    "md5": "c1b279b8c856210285d993327524152b", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pycparser-2.17-py27_0.tar.bz2"
  }, 
  "pycrypto-2.6.1-py27_6": {
    "md5": "ed73e89be763df73db1a6b991ae914f6", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pycrypto-2.6.1-py27_6.tar.bz2"
  }, 
  "pycurl-7.43.0-py27_2": {
    "md5": "c1e4a68de45e38bea80bd1fe9da38a0e", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pycurl-7.43.0-py27_2.tar.bz2"
  }, 
  "pyflakes-1.5.0-py27_0": {
    "md5": "74fd32cfbd2f08d164a8f174b85979c7", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pyflakes-1.5.0-py27_0.tar.bz2"
  }, 
  "pygments-2.2.0-py27_0": {
    "md5": "bdb89862a724c35d18dceab67cbf098d", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pygments-2.2.0-py27_0.tar.bz2"
  }, 
  "pylint-1.6.4-py27_1": {
    "md5": "0f1473fd07f18289f4008b8f58167e34", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pylint-1.6.4-py27_1.tar.bz2"
  }, 
  "pyodbc-4.0.16-py27_0": {
    "md5": "9d9d36b1b40c3ce85ec930c96ae222cc", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pyodbc-4.0.16-py27_0.tar.bz2"
  }, 
  "pyopenssl-17.0.0-py27_0": {
    "md5": "8a99964fe3c3970212af1ae0095420c3", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pyopenssl-17.0.0-py27_0.tar.bz2"
  }, 
  "pyparsing-2.1.4-py27_0": {
    "md5": "2238fcf2c035254741c1135a0cb4c9c9", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pyparsing-2.1.4-py27_0.tar.bz2"
  }, 
  "pyqt-5.6.0-py27_1": {
    "md5": "1e65a11a7761b651b84407468513b64a", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pyqt-5.6.0-py27_1.tar.bz2"
  }, 
  "pytables-3.3.0-np112py27_0": {
    "md5": "6cd7ea32dddfeae57ade5c6b4e48d999", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pytables-3.3.0-np112py27_0.tar.bz2"
  }, 
  "pytest-3.0.7-py27_0": {
    "md5": "b5ecba4b2c48598d3327fb7ef052a662", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pytest-3.0.7-py27_0.tar.bz2"
  }, 
  "python-2.7.13-0": {
    "md5": "ed556ceab44dadfac87200a6c711f3d8", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/python-2.7.13-0.tar.bz2"
  }, 
  "python-dateutil-2.6.0-py27_0": {
    "md5": "ccf781e8b07232ad6b7b8859ab2eba9a", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/python-dateutil-2.6.0-py27_0.tar.bz2"
  }, 
  "python.app-1.2-py27_4": {
    "md5": "1c7d5c9ba62c7fdb7ab4559b1d430c67", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/python.app-1.2-py27_4.tar.bz2"
  }, 
  "pytz-2017.2-py27_0": {
    "md5": "cffca16592c49501396100b04eee6b7e", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pytz-2017.2-py27_0.tar.bz2"
  }, 
  "pywavelets-0.5.2-np112py27_0": {
    "md5": "9ad2011b21c52b957f9e180af80bb9a1", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pywavelets-0.5.2-np112py27_0.tar.bz2"
  }, 
  "pyyaml-3.12-py27_0": {
    "md5": "aa476ce111cf5aca8a9dc3e0522295a5", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pyyaml-3.12-py27_0.tar.bz2"
  }, 
  "pyzmq-16.0.2-py27_0": {
    "md5": "bcac815c23f12ef7699166d958ebd678", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/pyzmq-16.0.2-py27_0.tar.bz2"
  }, 
  "qt-5.6.2-2": {
    "md5": "74b0c33e0629a62e7b0f7ed528594285", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/qt-5.6.2-2.tar.bz2"
  }, 
  "qtawesome-0.4.4-py27_0": {
    "md5": "2332e65b8c9ae1047352ca80cb192818", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/qtawesome-0.4.4-py27_0.tar.bz2"
  }, 
  "qtconsole-4.3.0-py27_0": {
    "md5": "ac6ad5f255145e01890663b30c78fb8c", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/qtconsole-4.3.0-py27_0.tar.bz2"
  }, 
  "qtpy-1.2.1-py27_0": {
    "md5": "21c7c7a4337c960d14775ae50b9ddaa0", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/qtpy-1.2.1-py27_0.tar.bz2"
  }, 
  "readline-6.2-2": {
    "md5": "0801e644bd0c1cd7f0923b56c52eb7f7", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/readline-6.2-2.tar.bz2"
  }, 
  "requests-2.14.2-py27_0": {
    "md5": "93795e817e87d0c99bad6de32f782536", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/requests-2.14.2-py27_0.tar.bz2"
  }, 
  "rope-0.9.4-py27_1": {
    "md5": "63e999bbd88fc69dae23c145b4cf2276", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/rope-0.9.4-py27_1.tar.bz2"
  }, 
  "ruamel_yaml-0.11.14-py27_1": {
    "md5": "22857f700192b9ab1688ed415e819b97", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/ruamel_yaml-0.11.14-py27_1.tar.bz2"
  }, 
  "scandir-1.5-py27_0": {
    "md5": "dd4fda0c4bfc089b60253d6dbb606ba2", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/scandir-1.5-py27_0.tar.bz2"
  }, 
  "scikit-image-0.13.0-np112py27_0": {
    "md5": "2dafeb8b94ec3006bfb2a152f7e9736e", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/scikit-image-0.13.0-np112py27_0.tar.bz2"
  }, 
  "scikit-learn-0.18.1-np112py27_1": {
    "md5": "5b1866879fe36ecd0767aeb037b44249", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/scikit-learn-0.18.1-np112py27_1.tar.bz2"
  }, 
  "scipy-0.19.0-np112py27_0": {
    "md5": "efe524c448744e033f8b0fb71541f00e", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/scipy-0.19.0-np112py27_0.tar.bz2"
  }, 
  "seaborn-0.7.1-py27_0": {
    "md5": "5ff81c834c8ccd420d45b6c7f717ce2a", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/seaborn-0.7.1-py27_0.tar.bz2"
  }, 
  "setuptools-27.2.0-py27_0": {
    "md5": "0063c540d11df7ae01d19346b87509f7", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/setuptools-27.2.0-py27_0.tar.bz2"
  }, 
  "simplegeneric-0.8.1-py27_1": {
    "md5": "b3e5b9b244d74325cc2fd5034611e8cf", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/simplegeneric-0.8.1-py27_1.tar.bz2"
  }, 
  "singledispatch-3.4.0.3-py27_0": {
    "md5": "38fc3c4659312843bae5d170225652a5", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/singledispatch-3.4.0.3-py27_0.tar.bz2"
  }, 
  "sip-4.18-py27_0": {
    "md5": "b49f80e88dcbdd52a764c6fa84df29c9", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/sip-4.18-py27_0.tar.bz2"
  }, 
  "six-1.10.0-py27_0": {
    "md5": "ce75af4aa6c25c007515b4651f469394", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/six-1.10.0-py27_0.tar.bz2"
  }, 
  "snowballstemmer-1.2.1-py27_0": {
    "md5": "739e7f2756761d9c509475bcdf670e0c", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/snowballstemmer-1.2.1-py27_0.tar.bz2"
  }, 
  "sortedcollections-0.5.3-py27_0": {
    "md5": "674a824c3231ecbb9cf821eb7d626bcc", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/sortedcollections-0.5.3-py27_0.tar.bz2"
  }, 
  "sortedcontainers-1.5.7-py27_0": {
    "md5": "5b350e47ecb6031d12404487060d27e6", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/sortedcontainers-1.5.7-py27_0.tar.bz2"
  }, 
  "sphinx-1.5.6-py27_0": {
    "md5": "ba49e7a8d6d4bef49776076cd3a6c299", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/sphinx-1.5.6-py27_0.tar.bz2"
  }, 
  "spyder-3.1.4-py27_0": {
    "md5": "c125dad6e23de6e805877dd056d5eb40", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/spyder-3.1.4-py27_0.tar.bz2"
  }, 
  "sqlalchemy-1.1.9-py27_0": {
    "md5": "7dfb59c40706f846f34e5626c3df4893", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/sqlalchemy-1.1.9-py27_0.tar.bz2"
  }, 
  "sqlite-3.13.0-0": {
    "md5": "dacf9558b650e37c4ec9003fe7f6b405", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/sqlite-3.13.0-0.tar.bz2"
  }, 
  "ssl_match_hostname-3.4.0.2-py27_1": {
    "md5": "51240dbd02f2f8b059ae17ab4b5cafa1", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/ssl_match_hostname-3.4.0.2-py27_1.tar.bz2"
  }, 
  "statsmodels-0.8.0-np112py27_0": {
    "md5": "38d4f72ee283eba54f2aeda30358e1a4", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/statsmodels-0.8.0-np112py27_0.tar.bz2"
  }, 
  "subprocess32-3.2.7-py27_0": {
    "md5": "60aff2cbfe01a53e3d122cd95100176c", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/subprocess32-3.2.7-py27_0.tar.bz2"
  }, 
  "sympy-1.0-py27_0": {
    "md5": "0916165678d98a334f5a749c1cb3457e", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/sympy-1.0-py27_0.tar.bz2"
  }, 
  "tblib-1.3.2-py27_0": {
    "md5": "55bf541d5428e855ab87bac0de7adcc5", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/tblib-1.3.2-py27_0.tar.bz2"
  }, 
  "terminado-0.6-py27_0": {
    "md5": "45fbff5477bf057726d052f236103d9b", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/terminado-0.6-py27_0.tar.bz2"
  }, 
  "testpath-0.3-py27_0": {
    "md5": "7ea4c79233e7e2135160eab9d5f26f9d", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/testpath-0.3-py27_0.tar.bz2"
  }, 
  "tk-8.5.18-0": {
    "md5": "6de7b2d4c4c9cc0f60150da541c0d843", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/tk-8.5.18-0.tar.bz2"
  }, 
  "toolz-0.8.2-py27_0": {
    "md5": "46080657fcd8929992903dc69360258c", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/toolz-0.8.2-py27_0.tar.bz2"
  }, 
  "tornado-4.5.1-py27_0": {
    "md5": "095b593540c0bbda7caa4d8e3df62e50", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/tornado-4.5.1-py27_0.tar.bz2"
  }, 
  "traitlets-4.3.2-py27_0": {
    "md5": "d218fc21ae9069fb5a11d90a4181b89e", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/traitlets-4.3.2-py27_0.tar.bz2"
  }, 
  "unicodecsv-0.14.1-py27_0": {
    "md5": "78abb3198da7509ac9f44ad8c669b74c", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/unicodecsv-0.14.1-py27_0.tar.bz2"
  }, 
  "unixodbc-2.3.4-0": {
    "md5": "3e347e915a8a60db20c0b64b81c78d01", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/unixodbc-2.3.4-0.tar.bz2"
  }, 
  "wcwidth-0.1.7-py27_0": {
    "md5": "8e7030d983cc88e94c5fb32210865bb1", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/wcwidth-0.1.7-py27_0.tar.bz2"
  }, 
  "werkzeug-0.12.2-py27_0": {
    "md5": "2bd2043eba30082f526a0757be6a2b5d", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/werkzeug-0.12.2-py27_0.tar.bz2"
  }, 
  "wheel-0.29.0-py27_0": {
    "md5": "2c2d6756adc65c38f83d355adef6cfab", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/wheel-0.29.0-py27_0.tar.bz2"
  }, 
  "widgetsnbextension-2.0.0-py27_0": {
    "md5": "370ec57f6e768ead75bc8e1a1b705e6f", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/widgetsnbextension-2.0.0-py27_0.tar.bz2"
  }, 
  "wrapt-1.10.10-py27_0": {
    "md5": "7a1ec5e8e59a4a3576c7530e2c5a8d5e", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/wrapt-1.10.10-py27_0.tar.bz2"
  }, 
  "xlrd-1.0.0-py27_0": {
    "md5": "5bca4e459c5d5e8eba5a39cf15fc5042", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/xlrd-1.0.0-py27_0.tar.bz2"
  }, 
  "xlsxwriter-0.9.6-py27_0": {
    "md5": "c347773a094e036cbe1bf1be0b8bc88b", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/xlsxwriter-0.9.6-py27_0.tar.bz2"
  }, 
  "xlwings-0.10.4-py27_0": {
    "md5": "52586dd1470bf0b51e64c97147fd7318", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/xlwings-0.10.4-py27_0.tar.bz2"
  }, 
  "xlwt-1.2.0-py27_0": {
    "md5": "1386fb682f81bb2815dacd5b009b734d", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/xlwt-1.2.0-py27_0.tar.bz2"
  }, 
  "xz-5.2.2-1": {
    "md5": "c8d5d3f406b5309e575c6848091f2fd2", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/xz-5.2.2-1.tar.bz2"
  }, 
  "yaml-0.1.6-0": {
    "md5": "7b1c018bf975c88fbe9df6292bf370b1", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/yaml-0.1.6-0.tar.bz2"
  }, 
  "zict-0.1.2-py27_0": {
    "md5": "f29e88be2ac69b3ffd4879e854e21077", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/zict-0.1.2-py27_0.tar.bz2"
  }, 
  "zlib-1.2.8-3": {
    "md5": "49b15627e7048317806615d519a5b581", 
    "url": "https://repo.continuum.io/pkgs/free/osx-64/zlib-1.2.8-3.tar.bz2"
  }
}
C_ENVS = {
  "root": [
    "python-2.7.13-0", 
    "_license-1.1-py27_1", 
    "alabaster-0.7.10-py27_0", 
    "anaconda-client-1.6.3-py27_0", 
    "anaconda-navigator-1.6.2-py27_0", 
    "anaconda-project-0.6.0-py27_0", 
    "appnope-0.1.0-py27_0", 
    "appscript-1.0.1-py27_0", 
    "asn1crypto-0.22.0-py27_0", 
    "astroid-1.4.9-py27_0", 
    "astropy-1.3.2-np112py27_0", 
    "babel-2.4.0-py27_0", 
    "backports-1.0-py27_0", 
    "backports_abc-0.5-py27_0", 
    "beautifulsoup4-4.6.0-py27_0", 
    "bitarray-0.8.1-py27_0", 
    "blaze-0.10.1-py27_0", 
    "bleach-1.5.0-py27_0", 
    "bokeh-0.12.5-py27_1", 
    "boto-2.46.1-py27_0", 
    "bottleneck-1.2.1-np112py27_0", 
    "cdecimal-2.3-py27_2", 
    "cffi-1.10.0-py27_0", 
    "chardet-3.0.3-py27_0", 
    "click-6.7-py27_0", 
    "cloudpickle-0.2.2-py27_0", 
    "clyent-1.2.2-py27_0", 
    "colorama-0.3.9-py27_0", 
    "configparser-3.5.0-py27_0", 
    "contextlib2-0.5.5-py27_0", 
    "cryptography-1.8.1-py27_0", 
    "curl-7.52.1-0", 
    "cycler-0.10.0-py27_0", 
    "cython-0.25.2-py27_0", 
    "cytoolz-0.8.2-py27_0", 
    "dask-0.14.3-py27_1", 
    "datashape-0.5.4-py27_0", 
    "decorator-4.0.11-py27_0", 
    "distributed-1.16.3-py27_0", 
    "docutils-0.13.1-py27_0", 
    "entrypoints-0.2.2-py27_1", 
    "enum34-1.1.6-py27_0", 
    "et_xmlfile-1.0.1-py27_0", 
    "fastcache-1.0.2-py27_1", 
    "flask-0.12.2-py27_0", 
    "flask-cors-3.0.2-py27_0", 
    "freetype-2.5.5-2", 
    "funcsigs-1.0.2-py27_0", 
    "functools32-3.2.3.2-py27_0", 
    "futures-3.1.1-py27_0", 
    "get_terminal_size-1.0.0-py27_0", 
    "gevent-1.2.1-py27_0", 
    "greenlet-0.4.12-py27_0", 
    "grin-1.2.1-py27_3", 
    "h5py-2.7.0-np112py27_0", 
    "hdf5-1.8.17-1", 
    "heapdict-1.0.0-py27_1", 
    "html5lib-0.999-py27_0", 
    "icu-54.1-0", 
    "idna-2.5-py27_0", 
    "imagesize-0.7.1-py27_0", 
    "ipaddress-1.0.18-py27_0", 
    "ipykernel-4.6.1-py27_0", 
    "ipython-5.3.0-py27_0", 
    "ipython_genutils-0.2.0-py27_0", 
    "ipywidgets-6.0.0-py27_0", 
    "isort-4.2.5-py27_0", 
    "itsdangerous-0.24-py27_0", 
    "jbig-2.1-0", 
    "jdcal-1.3-py27_0", 
    "jedi-0.10.2-py27_2", 
    "jinja2-2.9.6-py27_0", 
    "jpeg-9b-0", 
    "jsonschema-2.6.0-py27_0", 
    "jupyter-1.0.0-py27_3", 
    "jupyter_client-5.0.1-py27_0", 
    "jupyter_console-5.1.0-py27_0", 
    "jupyter_core-4.3.0-py27_0", 
    "lazy-object-proxy-1.2.2-py27_0", 
    "libiconv-1.14-0", 
    "libpng-1.6.27-0", 
    "libtiff-4.0.6-3", 
    "libxml2-2.9.4-0", 
    "libxslt-1.1.29-0", 
    "llvmlite-0.18.0-py27_0", 
    "locket-0.2.0-py27_1", 
    "lxml-3.7.3-py27_0", 
    "markupsafe-0.23-py27_2", 
    "matplotlib-2.0.2-np112py27_0", 
    "mistune-0.7.4-py27_0", 
    "mkl-2017.0.1-0", 
    "mkl-service-1.1.2-py27_3", 
    "mpmath-0.19-py27_1", 
    "msgpack-python-0.4.8-py27_0", 
    "multipledispatch-0.4.9-py27_0", 
    "navigator-updater-0.1.0-py27_0", 
    "nbconvert-5.1.1-py27_0", 
    "nbformat-4.3.0-py27_0", 
    "networkx-1.11-py27_0", 
    "nltk-3.2.3-py27_0", 
    "nose-1.3.7-py27_1", 
    "notebook-5.0.0-py27_0", 
    "numba-0.33.0-np112py27_0", 
    "numexpr-2.6.2-np112py27_0", 
    "numpy-1.12.1-py27_0", 
    "numpydoc-0.6.0-py27_0", 
    "odo-0.5.0-py27_1", 
    "olefile-0.44-py27_0", 
    "openpyxl-2.4.7-py27_0", 
    "openssl-1.0.2l-0", 
    "packaging-16.8-py27_0", 
    "pandas-0.20.1-np112py27_0", 
    "pandocfilters-1.4.1-py27_0", 
    "partd-0.3.8-py27_0", 
    "path.py-10.3.1-py27_0", 
    "pathlib2-2.2.1-py27_0", 
    "patsy-0.4.1-py27_0", 
    "pep8-1.7.0-py27_0", 
    "pexpect-4.2.1-py27_0", 
    "pickleshare-0.7.4-py27_0", 
    "pillow-4.1.1-py27_0", 
    "pip-9.0.1-py27_1", 
    "ply-3.10-py27_0", 
    "prompt_toolkit-1.0.14-py27_0", 
    "psutil-5.2.2-py27_0", 
    "ptyprocess-0.5.1-py27_0", 
    "py-1.4.33-py27_0", 
    "pyaudio-0.2.7-py27_0", 
    "pycosat-0.6.2-py27_0", 
    "pycparser-2.17-py27_0", 
    "pycrypto-2.6.1-py27_6", 
    "pycurl-7.43.0-py27_2", 
    "pyflakes-1.5.0-py27_0", 
    "pygments-2.2.0-py27_0", 
    "pylint-1.6.4-py27_1", 
    "pyodbc-4.0.16-py27_0", 
    "pyopenssl-17.0.0-py27_0", 
    "pyparsing-2.1.4-py27_0", 
    "pyqt-5.6.0-py27_1", 
    "pytables-3.3.0-np112py27_0", 
    "pytest-3.0.7-py27_0", 
    "python-dateutil-2.6.0-py27_0", 
    "python.app-1.2-py27_4", 
    "pytz-2017.2-py27_0", 
    "pywavelets-0.5.2-np112py27_0", 
    "pyyaml-3.12-py27_0", 
    "pyzmq-16.0.2-py27_0", 
    "qt-5.6.2-2", 
    "qtawesome-0.4.4-py27_0", 
    "qtconsole-4.3.0-py27_0", 
    "qtpy-1.2.1-py27_0", 
    "readline-6.2-2", 
    "requests-2.14.2-py27_0", 
    "rope-0.9.4-py27_1", 
    "ruamel_yaml-0.11.14-py27_1", 
    "scandir-1.5-py27_0", 
    "scikit-image-0.13.0-np112py27_0", 
    "scikit-learn-0.18.1-np112py27_1", 
    "scipy-0.19.0-np112py27_0", 
    "seaborn-0.7.1-py27_0", 
    "setuptools-27.2.0-py27_0", 
    "simplegeneric-0.8.1-py27_1", 
    "singledispatch-3.4.0.3-py27_0", 
    "sip-4.18-py27_0", 
    "six-1.10.0-py27_0", 
    "snowballstemmer-1.2.1-py27_0", 
    "sortedcollections-0.5.3-py27_0", 
    "sortedcontainers-1.5.7-py27_0", 
    "sphinx-1.5.6-py27_0", 
    "spyder-3.1.4-py27_0", 
    "sqlalchemy-1.1.9-py27_0", 
    "sqlite-3.13.0-0", 
    "ssl_match_hostname-3.4.0.2-py27_1", 
    "statsmodels-0.8.0-np112py27_0", 
    "subprocess32-3.2.7-py27_0", 
    "sympy-1.0-py27_0", 
    "tblib-1.3.2-py27_0", 
    "terminado-0.6-py27_0", 
    "testpath-0.3-py27_0", 
    "tk-8.5.18-0", 
    "toolz-0.8.2-py27_0", 
    "tornado-4.5.1-py27_0", 
    "traitlets-4.3.2-py27_0", 
    "unicodecsv-0.14.1-py27_0", 
    "unixodbc-2.3.4-0", 
    "wcwidth-0.1.7-py27_0", 
    "werkzeug-0.12.2-py27_0", 
    "wheel-0.29.0-py27_0", 
    "widgetsnbextension-2.0.0-py27_0", 
    "wrapt-1.10.10-py27_0", 
    "xlrd-1.0.0-py27_0", 
    "xlsxwriter-0.9.6-py27_0", 
    "xlwings-0.10.4-py27_0", 
    "xlwt-1.2.0-py27_0", 
    "xz-5.2.2-1", 
    "yaml-0.1.6-0", 
    "zict-0.1.2-py27_0", 
    "zlib-1.2.8-3", 
    "anaconda-4.4.0-np112py27_0", 
    "conda-4.3.21-py27_0", 
    "conda-env-2.6.0-0"
  ]
}



def _link(src, dst, linktype=LINK_HARD):
    if on_win:
        raise NotImplementedError

    if linktype == LINK_HARD:
        os.link(src, dst)
    elif linktype == LINK_COPY:
        # copy relative symlinks as symlinks
        if islink(src) and not os.readlink(src).startswith('/'):
            os.symlink(os.readlink(src), dst)
        else:
            shutil.copy2(src, dst)
    else:
        raise Exception("Did not expect linktype=%r" % linktype)


def rm_rf(path):
    """
    try to delete path, but never fail
    """
    try:
        if islink(path) or isfile(path):
            # Note that we have to check if the destination is a link because
            # exists('/path/to/dead-link') will return False, although
            # islink('/path/to/dead-link') is True.
            os.unlink(path)
        elif isdir(path):
            shutil.rmtree(path)
    except (OSError, IOError):
        pass


def yield_lines(path):
    for line in open(path):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        yield line


prefix_placeholder = ('/opt/anaconda1anaconda2'
                      # this is intentionally split into parts,
                      # such that running this program on itself
                      # will leave it unchanged
                      'anaconda3')

def read_has_prefix(path):
    """
    reads `has_prefix` file and return dict mapping filenames to
    tuples(placeholder, mode)
    """
    import shlex

    res = {}
    try:
        for line in yield_lines(path):
            try:
                placeholder, mode, f = [x.strip('"\'') for x in
                                        shlex.split(line, posix=False)]
                res[f] = (placeholder, mode)
            except ValueError:
                res[line] = (prefix_placeholder, 'text')
    except IOError:
        pass
    return res


def exp_backoff_fn(fn, *args):
    """
    for retrying file operations that fail on Windows due to virus scanners
    """
    if not on_win:
        return fn(*args)

    import time
    import errno
    max_tries = 6  # max total time = 6.4 sec
    for n in range(max_tries):
        try:
            result = fn(*args)
        except (OSError, IOError) as e:
            if e.errno in (errno.EPERM, errno.EACCES):
                if n == max_tries - 1:
                    raise Exception("max_tries=%d reached" % max_tries)
                time.sleep(0.1 * (2 ** n))
            else:
                raise e
        else:
            return result


class PaddingError(Exception):
    pass


def binary_replace(data, a, b):
    """
    Perform a binary replacement of `data`, where the placeholder `a` is
    replaced with `b` and the remaining string is padded with null characters.
    All input arguments are expected to be bytes objects.
    """
    def replace(match):
        occurances = match.group().count(a)
        padding = (len(a) - len(b)) * occurances
        if padding < 0:
            raise PaddingError(a, b, padding)
        return match.group().replace(a, b) + b'\0' * padding

    pat = re.compile(re.escape(a) + b'([^\0]*?)\0')
    res = pat.sub(replace, data)
    assert len(res) == len(data)
    return res


def update_prefix(path, new_prefix, placeholder, mode):
    if on_win:
        # force all prefix replacements to forward slashes to simplify need
        # to escape backslashes - replace with unix-style path separators
        new_prefix = new_prefix.replace('\\', '/')

    path = os.path.realpath(path)
    with open(path, 'rb') as fi:
        data = fi.read()
    if mode == 'text':
        new_data = data.replace(placeholder.encode('utf-8'),
                                new_prefix.encode('utf-8'))
    elif mode == 'binary':
        if on_win:
            # anaconda-verify will not allow binary placeholder on Windows.
            # However, since some packages might be created wrong (and a
            # binary placeholder would break the package, we just skip here.
            return
        new_data = binary_replace(data, placeholder.encode('utf-8'),
                                  new_prefix.encode('utf-8'))
    else:
        sys.exit("Invalid mode:" % mode)

    if new_data == data:
        return
    st = os.lstat(path)
    # unlink in case the file is memory mapped
    exp_backoff_fn(os.unlink, path)
    with open(path, 'wb') as fo:
        fo.write(new_data)
    os.chmod(path, stat.S_IMODE(st.st_mode))


def name_dist(dist):
    return dist.rsplit('-', 2)[0]


def create_meta(prefix, dist, info_dir, extra_info):
    """
    Create the conda metadata, in a given prefix, for a given package.
    """
    # read info/index.json first
    with open(join(info_dir, 'index.json')) as fi:
        meta = json.load(fi)
    # add extra info
    meta.update(extra_info)
    # write into <prefix>/conda-meta/<dist>.json
    meta_dir = join(prefix, 'conda-meta')
    if not isdir(meta_dir):
        os.makedirs(meta_dir)
        with open(join(meta_dir, 'history'), 'w') as fo:
            fo.write('')
    with open(join(meta_dir, dist + '.json'), 'w') as fo:
        json.dump(meta, fo, indent=2, sort_keys=True)


def run_script(prefix, dist, action='post-link'):
    """
    call the post-link (or pre-unlink) script, and return True on success,
    False on failure
    """
    path = join(prefix, 'Scripts' if on_win else 'bin', '.%s-%s.%s' % (
            name_dist(dist),
            action,
            'bat' if on_win else 'sh'))
    if not isfile(path):
        return True
    if SKIP_SCRIPTS:
        print("WARNING: skipping %s script by user request" % action)
        return True

    if on_win:
        try:
            args = [os.environ['COMSPEC'], '/c', path]
        except KeyError:
            return False
    else:
        shell_path = '/bin/sh' if 'bsd' in sys.platform else '/bin/bash'
        args = [shell_path, path]

    env = os.environ
    env['PREFIX'] = prefix

    import subprocess
    try:
        subprocess.check_call(args, env=env)
    except subprocess.CalledProcessError:
        return False
    return True


url_pat = re.compile(r'''
(?P<baseurl>\S+/)                 # base URL
(?P<fn>[^\s#/]+)                  # filename
([#](?P<md5>[0-9a-f]{32}))?       # optional MD5
$                                 # EOL
''', re.VERBOSE)

def read_urls(dist):
    try:
        data = open(join(PKGS_DIR, 'urls')).read()
        for line in data.split()[::-1]:
            m = url_pat.match(line)
            if m is None:
                continue
            if m.group('fn') == '%s.tar.bz2' % dist:
                return {'url': m.group('baseurl') + m.group('fn'),
                        'md5': m.group('md5')}
    except IOError:
        pass
    return {}


def read_no_link(info_dir):
    res = set()
    for fn in 'no_link', 'no_softlink':
        try:
            res.update(set(yield_lines(join(info_dir, fn))))
        except IOError:
            pass
    return res


def linked(prefix):
    """
    Return the (set of canonical names) of linked packages in prefix.
    """
    meta_dir = join(prefix, 'conda-meta')
    if not isdir(meta_dir):
        return set()
    return set(fn[:-5] for fn in os.listdir(meta_dir) if fn.endswith('.json'))


def link(prefix, dist, linktype=LINK_HARD):
    '''
    Link a package in a specified prefix.  We assume that the packacge has
    been extra_info in either
      - <PKGS_DIR>/dist
      - <ROOT_PREFIX>/ (when the linktype is None)
    '''
    if linktype:
        source_dir = join(PKGS_DIR, dist)
        info_dir = join(source_dir, 'info')
        no_link = read_no_link(info_dir)
    else:
        info_dir = join(prefix, 'info')

    files = list(yield_lines(join(info_dir, 'files')))
    has_prefix_files = read_has_prefix(join(info_dir, 'has_prefix'))

    if linktype:
        for f in files:
            src = join(source_dir, f)
            dst = join(prefix, f)
            dst_dir = dirname(dst)
            if not isdir(dst_dir):
                os.makedirs(dst_dir)
            if exists(dst):
                if FORCE:
                    rm_rf(dst)
                else:
                    raise Exception("dst exists: %r" % dst)
            lt = linktype
            if f in has_prefix_files or f in no_link or islink(src):
                lt = LINK_COPY
            try:
                _link(src, dst, lt)
            except OSError:
                pass

    for f in sorted(has_prefix_files):
        placeholder, mode = has_prefix_files[f]
        try:
            update_prefix(join(prefix, f), prefix, placeholder, mode)
        except PaddingError:
            sys.exit("ERROR: placeholder '%s' too short in: %s\n" %
                     (placeholder, dist))

    if not run_script(prefix, dist, 'post-link'):
        sys.exit("Error: post-link failed for: %s" % dist)

    meta = {
        'files': files,
        'link': ({'source': source_dir,
                  'type': link_name_map.get(linktype)}
                 if linktype else None),
    }
    try:    # add URL and MD5
        meta.update(IDISTS[dist])
    except KeyError:
        meta.update(read_urls(dist))
    meta['installed_by'] = 'Anaconda2-4.4.0-MacOSX-x86_64'
    create_meta(prefix, dist, info_dir, meta)


def duplicates_to_remove(linked_dists, keep_dists):
    """
    Returns the (sorted) list of distributions to be removed, such that
    only one distribution (for each name) remains.  `keep_dists` is an
    interable of distributions (which are not allowed to be removed).
    """
    from collections import defaultdict

    keep_dists = set(keep_dists)
    ldists = defaultdict(set) # map names to set of distributions
    for dist in linked_dists:
        name = name_dist(dist)
        ldists[name].add(dist)

    res = set()
    for dists in ldists.values():
        # `dists` is the group of packages with the same name
        if len(dists) == 1:
            # if there is only one package, nothing has to be removed
            continue
        if dists & keep_dists:
            # if the group has packages which are have to be kept, we just
            # take the set of packages which are in group but not in the
            # ones which have to be kept
            res.update(dists - keep_dists)
        else:
            # otherwise, we take lowest (n-1) (sorted) packages
            res.update(sorted(dists)[:-1])
    return sorted(res)


def remove_duplicates():
    idists = []
    for line in open(join(PKGS_DIR, 'urls')):
        m = url_pat.match(line)
        if m:
            fn = m.group('fn')
            idists.append(fn[:-8])

    keep_files = set()
    for dist in idists:
        with open(join(ROOT_PREFIX, 'conda-meta', dist + '.json')) as fi:
            meta = json.load(fi)
        keep_files.update(meta['files'])

    for dist in duplicates_to_remove(linked(ROOT_PREFIX), idists):
        print("unlinking: %s" % dist)
        meta_path = join(ROOT_PREFIX, 'conda-meta', dist + '.json')
        with open(meta_path) as fi:
            meta = json.load(fi)
        for f in meta['files']:
            if f not in keep_files:
                rm_rf(join(ROOT_PREFIX, f))
        rm_rf(meta_path)


def link_idists():
    src = join(PKGS_DIR, 'urls')
    dst = join(ROOT_PREFIX, '.hard-link')
    assert isfile(src), src
    assert not isfile(dst), dst
    try:
        _link(src, dst, LINK_HARD)
        linktype = LINK_HARD
    except OSError:
        linktype = LINK_COPY
    finally:
        rm_rf(dst)

    for env_name in sorted(C_ENVS):
        dists = C_ENVS[env_name]
        assert isinstance(dists, list)
        if len(dists) == 0:
            continue

        prefix = prefix_env(env_name)
        for dist in dists:
            assert dist in IDISTS
            link(prefix, dist, linktype)

        for dist in duplicates_to_remove(linked(prefix), dists):
            meta_path = join(prefix, 'conda-meta', dist + '.json')
            print("WARNING: unlinking: %s" % meta_path)
            try:
                os.rename(meta_path, meta_path + '.bak')
            except OSError:
                rm_rf(meta_path)


def prefix_env(env_name):
    if env_name == 'root':
        return ROOT_PREFIX
    else:
        return join(ROOT_PREFIX, 'envs', env_name)


def post_extract(env_name='root'):
    """
    assuming that the package is extracted in the environment `env_name`,
    this function does everything link() does except the actual linking,
    i.e. update prefix files, run 'post-link', creates the conda metadata,
    and removed the info/ directory afterwards.
    """
    prefix = prefix_env(env_name)
    info_dir = join(prefix, 'info')
    with open(join(info_dir, 'index.json')) as fi:
        meta = json.load(fi)
    dist = '%(name)s-%(version)s-%(build)s' % meta
    if FORCE:
        run_script(prefix, dist, 'pre-unlink')
    link(prefix, dist, linktype=None)
    shutil.rmtree(info_dir)


def main():
    global ROOT_PREFIX, PKGS_DIR

    p = OptionParser(description="conda link tool used by installers")

    p.add_option('--root-prefix',
                 action="store",
                 default=abspath(join(__file__, '..', '..')),
                 help="root prefix (defaults to %default)")

    p.add_option('--post',
                 action="store",
                 help="perform post extract (on a single package), "
                      "in environment NAME",
                 metavar='NAME')

    opts, args = p.parse_args()
    if args:
        p.error('no arguments expected')

    ROOT_PREFIX = opts.root_prefix.replace('//', '/')
    PKGS_DIR = join(ROOT_PREFIX, 'pkgs')

    if opts.post:
        post_extract(opts.post)
        return

    if FORCE:
        print("using -f (force) option")

    link_idists()


def main2():
    global SKIP_SCRIPTS

    p = OptionParser(description="conda post extract tool used by installers")

    p.add_option('--skip-scripts',
                 action="store_true",
                 help="skip running pre/post-link scripts")

    p.add_option('--rm-dup',
                 action="store_true",
                 help="remove duplicates")

    opts, args = p.parse_args()
    if args:
        p.error('no arguments expected')

    if opts.skip_scripts:
        SKIP_SCRIPTS = True

    if opts.rm_dup:
        remove_duplicates()
        return

    post_extract()


def warn_on_special_chrs():
    if on_win:
        return
    for c in SPECIAL_ASCII:
        if c in ROOT_PREFIX:
            print("WARNING: found '%s' in install prefix." % c)


if __name__ == '__main__':
    if IDISTS:
        main()
        warn_on_special_chrs()
    else: # common usecase
        main2()
