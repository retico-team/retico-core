"""
Debug Module
============

This file contains general debug modules that can be used to output information from any
incremental unit.
"""

import logging
import os
import json
from retico_core import network
from retico_core import abstract, text



class DebugModule(abstract.AbstractConsumingModule):
    """A debug module that prints the IUs that are coming in."""

    @staticmethod
    def name():
        return "Debug Module"

    @staticmethod
    def description():
        return "A consuming module that displays IU infos in the console."

    @staticmethod
    def input_ius():
        return [abstract.IncrementalUnit]

    def __init__(self, print_payload_only=False):
        super().__init__()
        self.print_payload_only = print_payload_only

    def process_update(self, update_message):
        if self.print_payload_only:
            for iu, ut in update_message:
                print(ut, iu.payload)
        else:
            print(f"Debug: Update Message ({len(update_message)})")
            for i, (iu, ut) in enumerate(update_message):
                print(f"{i}: {iu} (UpdateType: {ut})")
                print("  PreviousIU:", iu.previous_iu)
                print("  GroundedInIU:", iu.grounded_in)
                print("  Age:", iu.age())
            print(f"End of Debug Message")


class CallbackModule(abstract.AbstractConsumingModule):
    """A debug module that returns the incoming update messages into a callback
    function."""

    @staticmethod
    def name():
        return "Callback Debug Module"

    @staticmethod
    def description():
        return (
            "A consuming module that calls a callback function whenever an"
            "update message arrives."
        )

    @staticmethod
    def input_ius():
        return [abstract.IncrementalUnit]

    def __init__(self, callback, **kwargs):
        """Initializes the module with a callback function that has to take one argument
        that contains the update message whenever it arrives.
        """
        super().__init__(**kwargs)
        self.callback = callback

    def process_update(self, update_message):
        self.callback(update_message)


class TextPrinterModule(abstract.AbstractConsumingModule):
    """A debug module that prints the incoming text and updates it as text IUs are
    arriving. Once an IU is committed, the next incoming text is printed in a new
    line."""

    @staticmethod
    def name():
        return "Text Printer Module"

    @staticmethod
    def description():
        return "A module that prints out and updates text."

    @staticmethod
    def input_ius():
        return [text.TextIU]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._old_text = ""

    def process_update(self, update_message):
        for iu, ut in update_message:
            if ut == abstract.UpdateType.ADD:
                self.current_input.append(iu)
            elif ut == abstract.UpdateType.REVOKE:
                self.revoke(iu)
            elif ut == abstract.UpdateType.COMMIT:
                self.commit(iu)
        text = " ".join(iu.text for iu in self.current_input)
        print(" " * len(self._old_text), end="\r")
        print(text, end="\r")
        self._old_text = text
        if self.input_committed():
            self.current_input = []
            print("")


class LoggerModule(abstract.AbstractConsumingModule):
    """A debug module that logs IUs and network from any module that takes in and outputs IUs to a websocket that are coming in."""

    @staticmethod
    def name():
        return "Logger Module"

    @staticmethod
    def description():
        return "A consuming module that logs IUs and the full network to a websocket and writes logs in a logs directory."

    @staticmethod
    def input_ius():
        return [abstract.IncrementalUnit]

    def __init__(self, sio, route):
        super().__init__()
        self.sio = sio
        self.UM = dict()
        self.network_route = 'network'
        self.route = route
        self.logger = logging.getLogger(name=self.name())
        self.config_logger()
        self.computed_network = False
        
    def config_logger(self):
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_cnt = len(os.listdir(log_dir))
        log_file = os.path.join(log_dir, f'{self.name()}.log{log_cnt}')
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(name)s - %(message)s')
        
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
        
    def config_network(self):
        m, c = network.discover(self)
        
        network_list = dict()
        
        for mod in m:
            network_list[mod.name()] = {
                'current_mod': mod.name(),
                'previous_mods': list(),
                'next_mods': list(),
            }
            
        for to_mod, from_mod in c:
            network_list[to_mod.name()]['previous_mods'].append(from_mod.name())
            network_list[from_mod.name()]['next_mods'].append(to_mod.name())
        
        indegree_count = dict()
        
        for mod in m:
            indegree_count[mod.name()] = 0
            
        for to_mod, _ in c:
            indegree_count[to_mod.name()] += 1
        
        print("DISCOVERED MODULES AND CONNECTIONS")
        print(f"Modules: {m}")
        print(f"Connections: {c}")
        print(f"Degree Count: {indegree_count}")
        print(f"Network List: {network_list}")
        self.computed_network = True
        return m, c, indegree_count, network_list

    def process_update(self, update_message):
        msg_len = len(update_message)
        
        if not self.computed_network:
            modules, connections, indegree_count, network_list = self.config_network()
            network_info = {
                'NetworkList': network_list,
                'DegreeCount': indegree_count,
                'Modules': [mod.name() for mod in modules],
                'Connections': [
                    {
                        'From': conn[1].name(),
                        'To': conn[0].name(),
                    } for conn in connections
                ],
            }
            self.sio.emit(self.network_route, network_info)
            self.logger.info(json.dumps(network_info))
        
        for i, (iu, ut) in enumerate(update_message):
            if iu.previous_iu != None and iu.grounded_in != None:
                self.UM[i] = {
                    'IU': str(iu.payload),
                    'UpdateType': ut.value.upper(),
                    'Module': iu.creator.name(),
                    'IUType': str(iu.type()),
                    'IUID': str(iu.iuid),
                    'PreviousIUID': str(iu.previous_iu.iuid),
                    'Age': iu.age(),
                    'TimeCreated': iu.created_at,
                    'GroundedIn': {
                        'IUID': str(iu.grounded_in.iuid),
                        'IUType': str(iu.grounded_in.type()),
                        'Module': iu.grounded_in.creator.name(),
                        'Age': str(iu.grounded_in.age()),
                        'TimeCreated': iu.grounded_in.created_at,
                    },
                }
                
                self.sio.emit(self.route, self.UM[i])
                self.logger.info(json.dumps(self.UM[i]))

            # edge case where first iu is being made
            elif iu.grounded_in != None and iu.previous_iu == None:
                self.UM[i] = {
                    'IU': str(iu.payload),
                    'UpdateType': ut.value.upper(),
                    'Module': iu.creator.name(),
                    'IUType': str(iu.type()),
                    'IUID': str(iu.iuid),
                    'PreviousIU': None,
                    'Age': iu.age(),
                    'TimeCreated': iu.created_at,
                    'GroundedIn': {
                        'IUID': str(iu.grounded_in.iuid),
                        'IUType': str(iu.grounded_in.type()),
                        'Module': iu.grounded_in.creator.name(),
                        'Age': str(iu.grounded_in.age()),
                        'TimeCreated': iu.grounded_in.created_at,
                    },
                }
                
                self.sio.emit(self.route, self.UM[i])
                self.logger.info(json.dumps(self.UM[i]))

            else:
                print("Edge case where grounded_in and previous_iu is None")
                self.logger.warning("Edge case where grounded_in and previous_iu is None")
                

        self.UM.clear()