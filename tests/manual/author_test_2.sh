#!/bin/bash

python ../../main.py \
  --evidence ../json/evidence/author_verification_empty_status.json \
  --invoke '{"test":"../json/test_of_detail/verify_author_complete.py","evaluations":[{"subject":{"name":"status","data_type":"text"},"criteria":{"equals":"complete"}}]}'
