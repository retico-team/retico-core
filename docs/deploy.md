# retico-deploy

Deploys are done with PyPi, in order to deploy a script first update the version in the associated setup.py file. So if it is currently on version 1.1 update the version to 1.2 and then follow the deploy steps.


  ```

cd <project directory>

rm -rf dist

python -m build --sdist

twine upload dist/*

```

There is an option for a mass deploy of all the retico modules, however it requires all the setup.py files to be updated to a new version. If you want to use this script for some files, simply comment out the unneeded deploy commands in the `retico_deploy.sh` script. Just make sure to remove these comments after you are done with the mass deploy. To run the mass deploy execute the following command from the root retico-core directory.

`./retico_deploy.sh`