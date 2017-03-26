PY_FILE="$0.py"
CMD="python -u $PY_FILE $@"
echo "calling: $CMD"
exec $CMD
