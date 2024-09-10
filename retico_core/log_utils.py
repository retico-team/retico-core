import csv
import datetime
import os
import torch


# LOGS FUNCTIONS
def manage_log_folder(log_folder, file_name):
    complete_path = log_folder + "/" + file_name
    if os.path.isfile(complete_path):  # if file path already exists
        return create_new_log_folder(log_folder) + "/" + file_name
    else:
        print("log_folder = ", log_folder)
        if not os.path.isdir(log_folder):
            os.makedirs(log_folder)
        return log_folder + "/" + file_name


def create_new_log_folder(log_folder):
    cpt = 0
    filename = log_folder + "_" + str(cpt)
    while os.path.isdir(filename):
        cpt += 1
        filename = log_folder + "_" + str(cpt)
    os.mkdir(filename)
    filename = filename + "/logs.log"
    return filename


def write_logs(log_file, rows):
    with open(log_file, "a", newline="") as f:
        csv_writer = csv.writer(f)
        for row in rows:
            csv_writer.writerow(row)


def merge_logs(log_folder):
    wozmic_file = log_folder + "/wozmic.csv"
    if not os.path.isfile(wozmic_file):
        return None
    asr_file = log_folder + "/asr.csv"
    llm_file = log_folder + "/llm.csv"
    tts_file = log_folder + "/tts.csv"
    speaker_file = log_folder + "/speaker.csv"
    files = [wozmic_file, asr_file, llm_file, tts_file, speaker_file]

    res_file = log_folder + "/res.csv"
    date_format = "%H:%M:%S.%f"

    with open(res_file, "w", newline="") as w:
        writer = csv.writer(w)
        writer.writerow(["Module", "Start", "Stop", "Duration"])
        first_start = None
        last_stop = None
        for fn in files:
            if os.path.isfile(fn):
                with open(fn, "r") as f:
                    l = [fn, None, None, 0]
                    for row in csv.reader(
                        f
                    ):  # TODO : is there only 1 start and 1 stop ?
                        if row[0] == "Start":
                            if l[1] is None or l[1] > row[1]:
                                l[1] = row[1]
                            if first_start is None or first_start > row[1]:
                                first_start = row[1]
                        elif row[0] == "Stop":
                            if l[2] is None or l[2] < row[1]:
                                l[2] = row[1]
                            if last_stop is None or last_stop < row[1]:
                                last_stop = row[1]
                    if l[1] is not None and l[2] is not None:
                        l[3] = datetime.datetime.strptime(
                            l[2], date_format
                        ) - datetime.datetime.strptime(l[1], date_format)
                    writer.writerow(l)

        total_duration = datetime.datetime.strptime(
            last_stop, date_format
        ) - datetime.datetime.strptime(first_start, date_format)
        writer.writerow(["Total", first_start, last_stop, total_duration])


# DEVICE DEF
def device_definition(device):
    cuda_available = torch.cuda.is_available()
    final_device = None
    if device is None:
        if cuda_available:
            final_device = "cuda"
        else:
            final_device = "cpu"
    elif device == "cuda":
        if cuda_available:
            final_device = "cuda"
        else:
            print(
                "device defined for instantiation is cuda but cuda is not available. Check you cuda installation if you want the module to run on GPU. The module will run on CPU instead."
            )
            # Raise Exception("device defined for instantiation is cuda but cuda is not available. check you cuda installation or change device to "cpu")
            final_device = "cpu"
    elif device == "cpu":
        if cuda_available:
            print(
                "cuda is available, you can run the module on GPU by changing the device parameter to cuda."
            )
        final_device = "cpu"
    return final_device
