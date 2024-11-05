import torch


# DEVICE DEF
def device_definition(device):
    """Checks if the desired `device` is available, and if not, returns a default device (cpu).

    Args:
        device (str): the name of the desired device to use.

    Returns:
        str: the device that will be used.
    """
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
                "device defined for instantiation is cuda but cuda is not available. Check your\
                cuda installation if you want the module to run on GPU. The module will run on\
                CPU instead."
            )
            # Raise Exception("device defined for instantiation is cuda but cuda is not available.
            # check you cuda installation or change device to "cpu")
            final_device = "cpu"
    elif device == "cpu":
        if cuda_available:
            print(
                "cuda is available, you can run the module on GPU by changing the device parameter\
                to cuda."
            )
        final_device = "cpu"
    return final_device
