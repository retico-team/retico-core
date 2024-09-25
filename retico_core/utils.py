import torch


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
