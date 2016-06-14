#!/bin/bash

export LIBRARY_PATH=./ltp/lib:$LIBRARY_PATH
export LD_LIBRARY_PATH=./ltp/lib:$LD_LIBRARY_PATH

chmod +x ./tag
./tag ./ltp/model/pos.model ./ltp/model/parser.model
