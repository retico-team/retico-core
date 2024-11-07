"""
Log Utils Module
================

This file defines the classes and functions of a new logging system for retico, which provides
retico modules with the capacity to create structured (dictionary) log messages that they can either
store in a log file, or print in the terminal. 
The file is divided in 3 parts : 
- Loggers & Functions : defines the terminal and file logger classes, and logging-related functions
for retico modules.
- Log filters : defines general filters that can be used in the log configuration to filter out the 
desired log messages.
- Plot logs : defines general functions used for retico system's execution vizualization (after 
execution, or in real time during an execution). 
"""

import datetime
import os
import json
from pathlib import Path
import re
import threading
import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import structlog


#####################
# Loggers & Functions
#####################


class TerminalLogger(structlog.BoundLogger):
    """Dectorator / Singleton class of structlog.BoundLogger, that is used to configure / initialize
    once the terminal logger for the whole system."""

    def __new__(cls, filters=None):
        if not hasattr(cls, "instance"):
            # Define filters for the terminal logs
            if filters is not None:
                log_filters = filters
            else:
                log_filters = LOG_FILTERS

            # configure structlog to have a terminal logger
            processors = (
                [
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.add_log_level,
                ]
                + log_filters
                + [structlog.dev.ConsoleRenderer(colors=True)]
            )
            structlog.configure(
                processors=processors,
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
            terminal_logger = structlog.get_logger("terminal")

            # log info to cache the logger, using the config's cache_logger_on_first_use parameter
            terminal_logger.info("init terminal logger")

            # set the singleton instance
            cls.instance = terminal_logger
        return cls.instance


class FileLogger(structlog.BoundLogger):
    """Dectorator / Singleton class of structlog.BoundLogger, that is used to configure / initialize
    once the file logger for the whole system."""

    def __new__(cls, log_path="logs/run"):
        if not hasattr(cls, "instance"):
            # configure structlog to have a file logger
            structlog.configure(
                processors=[
                    structlog.processors.add_log_level,
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.ExceptionRenderer(),
                    structlog.processors.JSONRenderer(),
                ],
                logger_factory=structlog.WriteLoggerFactory(
                    file=Path(log_path).open("wt", encoding="utf-8")
                ),
                cache_logger_on_first_use=True,
            )
            file_logger = structlog.get_logger("file_logger")

            # log info to cache the logger, using the config's cache_logger_on_first_use parameter
            file_logger.info("init file logger")

            # set the singleton instance
            cls.instance = file_logger
        return cls.instance


def create_new_log_folder(log_folder):
    """Function that creates a new folder to store the current run's log file. Find the last run's
    number and creates a new log folder with an increment of 1.

    Args:
        log_folder (str): the log_folder path where every run's log folder is stored.

    Returns:
        str: returns the final path of the run's log_file, with a format : logs/run_33/logs.log
    """
    cpt = 0
    log_folder_full_path = log_folder + "_" + str(cpt)
    while os.path.isdir(log_folder_full_path):
        cpt += 1
        log_folder_full_path = log_folder + "_" + str(cpt)
    os.makedirs(log_folder_full_path)
    filepath = log_folder_full_path + "/logs.log"
    return filepath


def configurate_logger(log_path="log/run", filters=None):
    """
    Configure structlog's logger and set general logging args (timestamps,
    log level, etc.)

    Args:
        log_path: (str): logs folder's path.
        filters: (list): list of function that filters logs that will be outputted in the terminal.
    """
    log_path = create_new_log_folder(log_path)
    terminal_logger = TerminalLogger(filters=filters)
    file_logger = FileLogger(log_path)
    return terminal_logger, file_logger


def log_exception(module, exception):
    """function that enable modules to log the encountered exceptions to both logger (terminal and
    file) in
    a unified way (and factorize code).

    Args:
        module (object): the module that encountered the exception.
        exception (Exception): the encountered exception.
    """
    module.terminal_logger.exception(
        "The module encountered the following exception while running :"
    )
    module.file_logger.exception(
        "The module encountered the following exception while running :",
    )
    # could introduce errors while parsing the json logs,
    # because of the " chars in the exception tracebacks
    # module.file_logger.exception(
    #     "The module encountered the following exception while running :",
    #     tarcebacks=[
    #         tb.replace('"', "'") for tb in traceback.format_tb(exception.__traceback__)
    #     ],
    # )


#############
# Log Filters
#############


def filter_has_key(_, __, event_dict, key):
    """Delete the log if it has the key in its event_dict.

    Args:
        event_dict (dict): the log message's dict, containing all parameters passed during logging.
        key (str): the key to match in event_dict.

    Returns:
        dict : returns the log_message's event_dict if it went through the filter.
    """
    if event_dict.get(key):
        raise structlog.DropEvent
    return event_dict


def filter_does_not_have_key(_, __, event_dict, key):
    """Delete the log if it doesn't have the key in its event_dict.

    Args:
        event_dict (dict): the log message's dict, containing all parameters passed during logging.
        key (str): the key to match in event_dict.

    Returns:
        dict : returns the log_message's event_dict if it went through the filter.
    """
    if not event_dict.get(key):
        raise structlog.DropEvent
    return event_dict


def filter_value_in_list(_, __, event_dict, key, values):
    """Delete the log if it has the key, and the corresponding value is in values.

    Args:
        event_dict (dict): the log message's dict, containing all parameters passed during logging.
        key (str): the key to match in event_dict.
        values (list[str]): values to match in event_dict.

    Returns:
        dict : returns the log_message's event_dict if it went through the filter.
    """
    if event_dict.get(key):
        if event_dict.get(key) in values:
            raise structlog.DropEvent
    return event_dict


def filter_value_not_in_list(_, __, event_dict, key, values):
    """Delete the log if it has the key, and the corresponding value is not in values.

    Args:
        event_dict (dict): the log message's dict, containing all parameters passed during logging.
        key (str): the key to match in event_dict.
        values (list[str]): values to match in event_dict.

    Returns:
        dict : returns the log_message's event_dict if it went through the filter.
    """
    if event_dict.get(key):
        if event_dict.get(key) not in values:
            raise structlog.DropEvent
    return event_dict


def filter_all_from_modules(_, __, event_dict):
    """function that filters all log message that has a `module` key.
    (every retico module binds this parameter, so it would delete every log from retico modules)

    Args:
        event_dict (dict): the log message's dict, containing all parameters passed during logging.

    Returns:
        dict : returns the log_message's event_dict if it went through the filter.
    """
    if event_dict.get("module"):
        raise structlog.DropEvent
    return event_dict


def filter_conditions(_, __, event_dict, conditions):
    """
    filter function for the structlog terminal logger.
    This function only keeps logs that matchs EVERY condition.
    A condition is a tuple (key, values). To verify the condition, the log message (a dict) has to
    have the `key`, and the value corresponding to the key in log message has to be in the
    condition's `values` list.

    Example :
    conditions = [("module":["Microphone Module"]), ("event":["create_iu", "append UM"])]
    Meaning of the conditions :
    KEEP IF module is "Microphone Module" AND event is in ["create_iu", "append UM"]

    Args:
        event_dict (dict): the log message's dict, containing all parameters passed during logging.
        conditions (list[tuple[str,list[str]]]): the conditions the event_dict needs to match.

    Returns:
        dict : returns the log_message's event_dict if it went through the filter.
    """
    for key, values in conditions:
        if event_dict.get(key):
            if event_dict.get(key) in values:
                continue
        raise structlog.DropEvent
    return event_dict


def filter_cases(_, __, event_dict, cases):
    """
    filter function for the structlog terminal logger.
    This function keeps logs that matchs ANY case. A case is a list of conditions, EVERY condition
    has to be verified to verify the case. ie. case == conditions, from the filter_conditions
    function.
    A condition is a tuple (key, values). To verify the condition, the log message (a dict) has to
    have the `key`, and the value corresponding to the key in log message has to be in the
    condition's `values` list.
    A case is a list of conditions, ie. a list of tuple (key, value).
    cases are a list of list of conditions.

    Example :
    cases = [[("module":["Micro"]), ("event":["create_iu", "append UM"])],
    [("module":["Speaker"]), ("event":["create_iu"])]]
    Meaning of the cases :
    KEEP IF ((module is "Microphone Module" AND event is in ["create_iu", "append UM"])
    OR (module is "Speaker Module" AND event is "append UM"))

    Args:
        event_dict (dict): the log message's dict, containing all parameters passed during logging.
        cases (list[list[tuple[str,list[str]]]]): the cases the event_dict needs to match.

    Returns:
        dict : returns the log_message's event_dict if it went through the filter.
    """
    for conditions in cases:
        boolean = True
        for key, values in conditions:
            if event_dict.get(key):
                if event_dict.get(key) in values:
                    continue
            boolean = False
        if boolean:
            return event_dict
    raise structlog.DropEvent


def filter_all_but_warnings_and_errors(_, __, event_dict):
    """function that filters all log message that is not a warning or an error.

    Args:
        event_dict (dict): the log message's dict, containing all parameters passed during logging.

    Returns:
        dict : returns the log_message's event_dict if it went through the filter.
    """
    cases = [
        [
            (
                "level",
                [
                    "warning",
                    "error",
                ],
            ),
        ],
    ]
    return filter_cases(_, _, event_dict, cases=cases)


# LOG_FILTERS = []
# LOG_FILTERS = [filter_all_from_modules]
LOG_FILTERS = [filter_all_but_warnings_and_errors]


###########
# Plot logs
###########

THREAD_ACTIVE = False
REFRESHING_TIME = 1
LOG_FILE_PATH = None
PLOT_SAVING_PATH = None
PLOT_CONFIG_PATH = None
MODULE_ORDER = None


def store_log(
    log_data,
    plot_config,
    events,
    event_name_in_config,
    module_name_in_config,
    event_name_for_plot,
    module_name_for_plot,
    date,
):
    """function used to add to log_data the log events and their timestamps if they match the
    config_file conditions.

    Args:
        log_data (dict): the data structure where the logs that will be plotted are stored.
        plot_config (dict): the plot_config contains the events that will be plotted, and their
            corresponding plot information.
        events (dict): dictionary containing all events to plot for that event.
        event (str): the event name in log message.
        module (str): the module name in log message.
        event_name_for_plot (str): the log's event name.
        module_name_for_plot (str): A shorter version of the module's name (for the plot).
        date (date): the log's timestamp.

    Returns:
        tuple[dict[],bool]: Returns the logs storing data structure, and a boolean that is True if
        the event has been stored, False if it hasn't.
    """
    boolean = events is not None and event_name_in_config in events
    if boolean:
        if event_name_for_plot not in log_data["events"]:
            log_data["events"][event_name_for_plot] = {"x_axis": [], "y_axis": []}
            if (
                "plot_settings"
                in plot_config[module_name_in_config]["events"][event_name_in_config]
            ):
                log_data["events"][event_name_for_plot]["plot_settings"] = plot_config[
                    module_name_in_config
                ]["events"][event_name_in_config]["plot_settings"]
        log_data["events"][event_name_for_plot]["y_axis"].append(module_name_for_plot)
        log_data["events"][event_name_for_plot]["x_axis"].append(date)
    return log_data, boolean


def plot(
    log_file_path,
    plot_saving_path,
    plot_config,
    events_all_modules,
    module_order=None,
    log_data={"events": {}},
    line_cpt=0,
    window_duration=None,
):
    """function used to create a plot for a system run from the corresponding log file. Can be used
    to plot live or after the execution.

    Args:
        log_file_path (str, optional): path to the folder corresponding to the desired run to plot.
            Defaults to None.
        plot_saving_path (str, optional): path to the folder where the plot will be saved. Defaults
            to None.
        plot_config (dict): the plot_config contains the events that will be plotted, and their
            corresponding plot information.
        events_all_modules (dict): the log events that will be retrieved for every module.
        module_order (list[str], optional): Custom order of the modules in the final plot (first in
            the list is the lowest on the plot). Defaults to None
        log_data (dict, optional): If called from the plot_live function, used to store current
            log_file logs and only retrieve new logs at each loop of live plotting. Defaults to
            {"events": {}}.
        line_cpt (int, optional): If called from the plot_live function, used to only retrieve new
            logs at each loop of plot_live (log line > line_cpt). Defaults to 0.
        window_duration (int, optional): a fixed time window (in seconds) preceding the current time
            which defines all the logs that will be used for the real-time plot. Defaults to None.


    Returns:
        tuple[dict[],int]: Returns the already retrieved and processed logs with the line_cpt to the
        last line processed. Used to only process new logs at each plot_live loop.
    """
    nb_pb_line = 0
    terminal_logger = TerminalLogger()

    with open(log_file_path, encoding="utf-8") as f:
        lines = f.readlines()
        new_pointer = len(lines)
        lines = lines[line_cpt:]
        line_cpt = new_pointer

    # Retrieve logs : store data from log_file to log_data if a matching pair of "module" and
    # "event" can be found in plot_config
    for l in lines:
        try:
            log = json.loads(l)

            module_name = log["module"] if "module" in log else None
            event_name = log["event"] if "event" in log else None

            if module_name is None:
                continue

            date = datetime.datetime.fromisoformat(log["timestamp"])
            date_plt = mdates.date2num(date)
            module_name_for_plot = module_name.split(maxsplit=1)[0]
            # module_name_for_plot = " ".join(module_name.split()[:1])

            # log from event, from most specific to least specific
            events_specific_module = None
            if module_name in plot_config and "events" in plot_config[module_name]:
                events_specific_module = plot_config[module_name]["events"]

            # if we specified in the config to log specific event from specific module
            log_data, has_been_stored = store_log(
                log_data,
                plot_config,
                events_specific_module,
                event_name,
                module_name,
                module_name_for_plot + "_" + event_name,
                module_name_for_plot,
                date_plt,
            )
            if has_been_stored:
                continue

            # if we specified in the config to log specific event from any module
            log_data, has_been_stored = store_log(
                log_data,
                plot_config,
                events_all_modules,
                event_name,
                "any_module",
                event_name,
                module_name_for_plot,
                date_plt,
            )
            if has_been_stored:
                continue

            # if we specified in the config to log any event from specific module
            log_data, has_been_stored = store_log(
                log_data,
                plot_config,
                events_specific_module,
                "any_event",
                module_name,
                "other_events_" + module_name_for_plot,
                module_name_for_plot,
                date_plt,
            )
            if has_been_stored:
                continue

            # if we specified in the config to log any event from any module
            log_data, has_been_stored = store_log(
                log_data,
                plot_config,
                events_all_modules,
                "any_event",
                "any_module",
                "other_events",
                module_name_for_plot,
                date_plt,
            )

        except Exception:
            nb_pb_line += 1

    # put all events data in the plot
    _, ax = plt.subplots(figsize=(10, 5))
    try:
        for event_name, event_data in log_data["events"].items():
            x = event_data["x_axis"]
            y = event_data["y_axis"]
            # re-order if the module_order parameter is set
            if module_order is not None:
                x_np = np.array(event_data["x_axis"])
                y_np = np.array(event_data["y_axis"])
                reordered_indices = np.concatenate(
                    [np.where(y_np == o)[0] for o in module_order]
                )
                x = x_np[reordered_indices]
                y = y_np[reordered_indices]
            if "plot_settings" in event_data:
                ax.plot(
                    x,
                    y,
                    event_data["plot_settings"]["marker"],
                    color=event_data["plot_settings"]["marker_color"],
                    label=event_name,
                    markersize=event_data["plot_settings"]["marker_size"],
                )
            else:
                ax.plot(
                    event_data["x_axis"],
                    event_data["y_axis"],
                    "|",
                    color="g",
                    label=event_name,
                    markersize=20,
                )
    except Exception:
        terminal_logger.exception()

    # create and save the plot
    ax.grid(True)
    ax.legend(fontsize="7", loc="center left")
    # plt.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S.%f"))
    plt.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%M:%S"))
    plt.xticks(fontsize=7)
    #
    if window_duration is not None:
        last_date = datetime.datetime.fromisoformat(json.loads(lines[-1])["timestamp"])
        padding = 5
        end_window = last_date + datetime.timedelta(seconds=last_date.second % padding)
        start_window = end_window - datetime.timedelta(seconds=window_duration)
        ax.set_xlim(left=start_window, right=end_window)
    #
    # ax.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
    ax.xaxis.set_major_locator(mdates.SecondLocator(bysecond=range(0, 61, 5)))
    ax.xaxis.set_minor_locator(mdates.SecondLocator(bysecond=range(0, 61, 1)))
    plot_filename = plot_saving_path + "/plot_IU_exchange.png"
    plt.savefig(plot_filename, dpi=200, bbox_inches="tight")
    plt.close()

    return log_data, line_cpt


def extract_number(string):
    """extract the number from the string.

    Args:
        string (str): string to analyze.

    Returns:
        int: the extracted number.
    """
    s = re.findall("\d+$", string)
    return (int(s[0]) if s else -1, string)


def plot_live(module_order=None):
    """a looping function that creates a plot from the current run's log_file each `REFRESHING_TIME`
    seconds (if it's the biggest run number in your `logs` folder)

    Args:
        module_order (list[str], optional): Custom order of the modules in the final plot (first in
        the list is the lowest on the plot). Defaults to None.
    """
    global LOG_FILE_PATH, PLOT_SAVING_PATH

    if LOG_FILE_PATH is None or PLOT_SAVING_PATH is None:
        subfolders = [f.path for f in os.scandir("logs/") if f.is_dir()]
        max_run = max(subfolders, key=extract_number)
        LOG_FILE_PATH = max_run + "/logs.log"
        PLOT_SAVING_PATH = "run_plots/" + max_run.split("/")[-1]
        if not os.path.isdir(PLOT_SAVING_PATH):
            os.makedirs(PLOT_SAVING_PATH)

    if PLOT_CONFIG_PATH is None:
        raise NotImplementedError
    else:
        with open(PLOT_CONFIG_PATH, encoding="utf-8") as f:
            plot_config = json.load(f)

    events_all_modules = None
    if "any_module" in plot_config and "events" in plot_config["any_module"]:
        events_all_modules = plot_config["any_module"]["events"]

    log_data = {"events": {}}
    line_cpt = 0

    while THREAD_ACTIVE:
        time.sleep(REFRESHING_TIME)
        log_data, line_cpt = plot(
            log_file_path=LOG_FILE_PATH,
            plot_saving_path=PLOT_SAVING_PATH,
            plot_config=plot_config,
            events_all_modules=events_all_modules,
            module_order=module_order,
            log_data=log_data,
            line_cpt=line_cpt,
            window_duration=WINDOW_DURATION,
        )


def plot_once(
    plot_config_path, log_file_path=None, plot_saving_path=None, module_order=None
):
    """Create a plot for a previous system run from the corresponding log file.

    Args:
        plot_config_path (str): the path to the plot configuration file.
        log_file_path (str, optional): path to the folder corresponding to the desired run to plot.
            Defaults to None.
        plot_saving_path (str, optional): path to the folder where the plot will be saved. Defaults
            to None.
        module_order (list[str], optional): Custom order of the modules in the final plot (first in
            the list is the lowest on the plot). Defaults to None.
    """
    if log_file_path is None or plot_saving_path is None:
        subfolders = [f.path for f in os.scandir("logs/") if f.is_dir()]
        max_run = max(subfolders, key=extract_number)
        log_file_path = max_run + "/logs.log"
        plot_saving_path = "run_plots/" + max_run.split("/")[-1]
        if not os.path.isdir(plot_saving_path):
            os.makedirs(plot_saving_path)
    with open(plot_config_path, encoding="utf-8") as f:
        plot_config = json.load(f)
    events_all_modules = None
    if "any_module" in plot_config and "events" in plot_config["any_module"]:
        events_all_modules = plot_config["any_module"]["events"]
    plot(
        log_file_path=log_file_path,
        plot_saving_path=plot_saving_path,
        plot_config=plot_config,
        events_all_modules=events_all_modules,
        module_order=module_order,
    )


def setup_plot_live():
    """a function that initializes and starts a thread from the looping function `plot_live`, to
    create a plot from the log_file in real time passively."""
    threading.Thread(target=plot_live).start()


def stop_plot_live():
    """a function that stops plot_live's thread. Supposed to be called at the end of the run by the
    `network`"""
    global THREAD_ACTIVE
    THREAD_ACTIVE = False


def configurate_plot(
    is_plot_live=False,
    refreshing_time=1,
    plot_config_path=None,
    log_file_path=None,
    plot_saving_path=None,
    module_order=None,
    window_duration=5,
):
    """A function that configures the global parameters related to plot configuration.
    These global parameters will be used by the `plot_live` function to create a plot from
    the current run's log_file in real time.

    Args:
        plot_live (bool, optional): If set to True, a plot from the current run's log_file will be
            created in real time. If set to False, it will only be created at the end of the run.
            Defaults to False.
        refreshing_time (int, optional): The refreshing time (in seconds) between two creation of
            plots when `plot_live` is set to `True`. Defaults to 1.
        plot_config_path (str): the path to the plot configuration file.
        log_file_path (str, optional): path to the folder corresponding to the desired run to plot.
            Defaults to None.
        plot_saving_path (str, optional): path to the folder where the plot will be saved. Defaults
            to None.
        module_order (list[str], optional): Custom order of the modules in the final plot (first in
            the list is the lowest on the plot). Defaults to None.
        window_duration (int, optional): a fixed time window (in seconds) preceding the current time
            which defines all the logs that will be used for the real-time plot. Defaults to 5.
    """
    global THREAD_ACTIVE, REFRESHING_TIME, LOG_FILE_PATH, PLOT_SAVING_PATH, PLOT_CONFIG_PATH
    global MODULE_ORDER, WINDOW_DURATION
    THREAD_ACTIVE = is_plot_live
    REFRESHING_TIME = refreshing_time
    PLOT_CONFIG_PATH = plot_config_path
    LOG_FILE_PATH = log_file_path
    PLOT_SAVING_PATH = plot_saving_path
    MODULE_ORDER = module_order
    WINDOW_DURATION = window_duration


if __name__ == "__main__":
    m_order = [
        "Microphone",
        "VAD",
        "ASR",
        "LLM",
        "TTS",
        "Speaker",
    ]
    plot_once("configs/plot_config_simple.json", module_order=m_order)
