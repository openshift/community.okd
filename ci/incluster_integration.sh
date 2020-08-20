#!/bin/bash

set -x

# IMAGE_FORMAT be in the form $registry/$org/$image:$$component, ie
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
kubectl delete job molecule-integration-test --wait --ignore-not-found

echo "Creating molecule test job"
cat << EOF | kubectl create -f -
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
  backoffLimit: 3
  completions: 1
  parallelism: 1
EOF

echo "Waiting for test job to report success"

# Ensure the child processes are killed
trap 'kill $(jobs -p) || true' SIGINT SIGTERM EXIT

# Wait for job completion in background
kubectl wait --for=condition=complete job/molecule-integration-test --timeout 5m &
completion_pid=$!

# Wait for job failure in background
kubectl wait --for=condition=failed job/molecule-integration-test --timeout 5m && exit 1 &
failure_pid=$!

wait -n $completion_pid $failure_pid
exit_code=$?

if (( $exit_code == 0 )); then
  echo "Molecule integration tests ran successfully"
else
  echo "Molecule integration tests failed, see logs for more information..."
  kubectl logs job/molecule-integration-test
fi

exit $exit_code
