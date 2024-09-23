"""
Network Module
==============


A Module that allows for saving and loading networks from and to file as well as
starting and stopping them based on only a single module.
"""

from collections import deque
import logging
import pickle
import threading
import time
import retico_core
import structlog


def filter_all(_, __, event_dict):
    if event_dict.get("module"):
        raise structlog.DropEvent
    return event_dict


# LOG_FILTERS = []
LOG_FILTERS = [filter_all]


class Logger:

    def __init__(self, logger):
        self.logger = logger
        self.queue = deque()
        t = threading.Thread(target=self.run_logging)
        t.start()

    def append(self, data, level):
        self.queue.append((data, level))

    def bind(self, **kwargs):
        self.logger.bind(**kwargs)

    def debug(self, data):
        self.queue.append((data, "debug"))

    def info(self, data):
        self.queue.append((data, "info"))

    def warning(self, data):
        self.queue.append((data, "warning"))

    def run_logging(self):
        while True:
            if len(self.queue) == 0:
                time.sleep(0.1)
                continue
            data, level = self.queue.popleft()
            print("lala")
            print(self.logger)
            getattr(self.logger, level)(data)


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


def load_and_execute(filename, log_folder="logs/run"):
    """Loads a network from file and runs it.

    The network is loaded via the load-Method. Before running the network, it is
    setup.

    The networks runs until some input on the console is given

    Args:
        filename (str): The path to the .rtc file containing a network.
    """
    module_list, _ = load(filename)

    log_folder = retico_core.log_utils.create_new_log_folder(log_folder)

    for module in module_list:
        module.setup(log_folder=log_folder)

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


def configurate_logger(log_path):
    """
    Configure structlog's logger and set general logging args (timestamps,
    log level, etc.)

    Args:
        filename: (str): name of file to write to.

        foldername: (str): name of folder to write to.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        force=True,  # <-- HERE BECAUSE IMPORTING SOME LIBS LIKE COQUITTS WAS BLOCKING THE LOGGINGS SYSTEM
    )

    processors = (
        [
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.dict_tracebacks,
        ]
        + LOG_FILTERS
        + [structlog.dev.ConsoleRenderer(colors=True)]
    )

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Logger pour le terminal
    terminal_logger = structlog.get_logger("terminal")
    # self.terminal_logger = self.terminal_logger.bind(module=self.name())

    # Configuration du logger pour le fichier
    file_handler = logging.FileHandler(log_path, mode="a", encoding="UTF-8")
    file_handler.setLevel(logging.INFO)

    # Créer un logger standard sans handlers pour éviter la duplication des logs dans le terminal
    file_only_logger = logging.getLogger("file_logger")
    file_only_logger.addHandler(file_handler)
    file_only_logger.propagate = (
        False  # Empêche la propagation des logs vers les loggers parents
    )

    # Encapsuler ce logger avec structlog
    file_logger = structlog.wrap_logger(
        file_only_logger,
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),  # Format JSON pour le fichier
        ],
    )
    # self.file_logger = self.file_logger.bind(module=self.name())

    return terminal_logger, file_logger


def run(module, log_folder="logs/run"):
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

    # that is what creates 2 log_folder instead of 1
    log_folder = retico_core.log_utils.create_new_log_folder(log_folder)

    # create logger singleton
    terminal_logger, file_logger = configurate_logger(log_path=log_folder)
    # terminal_logger_class = Logger(logger=terminal_logger)
    # terminal_logger_class = Logger(logger=file_logger)

    for m in m_list:
        m.setup(
            log_folder=log_folder,
            terminal_logger=terminal_logger,
            file_logger=file_logger,
        )

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
