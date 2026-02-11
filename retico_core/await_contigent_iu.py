import threading
import time
from collections import deque, namedtuple

import retico_core
from retico_core import abstract

RequiredIU = namedtuple('RequiredIU', ['iu_type', 'count'])
IUtoForward = namedtuple('IUtoForward', ['iu_type', 'creator_name'])


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

    def __init__(self, required_ius:[RequiredIU], type_of_iu_to_forward, creator_of_iu_to_forward, **kwargs):

        super().__init__(**kwargs)
        self.queue = deque()
        self.required_ius = required_ius
        self.required_ius_list = []
        # Build list containing <count> # of each IU Types to make sure we have the correct number of each IU type
        for key, count in self.required_ius:
            self.required_ius_list.extend([key] * count)
        # If there are two of the same iu type being awaited, the type is not enough to differentiate which one needs to be passed on to the module
        # subscribed to this. Use the creator name as well.
        self.type_of_iu_to_forward = type_of_iu_to_forward # Will be passing this IU on
        self.creator_name_of_iu_to_forward = creator_of_iu_to_forward

    def process_update(self, update_message):
            for iu, ut in update_message:
                self.queue.append(iu)

    def _extractor_thread(self):
         while self._extractor_thread_active:
            time.sleep(0.5)
            if len(self.queue) != len(self.required_ius_list):
                continue
            # Iterate over queue and pop all the items off, make sure they align with the expected IUs.
            # There is an issue if they don't so I'd like to know, but that shouldn't happen so not going to write logic to handle it rn.
            # make a copy of the required iu list so we can pop items from both it and the queue
            required_ius_list_copy = self.required_ius_list.copy()
            while self.queue:
                current_iu = self.queue.popleft()
                iu_type = required_ius_list_copy.pop(required_ius_list_copy.index(type(current_iu)))
                # Pass the IU on, this module will not show as in the IU history via grounded_in or creator
                if iu_type is self.type_of_iu_to_forward and current_iu.creator.name() is self.creator_name_of_iu_to_forward:
                    output_iu = current_iu

            if len(required_ius_list_copy) != 0:
                raise IndexError("Contingent IU Queue did not contain expected IUs")

            # NOTE: It may be helpful in the future to output a new IU that keeps a list of all the IUs that were awaited + implement a solution
            # using that list for navigating revokes.
            # With this current implementation the IU subscriber chain is interrupted because we lose the linear 'grounded_in' path from iu to iu
            # that we would have if we did not process these in parallel and instead subscribed to each module in a chronological fashion.
            # For example, I await a TextIU from GRED and an ObjectPermanenceIU from Object Permanence, but I only pass the ObjectPermanenceIU on to
            # any subscribed modules so the TextIU chain is lost.
            print(f"All IUs successfully awaited ({self.required_ius_list})")
            um = retico_core.UpdateMessage.from_iu(output_iu, retico_core.UpdateType.ADD)
            self.append(um)

    def prepare_run(self):
        self._extractor_thread_active = True
        threading.Thread(target=self._extractor_thread).start()

    def shutdown(self):
        self._extractor_thread_active = False
