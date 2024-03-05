#!/bin/bash

# Deploy Core
#cd "retico_core/core"
echo "Deploying core"
#cd ".."
rm -rf "dist"
python -m build --sdist
twine upload "dist/*"

# Deploy huggingface
cd "retico_core/huggingface"
echo "Deploying huggingface"
echo "Now in $(pwd)"
rm -rf "dist"
python -m build --sdist
twine upload "dist/*"
cd ".."

# Deploy psi
cd "psi"
echo "Deploying psi"
echo "Now in $(pwd)"
rm -rf "dist"
python -m build --sdist
twine upload "dist/*"
cd ".."

# Deploy rasa
cd "rasa"
echo "Deploying rasa"
echo "Now in $(pwd)"
rm -rf "dist"
python -m build --sdist
twine upload "dist/*"
cd ".."

# Deploy sds_class
cd "sds_class"
echo "Deploying sds_class"
rm -rf "dist"
python -m build --sdist
twine upload "dist/*"
cd ".."

# Deploy slim
cd "slim"
echo "Now in $(pwd)"
echo "Deploying slim"
echo "All modules deployed"
rm -rf "dist"
python -m build --sdist
twine upload "dist/*"