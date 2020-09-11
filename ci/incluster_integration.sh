#!/bin/bash

set -x

# IMAGE_FORMAT is in the form $registry/$org/$image:$$component, ie
# quay.io/openshift/release:$component
# To test with your own image, build and push the test image
# (using the Dockerfile in ci/Dockerfile)
# and set the IMAGE_FORMAT environment variable so that it properly
# resolves to your image. For example, quay.io/mynamespace/$component
# would resolve to quay.io/mynamespace/molecule-test-runner
component='molecule-test-runner'
eval IMAGE=$IMAGE_FORMAT

PULL_POLICY=${PULL_POLICY:-IfNotPresent}

echo "Deleting test job if it exists"
oc delete job molecule-integration-test --wait --ignore-not-found

echo "Creating molecule test job"
cat << EOF | oc create -f -
---
apiVersion: batch/v1
kind: Job
metadata:
  name: molecule-integration-test
spec:
  template:
    spec:
      containers:
        - name: test-runner
          image: ${IMAGE}
          imagePullPolicy: ${PULL_POLICY}
          command:
            - make
            - test-integration
      restartPolicy: Never
  backoffLimit: 2
  completions: 1
  parallelism: 1
EOF

function wait_for_success {
  oc wait --for=condition=complete job/molecule-integration-test --timeout 5m
  oc logs job/molecule-integration-test
  echo "Molecule integration tests ran successfully"
  exit 0
}

function wait_for_failure {
  oc wait --for=condition=failed job/molecule-integration-test --timeout 5m
  oc logs job/molecule-integration-test
  echo "Molecule integration tests failed, see logs for more information..."
  exit 1
}

# Ensure the child processes are killed
trap 'kill -SIGTERM 0' SIGINT EXIT

echo "Waiting for test job to complete"
wait_for_success &
wait_for_failure
