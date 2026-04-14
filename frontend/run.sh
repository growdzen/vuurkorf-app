#!/bin/bash
set -e
cd /home/sprite/vuurkorf/frontend
npm install --legacy-peer-deps
exec npm run dev -- --port 3000
