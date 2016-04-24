Rage4 CLI
=========

[![MIT Licensed](https://img.shields.io/badge/license-MIT-green.svg)](https://tldrlegal.com/license/mit-license)
[![Circle CI](https://circleci.com/gh/jaredledvina/rage4/tree/master.svg?style=svg)](https://circleci.com/gh/jaredledvina/rage4/tree/master)

## Usage

```
pip install -r requirements.txt
```


```
# python3 rage4.py -h
usage: rage4.py [-h] [-v] {create,show,delete} ...

Play with the Rage4 API

positional arguments:
  {create,show,delete}
    create              Create an new record
    show                Show record by type
    delete              Delete record by name

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Enable debug messages
```

A simple cli to use against the Rage4 API

API Docs: 
https://gbshouse.uservoice.com/knowledgebase/articles/109834-rage4-dns-developers-api


## License
See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).
