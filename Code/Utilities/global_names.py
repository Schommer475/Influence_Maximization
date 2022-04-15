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
adaptive_code = os.path.join(code,"adaptive_im")
temp_dir = os.path.join("..", "Files", "Temporary","Created")
process_temp = os.path.join("..", "Files", "Temporary","Process")
logging = os.path.join("..", "Files", "Temporary","Logs")

adaptive_temp = os.path.join(temp_dir, "adaptive_im")
non_adaptive_temp = os.path.join(temp_dir, "non_adaptive_im")
compilation_temp = os.path.join(temp_dir, "compilation")

facebook_network = "facebook_network.txt"
communities = "communities.pkl"
node2vec = "node2vec.exe"
