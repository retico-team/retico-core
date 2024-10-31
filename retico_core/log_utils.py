import datetime
import os
import json
from pathlib import Path
import re
import threading
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
import numpy as np
import structlog


def filter_has_key(_, __, event_dict, key):
    if event_dict.get(key):
        raise structlog.DropEvent
    return event_dict


def filter_does_not_have_key(_, __, event_dict, key):
    if not event_dict.get(key):
        raise structlog.DropEvent
    return event_dict


def filter_value_in_list(_, __, event_dict, key, values):
    if event_dict.get(key):
        if event_dict.get(key) in values:
            raise structlog.DropEvent
    return event_dict


def filter_value_not_in_list(_, __, event_dict, key, values):
    if event_dict.get(key):
        if event_dict.get(key) not in values:
            raise structlog.DropEvent
    return event_dict


def filter_conditions(_, __, event_dict, conditions):
    """
    filter function for the structlog terminal logger.
    This function deletes logs that doesn't match the complete list of conditions.
    The conditions are a tuple (key, values), to verify the condition, the log has to have the key, and the corresponding key has to be present in the condition's values list.

    Example :
    conditions = [("module":["Microphone Module"]), ("event":["create_iu", "append UM"])]
    Meaning of the conditions : KEEP IF module is "Microphone Module" AND event is in ["create_iu", "append UM"]
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
    This function deletes logs that matchs none of the different cases, each case is a list of conditions that have to be completely validated.
    The conditions are a tuple (key, values), to verify the condition, the log has to have the key, and the corresponding key has to be present in the condition's values list.

    Example :
    cases = [[("module":["Micro"]), ("event":["create_iu", "append UM"])], [("module":["Speaker"]), ("event":["create_iu"])]]
    Meaning of the conditions : KEEP IF ((module is "Microphone Module" AND event is in ["create_iu", "append UM"])  OR (module is "Speaker Module" AND event is "append UM"))
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


def filter_all(_, __, event_dict):
    """function that filters all log message that has a `module` key."""
    if event_dict.get("module"):
        raise structlog.DropEvent
    return event_dict


def filter_all_but_warnings_and_errors(_, __, event_dict):
    """function that filters all log message that is not a warning or an error."""
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


def log_exception(module, exception):
    """function that enable modules to log the encountered exceptions to both logger (terminal and file) in a unified way (and factorize code).

    Args:
        module (object): the module that encountered the exception.
        exception (Exception): the encountered exception.
    """
    module.terminal_logger.exception(
        "The module encountered the following exception while running :"
    )
    # could maybe introduce errors while parsing the json logs, because of the " chars in the exception tracebacks
    module.file_logger.exception(
        "The module encountered the following exception while running :",
    )
    # module.file_logger.exception(
    #     "The module encountered the following exception while running :",
    #     tarcebacks=[
    #         tb.replace('"', "'") for tb in traceback.format_tb(exception.__traceback__)
    #     ],
    # )


def create_new_log_folder(log_folder):
    """Function that creates a new folder to store the current run's log file. Find the last run's number and creates a new log folder with an increment of 1.

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


# LOG_FILTERS = []
# LOG_FILTERS = [filter_all]
LOG_FILTERS = [filter_all_but_warnings_and_errors]


class TerminalLogger(structlog.BoundLogger):
    """Dectorator / Singleton class of structlog.BoundLogger, that is used to configure / initialize once the terminal logger for the whole system."""

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

            # log an info to cache the logger, using the config's cache_logger_on_first_use parameter
            terminal_logger.info("init terminal logger")

            # set the singleton instance
            cls.instance = terminal_logger
        return cls.instance


class FileLogger(structlog.BoundLogger):
    """Dectorator / Singleton class of structlog.BoundLogger, that is used to configure / initialize once the file logger for the whole system."""

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

            # log an info to cache the logger, using the config's cache_logger_on_first_use parameter
            file_logger.info("init file logger")

            # set the singleton instance
            cls.instance = file_logger
        return cls.instance


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


def extract_number(f):
    s = re.findall("\d+$", f)
    return (int(s[0]) if s else -1, f)


def log_event(
    log_data,
    events_to_plot,
    events_dict,
    event,
    event_config,
    module,
    date,
    module_name,
):
    """function used to add to log_data the log events and their timestamps if they match the config_file conditions.

    Args:
        log_data (dict): the data_structure where the logs that will be plotted are stored.
        events_to_plot (dict): the different log events described in the plot_config that will be retrieved from log_file.
        events_dict (_type_): _description_
        event (str): the log's event name.
        event_config (_type_): _description_
        module (str): the name of the module source of the log.
        date (date): the log's timestamp.
        module_name (str): A shorter version of the module's name (for the plot).

    Returns:
        _type_: _description_
    """
    boolean = events_dict is not None and event_config in events_dict
    if boolean:
        if event not in log_data["events"]:
            log_data["events"][event] = {"x_axis": [], "y_axis": []}
            if "plot_settings" in events_to_plot[module]["events"][event_config]:
                log_data["events"][event]["plot_settings"] = events_to_plot[module][
                    "events"
                ][event_config]["plot_settings"]
        log_data["events"][event]["x_axis"].append(date)
        log_data["events"][event]["y_axis"].append(module_name)
    return log_data, boolean


THREAD_ACTIVE = False
REFRESHING_TIME = 1
LOG_FILE_PATH = None
PLOT_SAVING_PATH = None
PLOT_CONFIG = None
MODULE_ORDER = None


def plot(
    events_to_plot,
    e_every_m,
    log_file_path,
    plot_saving_path,
    module_order=None,
    log_data={"events": {}},
    pointer=0,
    window_duration=None,
):
    """function used to create a plot for a system run from the corresponding log file. Can be used to plot live or after the execution.

    Args:
        events_to_plot (dict): the different log events described in the plot_config that will be retrieved from log_file.
        e_every_m (dict): the log events that will be retrieved for every module.
        log_file_path (str, optional): path to the folder corresponding to the desired run to plot. Defaults to None.
        plot_saving_path (str, optional): path to the folder where the plot will be saved. Defaults to None.
        terminal_logger (TerminalLogger, optional): The structlog logger that outputs log through terminal. Defaults to TerminalLogger().
        module_order (list[str], optional): Custom order of the modules in the final plot (first in the list is the lowest on the plot). Defaults to None
        log_data (dict, optional): If called from the plot_live function, used to store current log_file logs and only retrieve new logs at each loop of live plotting. Defaults to {"events": {}}.
        pointer (int, optional): If called from the plot_live function, used to only retrieve new logs at each loop of live plotting (logs whose line if greater than pointer). Defaults to 0.
        plot_config (str): the path to the plot configuration file.


    Returns:
        _type_: _description_
    """
    nb_pb_line = 0
    terminal_logger = TerminalLogger()

    with open(log_file_path, encoding="utf-8") as f:
        lines = f.readlines()
        new_pointer = len(lines)
        lines = lines[pointer:]
        pointer = new_pointer

    # Retrieve logs : store data from log_file to log_data if it is registered in plot_config (events_to_plot)
    for l in lines:
        try:
            log = json.loads(l)

            m_name = log["module"] if "module" in log else None
            e_name = log["event"] if "event" in log else None

            if m_name is None:
                continue

            date = datetime.datetime.fromisoformat(log["timestamp"])
            date_plt = mdates.date2num(date)
            module_name = " ".join(m_name.split()[:1])

            # log from event, from most specific to least specific
            e_that_m = None
            if m_name in events_to_plot and "events" in events_to_plot[m_name]:
                e_that_m = events_to_plot[m_name]["events"]

            # if we specified in the config to log specific event from specific module
            log_data, b = log_event(
                log_data,
                events_to_plot,
                e_that_m,
                module_name + "_" + e_name,
                e_name,
                m_name,
                date_plt,
                module_name,
            )
            if b:
                continue

            # if we specified in the config to log specific event from any module
            log_data, b = log_event(
                log_data,
                events_to_plot,
                e_every_m,
                e_name,
                e_name,
                "any_module",
                date_plt,
                module_name,
            )
            if b:
                continue

            # if we specified in the config to log any event from specific module
            log_data, b = log_event(
                log_data,
                events_to_plot,
                e_that_m,
                "other_events_" + module_name,
                "any_event",
                m_name,
                date_plt,
                module_name,
            )
            if b:
                continue

            # if we specified in the config to log any event from any module
            log_data, b = log_event(
                log_data,
                events_to_plot,
                e_every_m,
                "other_events",
                "any_event",
                "any_module",
                date_plt,
                module_name,
            )

        except Exception:
            nb_pb_line += 1

    # put all events data in the plot
    _, ax = plt.subplots(figsize=(10, 5))
    try:
        for e_name, e_dict in log_data["events"].items():
            x = e_dict["x_axis"]
            y = e_dict["y_axis"]
            # re-order if the module_order parameter is set
            if module_order is not None:
                x_np = np.array(e_dict["x_axis"])
                y_np = np.array(e_dict["y_axis"])
                reordered_indices = np.concatenate(
                    [np.where(y_np == o)[0] for o in module_order]
                )
                x = x_np[reordered_indices]
                y = y_np[reordered_indices]
            if "plot_settings" in e_dict:
                ax.plot(
                    x,
                    y,
                    e_dict["plot_settings"]["marker"],
                    color=e_dict["plot_settings"]["marker_color"],
                    label=e_name,
                    markersize=e_dict["plot_settings"]["marker_size"],
                )
            else:
                ax.plot(
                    e_dict["x_axis"],
                    e_dict["y_axis"],
                    "|",
                    color="g",
                    label=e_name,
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
    ax.xaxis.set_major_locator(mdates.SecondLocator(bysecond=(range(0, 61, 5))))
    ax.xaxis.set_minor_locator(mdates.SecondLocator(bysecond=(range(0, 61, 1))))
    plot_filename = plot_saving_path + "/plot_IU_exchange.png"
    plt.savefig(plot_filename, dpi=200, bbox_inches="tight")
    plt.close()

    return log_data, pointer


def plot_live(module_order=None):
    """a looping function that creates a plot from the current run's log_file each `REFRESHING_TIME` seconds (if it's the biggest number in your `logs` folder)"""
    global LOG_FILE_PATH, PLOT_SAVING_PATH

    if LOG_FILE_PATH is None or PLOT_SAVING_PATH is None:
        subfolders = [f.path for f in os.scandir("logs/") if f.is_dir()]
        max_run = max(subfolders, key=extract_number)
        LOG_FILE_PATH = max_run + "/logs.log"
        PLOT_SAVING_PATH = "run_plots/" + max_run.split("/")[-1]
        if not os.path.isdir(PLOT_SAVING_PATH):
            os.makedirs(PLOT_SAVING_PATH)

    if PLOT_CONFIG is None:
        raise NotImplementedError
    else:
        with open(PLOT_CONFIG, encoding="utf-8") as f:
            events_to_plot = json.load(f)

    e_every_m = None
    if "any_module" in events_to_plot and "events" in events_to_plot["any_module"]:
        e_every_m = events_to_plot["any_module"]["events"]

    log_data = {"events": {}}
    pointer = 0

    while THREAD_ACTIVE:
        time.sleep(REFRESHING_TIME)
        log_data, pointer = plot(
            events_to_plot=events_to_plot,
            e_every_m=e_every_m,
            log_file_path=LOG_FILE_PATH,
            plot_saving_path=PLOT_SAVING_PATH,
            module_order=module_order,
            log_data=log_data,
            pointer=pointer,
            window_duration=WINDOW,
        )


def plot_once(
    plot_config, log_file_path=None, plot_saving_path=None, module_order=None
):
    """Create a plot for a previous system run from the corresponding log file.

    Args:
        plot_config (str): the path to the plot configuration file.
        log_file_path (str, optional): path to the folder corresponding to the desired run to plot. Defaults to None.
        plot_saving_path (str, optional): path to the folder where the plot will be saved. Defaults to None.
        module_order (list[str], optional): Custom order of the modules in the final plot (first in the list is the lowest on the plot). Defaults to None.
    """
    if log_file_path is None or plot_saving_path is None:
        subfolders = [f.path for f in os.scandir("logs/") if f.is_dir()]
        max_run = max(subfolders, key=extract_number)
        log_file_path = max_run + "/logs.log"
        plot_saving_path = "run_plots/" + max_run.split("/")[-1]
        if not os.path.isdir(plot_saving_path):
            os.makedirs(plot_saving_path)
    with open(plot_config, encoding="utf-8") as f:
        events_to_plot = json.load(f)
    e_every_m = None
    if "any_module" in events_to_plot and "events" in events_to_plot["any_module"]:
        e_every_m = events_to_plot["any_module"]["events"]
    plot(
        log_file_path=log_file_path,
        plot_saving_path=plot_saving_path,
        events_to_plot=events_to_plot,
        e_every_m=e_every_m,
        module_order=module_order,
    )


def setup_plot_live():
    """a function that initializes and starts a thread from the looping function `plot_live`, to create a plot from the log_file in real time passively."""
    threading.Thread(target=plot_live).start()


def stop_plot_live():
    """a function that stops plot_live's thread. Supposed to be called at the end of the run by the `network`"""
    global THREAD_ACTIVE
    THREAD_ACTIVE = False


def configurate_plot(
    is_plot_live=False,
    refreshing_time=1,
    logfile_path=None,
    plot_saving_path=None,
    plot_config=None,
    module_order=None,
    window_dur=None,
):
    """A function that configures the global parameters `THREAD_ACTIVE` and `REFRESHING_TIME`.
    These two parameters will be used by the `plot_live` function to create a plot from the current run's log_file in real time.

    Args:
        plot_live (bool, optional): If set to True, a plot from the current run's log_file will be created in real time. If set to False, it will only be created at the end of the run. Defaults to False.
        refreshing_time (int, optional): The refreshing time (in seconds) between two creation of plots when `plot_live` is set to `True`. Defaults to 1.
    """
    global THREAD_ACTIVE, REFRESHING_TIME, LOG_FILE_PATH, PLOT_SAVING_PATH, PLOT_CONFIG, MODULE_ORDER, WINDOW
    THREAD_ACTIVE = is_plot_live
    REFRESHING_TIME = refreshing_time
    PLOT_CONFIG = plot_config
    LOG_FILE_PATH = logfile_path
    PLOT_SAVING_PATH = plot_saving_path
    MODULE_ORDER = module_order
    WINDOW = window_dur


if __name__ == "__main__":
    m_order = [
        "Microphone",
        "VAD",
        "DialogueManager",
        "WhisperASR",
        "LLM",
        "TTS",
        "Speaker",
    ]
    plot_once("plot_config_3.json", module_order=m_order)
