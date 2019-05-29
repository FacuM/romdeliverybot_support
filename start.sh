#!/usr/bin/env bash
REMOTE_HOST='https://github.com'
REMOTE_PATH='FacuM'
REMOTE_REPO='python-duckduckgo'
if [ ! -d "$HOME"'/'"$REMOTE_REPO" ]
then
  git clone "$REMOTE_HOST"'/'"$REMOTE_PATH"'/'"$REMOTE_REPO" "$HOME"'/'"$REMOTE_REPO"
  PRE_PWD="$PWD"
  cd "$HOME"'/'"$REMOTE_REPO"
  python setup.py install --user
  cd "$PRE_PWD"
fi
python -m pip install -r requirements.txt --user
python main.py
