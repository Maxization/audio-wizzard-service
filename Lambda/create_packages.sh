#!/bin/bash

rm -rf packages
mkdir packages

for l in * 
do
    ! [[ -d $l ]] && continue
    [[ $l == packages ]] && continue
    zip packages/$l.zip $l/lambda_function.py
done

aws s3 cp packages s3://${LAMBDAS_BUCKET}/ --recursive --include "*.zip" --exclude "packages"