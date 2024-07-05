#!/usr/bin/env bash

set -x

bash scripts/init_indexes_es/curl_genres_index.bash
bash scripts/init_indexes_es/curl_movies_index.bash
bash scripts/init_indexes_es/curl_persons_index.bash
