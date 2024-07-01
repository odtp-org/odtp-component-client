# odtp-component-client

Client for ODTP Components. This repository is aimed to be used as a submodule in the different components repositories. 

## Update of Components

There is a script to facilitate the update of components when the `odtp-component-client` is changed: 

- Enter in the list `component.csv` the component name and the tag. See current examples there
- Run the tool `scripts/component-update.sh`: you need to set some parameters in the script before you run it.

The parameters are: 

```
GIT_PATH=/<full path to a repo where you have your components on your local computer>
GIT_ORG=<git organisation: for example odtp-org>
BRANCH=<current branch on the client that you are working on>
```

When you have an entry such as `odtp-component-example,v0.1.3-alpha-22` in your csv file, the script 
will do the following:

Update the `odtp-component-client` in your git repo `odtp-org/odtp-component-example` and tag the commit 
in the component repo with `v0.1.3-alpha-22` so that you can use the tag to run the component in `odtp`.

## Changelog

- v0.1.2
    - Make logging to file the default
    - Log to mongodb only when the parameter ODTP_LOGS_IN_DB=TRUE

- v0.1.1
    - Logging with logging library in `src` that also provides tracebacks
    - Add parameters for logging to file and logging to mongod

- v0.1.0
    - Logging in `logs` collection as individual document. 
    - Updating `output` document
    - Updating `result` document

- v0.0.1
    - First version
    - Inluding conditional to make snapshot optionals
    - Adding quiet flag to compressing odtp-output

# Acknowledgments, Copyright, and Licensing
## Acknowledgments and Funding
This work is part of the broader project **O**pen **D**igital **T**win **P**latform of the **S**wiss **M**obility **S**ystem (ODTP-SMS) funded by Swissuniversities CHORD grant Track B - Establish Projects. ODTP-SMS project is a joint endeavour by the Center for Sustainable Future Mobility - CSFM (ETH Zürich) and the Swiss Data Science Center - SDSC (EPFL and ETH Zürich). 
The Swiss Data Science Center (SDSC) develops domain-agnostic standards and containerized components to manage digital twins. This includes the creation of the Core Platform (both back-end and front-end), Service Component Integration Templates, Component Ontology, and the Component Zoo template. 
The Center for Sustainable Future Mobility (CSFM) develops mobility services and utilizes the components produced by SDSC to deploy a mobility digital twin platform. CSFM focuses on integrating mobility services and collecting available components in the mobility zoo, thereby applying the digital twin concept in the realm of mobility.
 
## Copyright
Copyright © 2023-2024 Swiss Data Science Center (SDSC), www.datascience.ch. All rights reserved.
The SDSC is jointly established and legally represented by the École Polytechnique Fédérale de Lausanne (EPFL) and the Eidgenössische Technische Hochschule Zürich (ETH Zürich). This copyright encompasses all materials, software, documentation, and other content created and developed by the SDSC.

## Intellectual Property (IP) Rights
The Open Digital Twin Platform (ODTP) is the result of a collaborative effort between ETH Zurich (ETHZ) and the École Polytechnique Fédérale de Lausanne (EPFL). Both institutions hold equal intellectual property rights for the ODTP project, reflecting the equitable and shared contributions of EPFL and ETH Zürich in the development and advancement of this initiative.  
 
## Licensing
The Service Component Integration Templates within this repository are licensed under the BSD 3-Clause "New" or "Revised" License. This license allows for broad compatibility and standardization, encouraging open use and contribution. For the full license text, please see the LICENSE file accompanying these templates.

### Distinct Licensing for Other Components
- **Core Platform**: Open-source under AGPLv3.
- **Ontology**: Creative Commons Attribution-ShareAlike (CC BY-SA).
- **Component Zoo Template**: BSD-3 license.

### Alternative Commercial Licensing
Alternative commercial licensing options for the core platform and other components are available and can be negotiated through the EPFL Technology Transfer Office (https://tto.epfl.ch) or ETH Zürich Technology Transfer Office (https://ethz.ch/en/industry/transfer.html).

## Ethical Use and Legal Compliance Disclaimer
Please note that this software should not be used to deliberately harm any individual or entity. Users and developers must adhere to ethical guidelines and use the software responsibly and legally. This disclaimer serves to remind all parties involved in the use or development of this software to engage in practices that are ethical, lawful, and in accordance with the intended purpose of the software.