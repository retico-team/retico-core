"""
Network Module
==============


A Module that allows for saving and loading networks from and to file as well as
starting and stopping them based on only a single module.
"""

import pickle


def load(filename: str):
    """Loads a network from file and returns a list of modules in that network.

    The connections between the module have been set according to the file.

    Args:
        filename (str): The path to the .rtc file containing a network.

    Returns:
        (list, list): A list of Modules that are connected and ready to be run
            and a list of connections between those modules.
    """
    mc_list = pickle.load(open(filename, "rb"))
    module_dict = {}
    module_list = []
    connection_list = []

    for m in mc_list[0]:
        mod = m["retico_class"](**m["args"])
        module_dict[m["id"]] = mod
        module_list.append(mod)
    for ida, idb in mc_list[1]:
        module_dict[idb].subscribe(module_dict[ida])
        connection_list.append((module_dict[idb], module_dict[ida]))

    return (module_list, connection_list)


def load_and_execute(filename):
    """Loads a network from file and runs it.

    The network is loaded via the load-Method. Before running the network, it is
    setup.

    The networks runs until some input on the console is given

    Args:
        filename (str): The path to the .rtc file containing a network.
    """
    module_list, _ = load(filename)

    for module in module_list:
        module.setup()

    for module in module_list:
        module.run(run_setup=False)

    input()

    for module in module_list:
        module.stop()


def _discover_modules(module):
    discovered_lb = []
    discovered_rbs = []
    lbs = module.left_buffers()
    for lb in lbs:
        if lb and lb.provider:
            discovered_lb.append(lb.provider)
    for rb in module.right_buffers():
        if rb and rb.consumer:
            discovered_rbs.append(rb.consumer)
    return set(discovered_lb), set(discovered_rbs)


def run(module):
    """Properly prepares and runs a network based on one module or a list of modules.

    The network is automatically discovered so that only one module of the network has
    to be given to this function for the whole network to be executed. The function
    first calls the `setup` function of each module in the network and then runs all
    modules.

    Args:
        module (Abstract Module or list): A module of the network or a list of multiple
            module of the network
    """
    m_list, _ = discover(module)

    for m in m_list:
        m.setup()

    for m in m_list:
        m.run(run_setup=False)


def stop(module):
    """Properlystops a network based on one module or a list of modules.

    The network is automatically discovered so that only one module of the network has
    to be given to this function for the whole network to be stopped.

    Args:
        module (Abstract Module or list): A module of the network or a list of multiple
            module of the network
    """
    m_list, _ = discover(module)

    for m in m_list:
        m.stop()


def discover(module):
    """Discovers all modules and connections from a single a list of modules.

    The network is automatically discovered by traversing all left and right buffers of
    the modules given. If the argment module is only a single module, the network that
    is constructed consist only of modules and connections reachable by that module. A
    segmented network needs a module of each part of the network.

    The function returns a touple containing a list of module and a list of connections
    between the modules. The connections are touples containing the providing module of
    the connection as the first element and the receiving module as the second element.

    Args:
        module (AbstractModule or list): A module of the network or a list of multiple
            modules of the network

    Returns:
        list, list: A list of modules in the first return value and
            a list of connections in the second return value.
    """
    if not isinstance(module, list):
        module = [module]
    undiscovered = set(module)
    discovered = []
    m_list = []
    c_list = []
    while undiscovered:
        current_module = undiscovered.pop()
        discovered.append(current_module)
        lbs, rbs = _discover_modules(current_module)
        for mod in lbs:
            if mod not in discovered:
                undiscovered.add(mod)
        for mod in rbs:
            if mod not in discovered:
                undiscovered.add(mod)
        m_list.append(current_module)
        for buf in current_module.right_buffers():
            c_list.append((buf.consumer, buf.provider))
    return m_list, c_list


def save(module, filename):
    """Saves a network to file given a module or a list of modules.

    The network is automatically detected by traversing all left and right
    buffers of the modules given. If the argument module is only a single
    module, the network that is being saved consists only of the module
    reachable from this module. If a network should be saved that is splitted
    into multiple parts, at least one module of each split has to be included
    into the module-list.

    Args:
        module (AbstractModule or list): A module of the network or a list of
            multiple modules of the network.
        filename (str): The path to where the network should be stored. This
            excludes the file-ending .rtc that will be automatically added by
            this function.
    """
    if not isinstance(module, list):
        module = [module]
    undiscovered = set(module)
    discovered = []
    m_list = []
    c_list = []
    while undiscovered:
        current_module = undiscovered.pop()
        discovered.append(current_module)
        lbs, rbs = _discover_modules(current_module)
        for mod in lbs:
            if mod not in discovered:
                undiscovered.add(mod)
        for mod in rbs:
            if mod not in discovered:
                undiscovered.add(mod)
        current_dict = {}
        current_dict["widget_name"] = current_module.name()
        current_dict["retico_class"] = current_module.__class__
        current_dict["args"] = current_module.get_init_arguments()
        current_dict["id"] = id(current_module)
        current_dict["meta"] = current_module.meta_data
        m_list.append(current_dict)
        for buf in current_module.right_buffers():
            c_list.append((id(buf.consumer), id(buf.provider)))
    pickle.dump([m_list, c_list], open("%s.rtc" % filename, "wb"))
