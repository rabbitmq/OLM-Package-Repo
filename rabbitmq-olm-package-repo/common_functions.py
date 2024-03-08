import os
import fileinput

# This function complete an overlay generator file (in ./generators) for Role, Clusterrole and Deployment
def create_overlay(release_file, kind, firstString, endString, file_generator, file_output):

    found = False
    parsing = False


    with open(release_file, 'r') as myfile:

        filestring = ""

        for line in myfile:
            if parsing == True:
    
                if line.find(endString) >=0:
                    if found == True:
                        os.system("cp " + str(file_generator) + " " + str(file_output))
                        with open(file_output, 'a') as myfile:
                            myfile.write(filestring)
                            found = False
                            parsing = False
                            filestring = ""
                            return
              
                    
                filestring = filestring + "          " + line
 
            if found == True:
                if (line.find(firstString) >= 0): 
                    parsing = True
  

            if line.find(kind) >= 0:
                found = True

# This function complete an overlay generator file (in ./generators) for Role, Clusterrole and Deployment
def replace_rabbitmq_cluster_operator_version_overlay(file_input, pattern1, pattern2):

    with fileinput.FileInput(file_input, inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace(pattern1, pattern2), end='')

def replace_rabbitmq_cluster_operator_image(file_input, pattern1, pattern2):

    with fileinput.FileInput(file_input, inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace(pattern1, pattern2), end='')

def replace_if_rabbitmq_webhook(file_input):

    with fileinput.FileInput(file_input, inplace=True, backup='.bak') as file:
        for line in file:
           print(line.replace("- admissionReviewVersions:", "  admissionReviewVersions:"), end='')

