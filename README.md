### To create docker image
1. docker build -t test-python-operator .
2. TAG=latest
4. docker push test-python-operator:$TAG

### To deploy in kubernetes cluster
1. Ensure the operator image is present in artifactory
2. Ensure the kubernetes config is located at `HOME/.kube/config`
3. TARGET_NS=default
4. cd <directory where the project is cloned>/arghya-test-operator/
5. To Install: helm install arghya-test-operator . -n $TARGET_NS
6. To Delete: helm delete arghya-test-operator -n $TARGET_NS

### To check on the created pod
- `TARGET_NS=default`
- `kubectl get pods -n $TARGET_NS | grep arghya` - This will provide the pod id
- `kubectl exec -it <pod id> bash -n $TARGET_NS -c arghya-test-python-job` - This will get you inside the operator container
- `kubectl exec -it <pod id> bash -n $TARGET_NS -c arghya-test-job` - This will get you inside the kubectl container

### Intent of the project
- Create a very simple `Custom Resource Definition` or CRD
- Create an `Operator` which listens to addition/modification or deletion of Custom Resources or CRs and print sme meta data about the CRs
- Deploy some `CRs` and test the code  

Following sections describe each of the operations in detail

### Creation of Custom Resource Definition
- The specification could be found in `arghya-test-operator/templates/spec.yaml`
- Following objects are defined in the spec file:  
    * Service account: Which allows a role to be assigned & based on which the pods could query K8S
    * RBAC: Provides role to the Service account so that K8S could be queried
    * Job: Creates a Job with 2 pods: one for kubectl and another with `python based operator`
    * CRD: The Custom Resource Definition itself has just 1 property and a very simply one
- All above objects could be deployed with helm. Please see section `To deploy in kubernetes cluster` for deployment instruction

### Creation of Operator
- The operator is a simple Python based operator
- It used python `kubernetes` module to detect CRs
- The python file is located in `operator.py`
- The operator could be tested locally in laptop or in cluster pod
- Python module requirements are listed in `requirements.txt`
- For local testing:  
    ```
    export CRD_GROUP=arghya.test
    export CRD_PLURAL=testcrds
    export CRD_SINGULAR=testcrd
    export CRD_VERSION=v1 
    export CRD_SCOPE=Cluster
    python operator.py
    ```
- For cluster testing: deploy the project in cluster.  Please see section `To deploy in kubernetes cluster` for deployment instruction
- Before the project could be deployed in kubernetes cluster, docker image should be created. Please see section `To create docker image` for instructions

### To test the CRD and Operator
1. Deploy the helm chart in kubernetes cluster
2. Tail the logs from the created pod
3. Now, deploy the CR:
```
kubectl apply -f test_cr.yaml
```
4. Now delete the CR:
```
kubectl delete -f test_cr.yaml
```
5. You should see following entries in pod log:
```
DETECTED: ADDED, TestCRD, test-arghya-crd-1, 9d211d06-25cc-412c-b553-595d1205f166, 17763207
DETECTED: DELETED, TestCRD, test-arghya-crd-1, 9d211d06-25cc-412c-b553-595d1205f166, 17763908
```
