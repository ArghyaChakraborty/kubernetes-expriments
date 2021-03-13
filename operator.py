import os
import json
import traceback
from kubernetes import client, config
from kubernetes.client.api.custom_objects_api import CustomObjectsApi

def process_cr_object(cr_obj: dict):
    """ This method processes a CR object """
    operation_type = cr_obj.get("type", None)

    crd_object = cr_obj.get("object", None)
    crd_object_metadata = crd_object.get("metadata", None) if crd_object else None

    object_kind = crd_object.get("kind", None) if crd_object else None
    object_name = crd_object_metadata.get("name", None) if crd_object_metadata else None
    object_uid = crd_object_metadata.get("uid", None) if crd_object_metadata else None
    object_resourceversion = crd_object_metadata.get("resourceVersion", None) if crd_object_metadata else None

    print("DETECTED: "+str(operation_type)+", "+str(object_kind)+", "+str(object_name)+", "+str(object_uid)+", "+str(object_resourceversion))
    return object_resourceversion


def event_loop(CRD_GROUP: str, CRD_VERSION: str, CRD_PLURAL: str, CRD_SCOPE: str, CRD_NAMESPACE: str):
    """ This method always watches for the CRD """
    v1=client.CustomObjectsApi()
    resource_version = None

    while(True):
        custom_objects = None
        if CRD_SCOPE == "Cluster":
            custom_objects = v1.list_cluster_custom_object(CRD_GROUP, CRD_VERSION, CRD_PLURAL, timeout_seconds=5, resource_version=resource_version, watch=True)
        elif CRD_SCOPE == "Namespaced":
            custom_objects = v1.list_namespaced_custom_object(CRD_GROUP, CRD_VERSION, CRD_NAMESPACE, CRD_PLURAL, timeout_seconds=5, resource_version=resource_version, watch=True)

        # The list() API returns objects as string of there are multiple CRs detcted
        # The API returns an object as a dictionary if only 1 CR is detected
        returned_objects_type = str(type(custom_objects))

        if "str" in returned_objects_type and str(custom_objects):
            cr_objects_list = str(custom_objects).split("\n")
            for cr_str in cr_objects_list:
                if not cr_str:
                    continue
                cr_obj = json.loads(cr_str)
                resource_version = process_cr_object(cr_obj)
        elif "dict" in returned_objects_type:
            resource_version = process_cr_object(custom_objects)


def main():
    """ This is the main method """
    CRD_GROUP = os.environ.get("CRD_GROUP", None)
    CRD_PLURAL = os.environ.get("CRD_PLURAL", None)
    CRD_SINGULAR = os.environ.get("CRD_SINGULAR", None)
    CRD_VERSION = os.environ.get("CRD_VERSION", None)
    CRD_SCOPE = os.environ.get("CRD_SCOPE", None)
    CRD_NAMESPACE = os.environ.get("CRD_NAMESPACE", "")
    try:
        if CRD_GROUP and CRD_PLURAL and CRD_SINGULAR and CRD_VERSION and CRD_SCOPE:
            if CRD_SCOPE == "Cluster":
                event_loop(CRD_GROUP, CRD_VERSION, CRD_PLURAL, CRD_SCOPE, CRD_NAMESPACE)
            elif CRD_SCOPE == "Namespaced":
                if CRD_NAMESPACE:
                    event_loop(CRD_GROUP, CRD_VERSION, CRD_PLURAL, CRD_SCOPE, CRD_NAMESPACE)
                else:
                    raise Exception("For Namespaced CRDs, Namespace is required. Please pass it as environment variable")
            else:
                raise Exception("CRD Scope has to be either Cluster OR Namespaced. Please provide appropriate choice")
        else:
            raise Exception("CRD Group OR Plural OR Singular OR Version OR Scope is undefined. Please provide them as environment variables")
    except Exception as ex:
        print("Caught exception : "+str(ex))
        print(str(traceback.format_exc()))

if __name__ == "__main__":
    in_cluster = os.environ.get("KUBERNETES_SERVICE_HOST", None)
    if in_cluster:
        config.load_incluster_config()
    else:
        config.load_kube_config()
    main()