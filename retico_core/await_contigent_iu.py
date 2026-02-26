import queue
import threading
import time
from collections import deque, namedtuple
from enum import Enum

import retico_core
from retico_core import abstract

RequiredIU = namedtuple('RequiredIU', ['iu_type', 'count'])
IUtoForward = namedtuple('IUtoForward', ['iu_type', 'creator_name'])

class AwaitType(Enum):
    # Return the first instance of each awaited IU
    # e.g. awaiting ('mic',1) and ('yolo',1) and queue has IU types ['mic', 'mic', 'yolo'] we will return IUs at index [0,2]
    FIRST = 'first'
    # Return the most recent instance of each awaited IU up until all required IUs are captured
    # e.g. awaiting ('mic',1) and ('yolo',1) and queue has IU types ['mic', 'mic', 'yolo'] we will return IUs at index [1,2]
    LATEST = 'latest'

class AwaitContingentIUsModule(abstract.AbstractModule):
    @staticmethod
    def name():
        return "Await Contingent IUs"
    @staticmethod
    def description():
        return "Wait for all required IUs to arrive before proceeding"

    def input_ius(self,):
        return [iu.iu_type for iu in self.required_ius]

    @staticmethod
    def output_iu():
        # output IU does not have any impact because this module does not create any IUs, just passes existing ones on.
        pass

    def __init__(self, required_ius:[RequiredIU], type_of_iu_to_forward, creator_of_iu_to_forward, await_type=AwaitType.LATEST, **kwargs):

        super().__init__(**kwargs)
        self.queue = deque()
        self.required_ius = required_ius
        self.await_type = await_type

        # If there are two of the same iu type being awaited, the type is not enough to differentiate which one needs to be passed on to the module
        # subscribed to this. Use the creator name as well.
        self.type_of_iu_to_forward = type_of_iu_to_forward # Will be passing this IU on
        self.creator_name_of_iu_to_forward = creator_of_iu_to_forward

        self.required_iu_queues = {}
        for key, count in self.required_ius:
            # Blocks additional put() actions after maxsize is met
            # Could use a deque for when await_type is LATEST, but the implementation is simpler if we aren't having to deal with different
            # queue methods
            self.required_iu_queues[key] = queue.Queue(maxsize=count)

    def process_update(self, update_message):
        for iu, ut in update_message:
            self.queue.append(iu)

    def _extractor_thread(self):
         while self._extractor_thread_active:
            time.sleep(0.01)
            if len(self.queue) == 0:
                continue
            # Iterate over queue and pop the items off, make sure they align with the expected IUs.
            while self.queue:
                current_iu = self.queue.popleft()
                required_iu_queue = self.required_iu_queues.get(type(current_iu))
                if required_iu_queue is None:
                    print(f"Await Contingent IU received unexpected IU type {type(current_iu)}")
                else:
                    if required_iu_queue.full() is True:
                        if self.await_type is AwaitType.FIRST:
                            continue
                        elif self.await_type is AwaitType.LATEST:
                            required_iu_queue.get()
                            required_iu_queue.put(current_iu)
                    else:
                        required_iu_queue.put(current_iu)

                if all(iu_queue.full() for iu_queue in self.required_iu_queues.values()):
                    # All the queues are full, done awaiting and ready to continue processing
                    break

            # get iu to forward
            queue_with_iu_to_forward = self.required_iu_queues[self.type_of_iu_to_forward]
            for iu in reversed(list(queue_with_iu_to_forward.queue)): # reversed() to get the most recent iu matching the condition
                if iu.creator.name() is self.creator_name_of_iu_to_forward:
                    # Pass the IU on, this module will not show in the IU history via grounded_in or creator
                    output_iu = iu
                    break

            # clear the queues so we can begin waiting for the next set of required IUs
            for iu_queue in self.required_iu_queues.values():
                iu_queue.queue.clear()

            # With this current implementation the IU subscriber chain is interrupted because we lose the linear 'grounded_in' path from iu to iu
            # that we would have if we did not process these in parallel and instead subscribed to each module in a chronological fashion.
            # For example, I await a TextIU from GRED and an ObjectPermanenceIU from Object Permanence, but I only pass the ObjectPermanenceIU on to
            # any subscribed modules so the TextIU chain is lost.
            # NOTE: It may be helpful in the future to output a *new* IU (instead of passing an input one forward) that keeps a list of all the IUs
            # that were awaited + implement a solution using that list for navigating revokes.
            print(f"All IUs successfully awaited ({self.required_ius})")
            um = retico_core.UpdateMessage.from_iu(output_iu, retico_core.UpdateType.ADD)
            self.append(um)

    def prepare_run(self):
        self._extractor_thread_active = True
        threading.Thread(target=self._extractor_thread).start()

    def shutdown(self):
        self._extractor_thread_active = False
