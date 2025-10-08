 #!/bin/env bash
./setup.sh
source venv/bin/activate
python3 proto_aff.py
deactivate
