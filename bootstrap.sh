#!/bin/bash

virtualenv --python=python2.7 .
bin/pip install zc.buildout==2.12.0
bin/buildout
