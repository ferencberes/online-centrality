import json, shutil, os
from shutil import copyfile
from os.path import expanduser

class ParamHelper():
    def __init__(self, pipeline_config_path, relative_path_in_repo, verbose=False):
        """Through ParamHelper can load and store notebook related custom and default parameters."""
        self.pipeline_config_path = pipeline_config_path
        self.root_directory = os.path.abspath("/".join(self.pipeline_config_path.split("/")[:-2]))
        self.rel_nb_path = relative_path_in_repo 
        self.PARAMS = {}
        self.DEFAULTS = {}
        self.verbose = verbose
        self._load_params()
        
    def _load_defaults(self):
        with open(self.pipeline_config_path) as f:
            self.pipeline_cfg = json.loads(f.read())
        self.pipeline_name = self.pipeline_cfg["name"]
        if "default_config" in self.pipeline_cfg:
            self.DEFAULTS = self.pipeline_cfg["default_config"]

    def _load_notebook_params(self):
        for nb in self.pipeline_cfg["notebooks"]:
            if nb["path"] == self.rel_nb_path and "config" in nb:
                self.PARAMS = dict(nb["config"])
                break

    def _load_params(self):
        """Loading parameters from pipeline json configuration"""
        print(self.root_directory)
        self._load_defaults()
        print("Default parameters:")
        print(self.DEFAULTS)
        self._load_notebook_params()
        print("Custom parameters:")
        print(self.PARAMS)
        
    def get(self, param_name):
        """Access parameters by key 'param_name'. This function first searches among notebook related custom variables then among default variables."""
        if param_name in self.PARAMS:
            if self.verbose:
                print("Using parameter: %s=%s" % (param_name, str(self.PARAMS[param_name])))
            return self.PARAMS[param_name]
        elif param_name in self.DEFAULTS:
            print("Using default parameter: %s=%s" % (param_name, str(self.DEFAULTS[param_name])))
            return self.DEFAULTS[param_name]
        else:
            raise RuntimeError("Parameter '%s' not found in pipeline config %s !!!" % (param_name, self.pipeline_config_path))


class ConfigGenerator():
    def __init__(self, pipeline_cfg_file):
        """ConfigGenerator manages and stores parameters in pipeline config json files"""
        self.pipeline_cfg_file = pipeline_cfg_file
        self.pipeline_cfg = {}
        self._init()
        
    def _init(self):
        """Initialize ConfigGenerator"""
        self._load_config()
        self._clear_config()
        
    def _load_config(self):
        """Load pipeline config json file"""
        with open(self.pipeline_cfg_file) as f_in:
            self.pipeline_cfg = json.loads(f_in.read())
            
    def _clear_config(self):
        """Clear pipeline config json file. Deleting former parameters."""
        if "default_config" in self.pipeline_cfg:
            del self.pipeline_cfg["default_config"]
        self.notebook_names = []
        for categ in ["notebooks", "py_scripts"]:
            non_clones = []
            for nb in self.pipeline_cfg[categ]:
                print(nb)
                if "config" in nb:
                    del nb["config"]
                if "is_clone" in nb and nb["is_clone"] == "yes":
                    # delete clone file
                    clone_path = "../" + nb["path"]
                    if os.path.exists(clone_path):
                        os.remove(clone_path)
                else:
                    nb["is_clone"] = "no"
                    non_clones.append(nb)
                    self.notebook_names.append(nb["name"])
            self.pipeline_cfg[categ] = non_clones

    def load_params(self, defaults, parameters=None):
        """Load variables stored in 'parameters' and 'defaults' into pipeline json config."""
        if parameters == None:
            PARAMETERS = {}
            for nb_name in self.notebook_names:
                PARAMETERS[nb_name] = []
            #print(PARAMETERS)
            parameters = PARAMETERS
        clone_deps = {}
        for categ in ["notebooks", "py_scripts"]:
            clones = []
            for nb in self.pipeline_cfg[categ]:
                clone_deps[nb["name"]] = []
                if len(parameters[nb["name"]]) > 0:
                    for i in range(len(parameters[nb["name"]])):
                        # first parameter instance is assigned to original notebook
                        if i == 0:
                            nb["config"] = parameters[nb["name"]][i]
                            continue
                        # other parameter instances are assigned to clones
                        clone = {"is_clone": "yes", "type": nb["type"], "kernel_type": nb["kernel_type"]}
                        clone["name"] = "%s_CLONE_%i" % (nb["name"], i)
                        if categ == "notebook":
                            clone["path"] = "%s_CLONE_%i.ipynb" % (".".join(nb["path"].split(".")[:-1]), i)
                        elif categ == "py_scripts":
                            clone["path"] = "%s_CLONE_%i.py" % (".".join(nb["path"].split(".")[:-1]), i)
                        clone["config"] = parameters[nb["name"]][i]
                        clone["pipeline_status"] = nb["pipeline_status"]
                        clone_deps[nb["name"]].append(clone["name"])
                        if "dependencies" in nb:
                            clone["dependencies"] = nb["dependencies"]
                        # create clone file
                        copyfile("../" + nb["path"], "../" + clone["path"])
                        clones.append(clone)
            self.pipeline_cfg[categ] = self.pipeline_cfg[categ] + clones
        self._resolve_dependencies(clone_deps)
        self.pipeline_cfg["default_config"] = defaults
        
    def _resolve_dependencies(self, clone_deps):
        """Resolve pipeline dependencies among original and clone notebooks."""
        print(clone_deps)
        for categ in ["notebooks", "py_scripts"]:
            for nb in self.pipeline_cfg[categ]:
                if "dependencies" in nb:
                    for dep in nb["dependencies"]:
                        if dep in clone_deps:
                            for c_dep in clone_deps[dep]:
                                if not c_dep in nb["dependencies"]:
                                    nb["dependencies"].append(c_dep)
        
    def save(self):
        """Save all parameters into pipeline json file"""
        with open(self.pipeline_cfg_file, 'w') as f_out:
            f_out.write(json.dumps(self.pipeline_cfg, indent=3, sort_keys=True))
        print("%s pipeline config was updated!" % self.pipeline_cfg["name"])
        
