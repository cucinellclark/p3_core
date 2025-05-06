# BV-BRC Core Library Routines

## About this module

There are a handful of programming APIs that are used across a wide range of BV-BRC applications as well as SEEDtk applications. This module contains this small set of key library files implementing these APIs:

- GenomeTypeObject.pm: Methods to manipulate the JSON-formatted genome objects used in the BV-BRC annotation system
- P3DataAPI.pm: Methods that build on the basic [REST BV-BRC data api](https://www.bv-brc.org/api/doc) that provides access to the BV-BRC database
- P3UserAPI: Methods that provide basic access to the [BV-BRC user service](https://github.com/PATRIC3/p3_user)
- P3Utils.pm: Common utilities
- bvbrc_api.py: Python methods for interacting with the BV-BRC data api

This module is a component of the BV-BRC build system. It is designed to fit into the
`dev_container` infrastructure which manages development and production deployment of
the components of the BV-BRC. More documentation is available [here](https://github.com/BV-BRC/dev_container/tree/master/README.md).
