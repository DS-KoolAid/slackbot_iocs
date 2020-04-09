#!/bin/bash

source env/bin/activate

gunicorn -b 0.0.0.0:5000 cs
