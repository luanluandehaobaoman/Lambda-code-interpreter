#!/bin/bash

export PATH=$PATH:$LAMBDA_TASK_ROOT/bin:/opt/python/bin
export PYTHONPATH=$PYTHONPATH:/opt/python:$LAMBDA_RUNTIME_DIR:$LAMBDA_TASK_ROOT
exec python -m uvicorn --port=$PORT server:app --host=0.0.0.0