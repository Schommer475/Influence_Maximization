from importlib.metadata import files
import os

files_dir = os.path.join("..","Files")
code = "."
resources = os.path.join(files_dir,"Resources")
outputs = os.path.join(files_dir,"Outputs")
namespace = os.path.join(files_dir, "Namespaces")
inputs = os.path.join(files_dir, "Inputs")
common_inputs = os.path.join(inputs, "common")
temp_inputs = os.path.join(inputs, "temp")
global_namespace = os.path.join(namespace,"global_name_vars.json")
registered_namespace = os.path.join(namespace,"registered_items.json")
application_namespace = os.path.join(namespace,"ApplicationNames")
algorithm_namespace = os.path.join(namespace,"AlgorithmNames")
joint_namespace = os.path.join(namespace,"JointNames")
temp_dir = os.path.join(files_dir, "Temporary","Created")
process_temp = os.path.join(files_dir, "Temporary","Process")
logging = os.path.join(files_dir, "Temporary","Logs")


facebook_network = "facebook_network.txt"
communities = "communities.pkl"
node2vec = "node2vec.exe"
