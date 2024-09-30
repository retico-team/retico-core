import csv
import datetime
import os
import json
from pathlib import Path
import re
import traceback
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
import structlog
import pandas as pd


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
            file_logger.info("test file logger")

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


def plotting_run(logfile_path=None, plot_saving_path=None):
    if logfile_path is None or plot_saving_path is None:
        subfolders = [f.path for f in os.scandir("logs/") if f.is_dir()]
        max_run = max(subfolders, key=extract_number)
        logfile_path = max_run + "/logs.log"
        plot_saving_path = "run_plots/" + max_run.split("/")[-1]
    x_axis = []
    y_axis = []
    y_axis_append_UM = []
    x_axis_append_UM = []
    x_axis_process_update = []
    y_axis_process_update = []
    nb_pb_line = 0
    with open(logfile_path, encoding="utf-8") as f:
        lines = f.readlines()

        for i, l in enumerate(lines):
            try:
                log = json.loads(l)
                date = datetime.datetime.fromisoformat(log["timestamp"])
                date_plt = mdates.date2num(date)
                module_name = " ".join(log["module"].split()[:1])
                if log["event"] == "create_iu":
                    x_axis.append(date_plt)
                    y_axis.append(module_name)
                elif log["event"] == "append UM":
                    x_axis_append_UM.append(date_plt)
                    y_axis_append_UM.append(module_name)
                elif log["event"] == "process_update":
                    x_axis_process_update.append(date_plt)
                    y_axis_process_update.append(module_name)
            except Exception:
                nb_pb_line += 1

    print("nb_pb_line = ", nb_pb_line)

    _, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_axis, y_axis, "+", color="b", label="create_iu", markersize=7)
    ax.plot(
        x_axis_append_UM,
        y_axis_append_UM,
        "^",
        color="c",
        label="append UM",
        markersize=3,
    )
    ax.plot(
        x_axis_process_update,
        y_axis_process_update,
        "o",
        color="darkorange",
        label="process_update",
        markersize=1,
    )

    ax.grid(True)
    ax.legend()
    plt.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S.%f"))
    plt.xticks(fontsize=7)

    # saving the plot
    if not os.path.isdir(plot_saving_path):
        os.makedirs(plot_saving_path)
    plot_filename = plot_saving_path + "/plot_IU_exchange.png"
    plt.savefig(plot_filename, dpi=200, bbox_inches="tight")

    # showing the plot
    # plt.show()


def plotting_run_2(logfile_path=None, plot_saving_path=None):
    if logfile_path is None or plot_saving_path is None:
        subfolders = [f.path for f in os.scandir("logs/") if f.is_dir()]
        max_run = max(subfolders, key=extract_number)
        logfile_path = max_run + "/logs.log"
        plot_saving_path = "run_plots/" + max_run.split("/")[-1]
    x_axis = []
    y_axis = []
    y_axis_append_UM = []
    x_axis_append_UM = []
    x_axis_process_update = []
    y_axis_process_update = []
    x_axis_vad = []
    y_axis_vad = []
    x_axis_sil = []
    y_axis_sil = []
    x_axis_agentEOT = []
    y_axis_agentEOT = []
    x_axis_int = []
    y_axis_int = []
    x_axis_spk = []
    y_axis_spk = []
    nb_pb_line = 0
    with open(logfile_path, encoding="utf-8") as f:
        lines = f.readlines()

        for i, l in enumerate(lines):
            pb_line = i, l
            try:
                log = json.loads(l)
                date = datetime.datetime.fromisoformat(log["timestamp"])
                date_plt = mdates.date2num(date)
                module_name = " ".join(log["module"].split()[:1])
                if log["event"] == "create_iu":
                    x_axis.append(date_plt)
                    y_axis.append(module_name)
                elif log["event"] == "append UM":
                    x_axis_append_UM.append(date_plt)
                    y_axis_append_UM.append(module_name)
                elif log["event"] == "process_update":
                    x_axis_process_update.append(date_plt)
                    y_axis_process_update.append(module_name)
                elif log["module"] == "VADTurn Module":
                    x_axis_vad.append(date_plt)
                    y_axis_vad.append(module_name)
                elif log["event"] == "output_silence":
                    x_axis_sil.append(date_plt)
                    y_axis_sil.append(module_name)
                elif log["event"] == "agent_EOT":
                    x_axis_agentEOT.append(date_plt)
                    y_axis_agentEOT.append(module_name)
                elif log["event"] == "interruption":
                    x_axis_int.append(date_plt)
                    y_axis_int.append(module_name)
                elif log["event"] == "output_audio":
                    x_axis_spk.append(date_plt)
                    y_axis_spk.append(module_name)
            except Exception:
                nb_pb_line += 1

    print("nb_pb_line = ", nb_pb_line)

    _, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_axis, y_axis, "|", color="mediumblue", label="create_iu", markersize=12)
    ax.plot(
        x_axis_append_UM,
        y_axis_append_UM,
        "|",
        color="deepskyblue",
        label="append UM",
        markersize=8,
    )
    ax.plot(
        x_axis_process_update,
        y_axis_process_update,
        "|",
        color="royalblue",
        # color="dodgerblue",
        label="process_update",
        markersize=4,
    )
    ax.plot(
        x_axis_vad,
        y_axis_vad,
        "|",
        color="black",
        label="VAD",
        markersize=16,
    )
    ax.plot(
        x_axis_sil,
        y_axis_sil,
        marker=3,
        color="gray",
        label="silence_outputted",
        markersize=7,
    )
    ax.plot(
        x_axis_agentEOT,
        y_axis_agentEOT,
        "|",
        color="r",
        label="agent_EOT",
        markersize=15,
    )
    ax.plot(
        x_axis_int,
        y_axis_int,
        "x",
        color="r",
        label="interruption",
        markersize=10,
    )
    ax.plot(
        x_axis_spk,
        y_axis_spk,
        "+",
        color="g",
        label="first_audio",
        markersize=7,
    )

    ax.grid(True)
    ax.legend(fontsize="7", loc="center left")
    plt.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S.%f"))
    plt.xticks(fontsize=7)

    # saving the plot
    if not os.path.isdir(plot_saving_path):
        os.makedirs(plot_saving_path)
    plot_filename = plot_saving_path + "/plot_IU_exchange.png"
    plt.savefig(plot_filename, dpi=200, bbox_inches="tight")

    # showing the plot
    # plt.show()


def get_latency(logfile_path=None):
    if logfile_path is None:
        subfolders = [f.path for f in os.scandir("logs/") if f.is_dir()]
        max_run = max(subfolders, key=extract_number)
        logfile_path = max_run + "/logs.log"
    nb_pb_line = 0

    # get all append UM messages per module
    with open(logfile_path, encoding="utf-8") as f:
        lines = f.readlines()
        messages_per_module = {}
        for i, l in enumerate(lines):
            try:
                log = json.loads(l)
                if log["event"] == "append UM":
                    date = datetime.datetime.fromisoformat(log["timestamp"])
                    if log["module"] not in messages_per_module:
                        messages_per_module[log["module"]] = [date]
                    else:
                        messages_per_module[log["module"]].append(date)
            except Exception:
                nb_pb_line += 1

    # filter to find the first and last append UM of each turn
    first_and_last_per_module = {}
    for module, dates in messages_per_module.items():
        first_and_last_per_module[module] = [[], []]
        # last append UM per turn per module
        for i, message_date in enumerate(dates):
            if i != len(dates) - 1:
                # print(f"dates : {message_date} , {dates[i + 1]}")
                # print(f"dates sub : {dates[i + 1] - message_date}")
                # print(f"dates sub : {(dates[i + 1] - message_date).total_seconds()}")
                if (dates[i + 1] - message_date).total_seconds() > 1.2:
                    first_and_last_per_module[module][1].append(message_date)
            else:
                first_and_last_per_module[module][1].append(message_date)
        # first append UM per turn per module
        for i, message_date in enumerate(dates):
            if i != 0:
                # print(f"dates : {message_date} , {dates[i - 1]}")
                # print(f"dates sub : {message_date - dates[i - 1]}")
                # print(f"dates sub : {(message_date - dates[i - 1]).total_seconds()}")
                if (message_date - dates[i - 1]).total_seconds() > 1.2:
                    first_and_last_per_module[module][0].append(message_date)
            else:
                first_and_last_per_module[module][0].append(message_date)

    print(
        f"first_and_last_per_module = {[(len(v[0]), len(v[1])) for k,v in first_and_last_per_module.items()]}",
    )
    # print("first_and_last_per_module = ", first_and_last_per_module)
    modules = [(key, value) for key, value in first_and_last_per_module.items()]
    last_module = modules[0][0]
    modules = modules[1:]
    for module, dates in modules:
        firsts = dates[0]
        for i, fdate in enumerate(firsts):
            # get last date from previous module in pipeline
            previous_dates_from_previous_module = [
                date
                for date in first_and_last_per_module[last_module][0]
                if date < fdate
            ]

            latency = (fdate - max(previous_dates_from_previous_module)).total_seconds()
            print(f"latency {module}, {latency}")

        last_module = module


def test_pandas(logfile_path=None):
    if logfile_path is None:
        subfolders = [f.path for f in os.scandir("logs/") if f.is_dir()]
        max_run = max(subfolders, key=extract_number)
        logfile_path = max_run + "/logs.log"
    with open(logfile_path, encoding="utf-8") as f:
        lines = f.readlines()
        lines_json = []
        for _, l in enumerate(lines):
            try:
                lines_json.append(json.loads(l))
            except Exception:
                pass
    df = pd.DataFrame(lines_json)
    print(df)
    print(df[df["module"] == "Microphone Module"])


def pandas_latency(logfile_path=None):
    if logfile_path is None:
        subfolders = [f.path for f in os.scandir("logs/") if f.is_dir()]
        max_run = max(subfolders, key=extract_number)
        logfile_path = max_run + "/logs.log"
    with open(logfile_path, encoding="utf-8") as f:
        lines = f.readlines()
        lines_json = []
        for i, l in enumerate(lines):
            try:
                line = json.loads(l)
                line["timestamp"] = datetime.datetime.fromisoformat(line["timestamp"])
                lines_json.append(line)
            except Exception:
                pass

    df = pd.DataFrame(lines_json)

    # GET ALL TIMESTAMP FOR SPEAKERS APPEND MSG (EOT timestamps)
    spk_msgs = df[df["module"] == "Speaker Interruption Module"]
    append_spk_msgs = spk_msgs[spk_msgs["event"] == "append UM"]
    append_spk_msgs = append_spk_msgs.drop_duplicates(subset=["timestamp"])
    print(append_spk_msgs)
    EOT_timestamps = append_spk_msgs["timestamp"]
    print(EOT_timestamps)

    # GET ALL TIMESTAMP FOR VAD APPEND MSG (BOT timestamps)
    vad_msgs = df[df["module"] == "VADTurn Module"]
    append_vad_msgs = vad_msgs[vad_msgs["event"] == "append UM"]
    BOT_append_vad_msgs = append_vad_msgs[
        append_vad_msgs["timestamp"].diff().gt(pd.Timedelta("0.1 s"))
    ]
    first_BOT = append_vad_msgs.iloc[[0]]
    BOTs = pd.concat([first_BOT, BOT_append_vad_msgs])
    print(BOTs)
    BOT_timestamps = BOTs["timestamp"]
    print(BOT_timestamps)

    # trying to have turns as tuple (BOT_timestamps, EOT_timestapms) but not easy iwith pandas.
    # BOT_timestamps_f = BOT_timestamps.to_frame()
    # EOT_timestamps_f = EOT_timestamps.to_frame()
    # print(BOT_timestamps_f)
    # print(EOT_timestamps_f)
    # print(EOT_timestamps_f.columns.intersection(EOT_timestamps_f.columns))
    # Turns_timestamps = BOT_timestamps_f.join(
    #     EOT_timestamps, lsuffix="_BOT", rsuffix="_EOT"
    # )
    # print(Turns_timestamps)

    # check that BOT and EOT have same length
    assert BOT_timestamps.size == EOT_timestamps.size

    # get each module's first append UM of each turn
    append_msgs = df[df["event"] == "append UM"]
    for turn_id in range(BOT_timestamps.size):
        print("Turn ", turn_id)
        bot = BOT_timestamps.iloc[turn_id]
        eot = EOT_timestamps.iloc[turn_id]
        # print(BOT)
        # print(EOT)
        # print(append_msgs["timestamp"])
        append_msgs_turn_i = append_msgs[
            (append_msgs["timestamp"] >= bot) & (append_msgs["timestamp"] <= eot)
        ]
        # print(append_msgs_turn_i["timestamp"])

        #
        print("first and last append Um of each module")
        turn_i_per_module = append_msgs_turn_i.groupby("module")
        turn_i_per_module_first = turn_i_per_module["timestamp"].min()
        turn_i_per_module_last = turn_i_per_module["timestamp"].max()
        # print(turn_i_per_module)
        print(turn_i_per_module_first)
        print(turn_i_per_module_last)

        # TODO: calculate the latency between each module's first append UM message
        pipeline = [
            "Microphone Module",
            "VADTurn Module",
            "WhisperASR Module",
            "LlamaCppMemoryIncremental Module",
            "CoquiTTS Module",
            "Speaker Interruption Module",
        ]
        for i, module in enumerate(pipeline[1:]):
            piepline_diff = (
                turn_i_per_module_first[module]
                - turn_i_per_module_first[pipeline[i - 1]]
            )
            print(piepline_diff)


def pandas_latency_2(logfile_path=None):
    if logfile_path is None:
        subfolders = [f.path for f in os.scandir("logs/") if f.is_dir()]
        max_run = max(subfolders, key=extract_number)
        logfile_path = max_run + "/logs.log"
    with open(logfile_path, encoding="utf-8") as f:
        lines = f.readlines()
        lines_json = []
        for i, l in enumerate(lines):
            try:
                line = json.loads(l)
                line["timestamp"] = datetime.datetime.fromisoformat(line["timestamp"])
                lines_json.append(line)
            except Exception:
                pass

    df = pd.DataFrame(lines_json)

    # Get user BOTs & EOTs
    user_BOTs = df[df["event"] == "user_BOT"]  # 12, 2, div/6
    user_EOTs = df[df["event"] == "user_EOT"]  # 30, 5, div/6
    agent_BOTs = user_EOTs  # 30, 5, div/6
    agent_EOTs = df[df["event"] == "agent_EOT"]  # 12, 2, div/6
    interruptions = df[df["event"] == "interruption"]  # 36, 6, div/6
    user_BARGE_IN = interruptions[
        interruptions["module"] == "VADTurn Module"
    ]  # 18, 3, div/6
    user_TOT_BOTs = pd.concat([user_BOTs, user_BARGE_IN])  # 30, 5, div/6
    agent_TOT_EOTs = pd.concat([agent_EOTs, user_BARGE_IN])  # 30, 5, div/6
    user_TOT_BOTs = user_TOT_BOTs.sort_values(by=["timestamp"])
    agent_TOT_EOTs = agent_TOT_EOTs.sort_values(by=["timestamp"])
    user_BOTs = user_BOTs.drop_duplicates()
    user_EOTs = user_EOTs.drop_duplicates()
    agent_BOTs = agent_BOTs.drop_duplicates()
    agent_EOTs = agent_EOTs.drop_duplicates()
    interruptions = interruptions.drop_duplicates()
    user_BARGE_IN = user_BARGE_IN.drop_duplicates()
    user_TOT_BOTs = user_TOT_BOTs.drop_duplicates()
    agent_TOT_EOTs = agent_TOT_EOTs.drop_duplicates()
    speaker_outputs = df[df["event"] == "output_audio"].drop_duplicates()

    append_msgs = df[df["event"] == "append UM"]
    pipeline = [
        "Microphone Module",
        "VADTurn Module",
        "WhisperASR Module",
        "LlamaCppMemoryIncremental Module",
        "CoquiTTS Module",
        "Speaker Interruption Module",
    ]
    for turn_id in range(user_TOT_BOTs["timestamp"].size):

        try:
            #######
            # Calculate the user and agent BOT and EOT and the timestamp of the first agent audio output
            ######
            user_BOT = user_TOT_BOTs.iloc[turn_id]["timestamp"]
            if turn_id < user_TOT_BOTs["timestamp"].size - 1:
                user_EOT = user_EOTs[
                    (user_EOTs["timestamp"] >= user_BOT)
                    & (
                        user_EOTs["timestamp"]
                        <= user_TOT_BOTs.iloc[turn_id + 1]["timestamp"]
                    )
                ]
                user_EOT = max(user_EOT["timestamp"])
                agent_EOT = agent_TOT_EOTs[
                    (agent_TOT_EOTs["timestamp"] >= user_BOT)
                    & (
                        agent_TOT_EOTs["timestamp"]
                        <= user_TOT_BOTs.iloc[turn_id + 1]["timestamp"]
                    )
                ]
                agent_EOT = max(agent_EOT["timestamp"])
                speaker_first_output = speaker_outputs[
                    (speaker_outputs["timestamp"] >= user_BOT)
                    & (
                        speaker_outputs["timestamp"]
                        <= user_TOT_BOTs.iloc[turn_id + 1]["timestamp"]
                    )
                ]
                speaker_first_output = min(speaker_first_output["timestamp"])
            else:
                speaker_first_output = speaker_outputs[
                    speaker_outputs["timestamp"] >= user_BOT
                ]
                speaker_first_output = min(speaker_first_output["timestamp"])
                user_EOT = max(user_EOTs["timestamp"])
                agent_EOT = max(agent_TOT_EOTs["timestamp"])

            print(f"\n\nTURN {turn_id} : ")
            print(f"{'user BOT :'.ljust(25, ' ')} {user_BOT}")
            print(f"{'user EOT / agent BOT :'.ljust(25, ' ')} {user_EOT}")
            print(f"{'agent first output :'.ljust(25, ' ')} {speaker_first_output}")
            print(f"{'agent EOT :'.ljust(25, ' ')} {agent_EOT}\n")

            #######
            # Print the timestamp of the first data output for each module
            #######
            if turn_id < user_TOT_BOTs["timestamp"].size - 1:
                append_msgs_turn = append_msgs[
                    (append_msgs["timestamp"] >= user_EOT)
                    & (append_msgs["timestamp"] <= agent_EOT)
                ]
            else:
                append_msgs_turn = append_msgs[append_msgs["timestamp"] >= user_EOT]
            append_msgs_turn_module = append_msgs_turn.groupby("module")
            append_msgs_turn_module_BOT = append_msgs_turn_module["timestamp"].min()
            append_msgs_turn_module_BOT = (
                append_msgs_turn_module_BOT.to_frame().sort_values(by="timestamp")
            )

            # Changing the values for Microphone Module and Speaker Module because they are logged differently
            append_msgs_turn_module_BOT.loc[
                "Speaker Interruption Module", "timestamp"
            ] = speaker_first_output
            append_msgs_turn_module_BOT.loc["Microphone Module", "timestamp"] = user_EOT
            print(f"Timestamp first data append : \n{append_msgs_turn_module_BOT}\n")

            append_msgs_turn_module_BOT = append_msgs_turn_module_BOT

            #######
            # Calculate the EXEC TIME of each module at each turn of the dialogue
            # (EXEC TIME = the time for each module between receiving the first data and outputting the first data)
            # the sum of the EXEC TIME of all modules = the answering latency of the system
            ######
            total_exec_time = pd.Timedelta(0)
            start_id = 1
            for i, module in enumerate(pipeline[start_id:]):
                pipeline_diff = (
                    append_msgs_turn_module_BOT.loc[module, "timestamp"]
                    - append_msgs_turn_module_BOT.loc[
                        pipeline[i + start_id - 1], "timestamp"
                    ]
                )
                total_exec_time += pipeline_diff
                print(f"EXEC TIME   {module.ljust(40, ' ')} {pipeline_diff}")

            print(f"\nTOTAL EXEC TIME   {str(total_exec_time).ljust(40, ' ')}")
            print(
                f"TOTAL EXEC TIME   {str(speaker_first_output-user_EOT).ljust(40, ' ')}"
            )

        except ValueError:
            print(
                "Turns where the user interrupted the agent before the agent had time to speak are not interesting for now"
            )


if __name__ == "__main__":

    # test_structlog()
    # test_plot()
    # logfile_path = "logs/run_1/logs.log"
    # plot_saving_path = "run_plots/run_1"
    # plotting_run(logfile_path, plot_saving_path)

    # plotting_run()
    plotting_run_2()

    # get_latency()

    # pandas_latency()
    # pandas_latency_2()
