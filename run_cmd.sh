#!/bin/bash

ssh localhost -p222
cd ~/suyumbike/suyumbike
source venv/bin/activate
python3 manage.py $@