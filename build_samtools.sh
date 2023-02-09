# ------------------------------------------------------------------------------
# Copyright 2022 by the U. S. Government as represented by the Administrator of 
# the National Aeronautics and Space Administration.  All Other Rights Reserved.
 
# The 889 Compliance SAM Tool is licensed under the Apache License, Version 2.0 
# (the "License"); you may not use this file except in compliance with the 
# License. You may obtain a copy of the License at 
# http://www.apache.org/licenses/LICENSE-2.0.
 
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT 
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the 
# License for the specific language governing permissions and limitations under 
# the License.
# ------------------------------------------------------------------------------
set -v
set -e

INSTALL_DIR=$(pwd)

# Build virtual environment for python
virtualenv -p python3 venv
source venv/bin/activate
venv/bin/pip install -r requirements.txt

# Build javascript/css libraries
npm install
cd node_modules/fomantic-ui/
npx gulp install
cd ${INSTALL_DIR}
cp site.variables semantic/src/site/globals/
cd ${INSTALL_DIR}/semantic
npx gulp build
cd ${INSTALL_DIR}
rsync -av semantic/dist/* samtools/static/semantic/

# Output to file the last time site was updated
git log -1 | grep Date > last_updated.txt 

# show if there any any updates to the libraires
pip list --outdated
npm outdated
