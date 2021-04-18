PY_FILE="$0.py"
CMD="python3 -u $PY_FILE $@"
echo "calling: $CMD"
exec $CMD
