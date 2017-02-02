#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

# If Boron zip exists in /opt, it extracts it in the
# current directory (the "fast" path).
# If it doesn't exist, it downloads it in /opt and them extracts it.

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd $SCRIPT_DIR

ODL_ZIP_FILE="distribution-karaf-0.5.3-20170126.002119-364.zip"
ODL_NEXUS_LOCATION="https://nexus.opendaylight.org/content/repositories/opendaylight.snapshot/org/opendaylight/integration/distribution-karaf/0.5.3-SNAPSHOT/"

wget -nc "$ODL_NEXUS_LOCATION$ODL_ZIP_FILE" -P /opt/
if [ $? -ne 0 ]; then
    exit 1
fi

unzip -o /opt/$ODL_ZIP_FILE -d ./
if [ $? -ne 0 ]; then
    exit 1
fi

