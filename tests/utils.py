import os


def validate_bundle_struct(output_directory):

    validate_folder_structure(output_directory)


def validate_folder_structure(output_directory):
    assert os.path.isdir(output_directory)
    assert os.path.isfile(output_directory + "/bundle.Dockerfile")
    assert os.path.isdir(output_directory + "/manifests")
    assert os.path.isdir(output_directory + "/metadata")
    assert os.path.isfile(
        output_directory + "/manifests/rabbitmq.clusterserviceversion.yaml"
    )
