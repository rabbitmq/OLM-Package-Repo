import fileinput
import os
from enum import Enum


class OperatorType(Enum):
    CLUSTER_OPERATOR = 1
    MESSAGING_TOPOLOGY_OPERATOR = 2


# This function complete an overlay generator file (in ./generators) for Role, Clusterrole and Deployment
def create_overlay(
    release_file, kind, firstString, endString, file_generator, file_output, filters
):
    found = False
    parsing = False

    with open(release_file, "r") as myfile:
        filestring = ""

        security_verbs = [
            "get",
            "list",
            "watch",
            "update",
            "create",
            "delete",
            "patch",
            "watch",
        ]
        special_cases = False
        for line in myfile:
            if parsing == True:
                if (
                    "pods/exec" in line
                    or "endpoints" in line
                    or "finalizers" in line
                    or "rabbitmqclusters" in line
                    or "services" in line
                ):
                    special_cases = True

                line_filtered = False
                for filter in filters:
                    if filter in line:
                        line_filtered = True

                if line_filtered is True:
                    if special_cases is False:
                        continue
                    else:
                        special_cases = False

                if special_cases is True:
                    for security_verb in security_verbs:
                        if security_verb in line:
                            special_cases = False

                if line.find(endString) >= 0:
                    if found == True:
                        os.system("cp " + str(file_generator) + " " + str(file_output))
                        with open(file_output, "a") as myfile:
                            myfile.write(filestring)
                            found = False
                            parsing = False
                            filestring = ""
                            return

                filestring = filestring + "          " + line

            if found == True:
                if line.find(firstString) >= 0:
                    parsing = True

            if line.find(kind) >= 0:
                found = True


# This function complete an overlay generator file (in ./generators) for Role, Clusterrole and Deployment
def replace_rabbitmq_cluster_operator_version_overlay(file_input, pattern1, pattern2):
    with fileinput.FileInput(file_input, inplace=True, backup=".bak") as file:
        for line in file:
            print(line.replace(pattern1, pattern2), end="")


# This function complete an overlay generator file (in ./generators) for Role, Clusterrole and Deployment
def replace_rabbitmq_security_overlay(file_input, securities):
    with fileinput.FileInput(file_input, inplace=True, backup=".bak") as file:
        for line in file:
            for security in securities:
                if security in line:
                    print(line.replace(pattern1, ""), end="")


def replace_rabbitmq_cluster_operator_image(file_input, pattern1, pattern2):
    with fileinput.FileInput(file_input, inplace=True, backup=".bak") as file:
        for line in file:
            print(line.replace(pattern1, pattern2), end="")


def replace_if_rabbitmq_webhook(file_input):
    with fileinput.FileInput(file_input, inplace=True, backup=".bak") as file:
        for line in file:
            print(
                line.replace(
                    "- admissionReviewVersions:", "  admissionReviewVersions:"
                ),
                end="",
            )


def get_operator_name(file_input):
    with open(file_input) as f:
        if "rabbitmqoperator/messaging-topology-operator" in f.read():
            return OperatorType.MESSAGING_TOPOLOGY_OPERATOR

    return OperatorType.CLUSTER_OPERATOR


def get_operator_last_tag(operator):
    last_tag_file = "./last_tag_file"
    os.system(
        "curl https://api.github.com/repos/rabbitmq/"
        + operator
        + "/tags | jq -r '.[0].name' > "
        + last_tag_file
    )

    with open(last_tag_file) as f:
        for line in f:
            pass

    last_line = "rabbitmq-" + operator + "." + line.strip()

    os.system("rm ./last_tag_file")

    return last_line
