#!/usr/bin/env bash

# GIT_PATH should be an empty directory
GIT_PATH=/Users/smaennel/odtp/git
GIT_ORG=odtp-org
BRANCH=chore/main

# Function to update COMPONENT for TAG
update_client() {
    local COMPONENT_NAME=$1
    local TAG=$2
    echo "processing ${COMPONENT} ${TAG}"

    REPO_URL=git@github.com:${GIT_ORG}/${COMPONENT_NAME}.git
    CLIENT_DIR=odtp-component-client

    cd "${GIT_PATH}" || exit
    echo "${GIT_PATH}/${COMPONENT_NAME}"
    if test -d "${GIT_PATH}/${COMPONENT_NAME}"; then
        echo "repo has already been cloned"
    else
        git clone ${REPO_URL} --recurse-submodules    
    fi

    cd ${COMPONENT_NAME} || exit

    echo "Checking out ${BRANCH} and updating ${CLIENT_DIR}"
    cd "${CLIENT_DIR}" || exit
    git pull origin ${BRANCH}

    echo "get commit"
    COMMIT=$(git rev-parse HEAD)
    COMMITHASH=${COMMIT[0]}
    COMMIT7="${COMMITHASH:0:8}"
    echo "${COMMIT7}"
    cd ..
    COMPONENT_BRANCH="update-client-commit-${COMMIT7}"
    echo "${COMPONENT_BRANCH}"
    git ls-remote --exit-code --heads origin "${COMPONENT_BRANCH}"
    exit_code="$?"
    if [ "$exit_code" -eq 0 ]; then
        echo "Branch ${COMPONENT_BRANCH} does already exists." 
        exit  
    fi

    git checkout -b "${COMPONENT_BRANCH}"
    git pull origin "${COMPONENT_BRANCH}"

    echo "Making commit to update client to ${COMMIT7}"
    git add ${CLIENT_DIR}
    MESSAGE="update client to ${COMMIT7}"
    git commit -m "update client to ${MESSAGE}"

    echo "Getting git status"
    echo "git status"
    git status
    git push origin "${COMPONENT_BRANCH}"

    echo "Add tag"
    git tag -a ${TAG} -m "${MESSAGE}"
    git push origin ${TAG}

    echo "Component was successfully updated: use tag ${TAG}"    
}

# Path to your CSV file
csv_file="components.csv"

# Read the CSV file line by line
{
    # Skip the header line
    read header
    while IFS=, read -r COMPONENT TAG; do
        echo "=====> Read line: COMPONENT=$COMPONENT, TAG=$TAG"  # Debugging output
        if [ -n "$COMPONENT" ]; then
            # Call the function with COMPONENT and TAG
            update_client "$COMPONENT" "$TAG"        
        fi
    done   
} < "$csv_file"