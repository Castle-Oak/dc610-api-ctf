#!/usr/bin/env bash
docker build -t dc610-api-ctf:latest .
docker run -d --read-only --restart=always -p 80:80 dc610-api-ctf
