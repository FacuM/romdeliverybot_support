#!/usr/bin/env bash
REMOTE_HOST='https://github.com'
REMOTE_PATH='FacuM'
REMOTE_REPO='python-duckduckgo'
if [ ! -d "$HOME"'/'"$REMOTE_REPO" ]
then
  git clone "$REMOTE_HOST"'/'"$REMOTE_PATH"'/'"$REMOTE_REPO" "$HOME"'/'"$REMOTE_REPO"
  PRE_PWD="$PWD"
  cd "$HOME"'/'"$REMOTE_REPO"
  python3 setup.py install --user
  cd "$PRE_PWD"
fi
python3 -m pip install -r requirements.txt --user
python3 main.py
