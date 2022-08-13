# Fundamentals

This part of the documentation describes the core elements of retico's incremental processing. The main classes in the retico framework are the {class}`IncrementalUnit<retico_core.abstract.IncrementalUnit>` and the {class}`AbstractModule<retico_core.abstract.AbstractModule>`. These are built to be general and extensible and thus should provide the basic building blocks for incremental networks.

After reading this part of the documentation, you should be able to create your own incremental modules and incremental units.

## Incremental Units

Incremental units are the general package for every type of information that should be transmitted incrementally. Each incremental unit finally inherits from the abstract class {class}`IncrementalUnit<retico_core.abstract.IncrementalUnit>` and has a set of basic functionalities. Many of these basic properties are driven by the incremental module itself, others require an incremental module to update information. 

### Basic attributes

While an incremental module can be instantiated, it should usually be created directly by an incremental module with the {meth}`create_iu<retico_core.abstract.AbstractModule.create_iu>` method (see next section). the IU then has the following attributes:

 - **creator**: A reference to the module that has created the IU
 - **iuid**: A unique ID given by the creating module.
 - **previous_iu**: The IU that was previously created by the module.
 - **grounded_in**: The IU that it was grounded in.
 - **payload**: An general representation of its contents
 - **committed**: A flag whether the IU is committed
 - **revoked**: A flag whether the IU is revoked
 - **created_at**: The timestamp at which the IU was created

During creation, each IU will limit its number of `grounded_in` and `previous_iu` connection depth by removing the connection. The reference depth of an IU is defined in the {meth}`IncrementalUnit.MAX_DEPTH<retico_core.abstract.IncrementalUnit.MAX_DEPTH>` value.

Each incremental unit needs to define the static {meth}`type<retico_core.abstract.IncrementalUnit.type>` method, which should return the type of the IU in a human-readable format. An example for the type output may be `Dialogue Act Incremental Unit`. This function may be called by debug modules or a graphical user interface in order to better represent an IU.

Another useful method to overwrite is the `__repr__` method that should return a string representation of the contents of the incremental unit. Per default it returns the human-readable type, the creator, and the first 10 characters of the string representation of the IU's payload.

### Provided methods

An IU provides convenience functions that might be useful when processing an IU.

The {meth}`age<retico_core.abstract.IncrementalUnit.age>` method returns the current age in seconds as a float. This might be helpful in deciding whether an IU still needs to be processed or if it is too old. Similarly, the {meth}`older_than<retico_core.abstract.IncrementalUnit.older_than>` method takes a timestamp as an argument and returns true if the IU is older than the given time.

If an incremental module has taken an IU out of its left buffer and processed it (e.g., created a hypothesis and potentially a new output IU based on it), the IU is marked as *processed* by the module. The {meth}`processed_list<retico_core.abstract.IncrementalUnit.processed_list>` method returns a list of all modules that have processed this IU. Similarly, the {meth}`is_processed_by<retico_core.abstract.IncrementalUnit.is_processed_by>` takes an incremental module as an argument and returns whether the IU was already processed by this module. While an incremental module automatically processes an IU, an IU can manually set to be processed by a module with the {meth}`set_processed<retico_core.abstract.IncrementalUnit.set_processed>` method.

## Update Message

Because an update to the state (i.e., hypothesis) of an incremental module might not be conveyed in a single incremental unit, updates are bundled together in an {class}`UpdateMessage<retico_core.abstract.UpdateMessage>`. An update message might contain multiple incremental units, each with an {class}`UpdateType<retico_core.abstract.UpdateType>` defined. An update type can be one of

 - `add`: The IU should be added to the current hypothesis
 - `update`: The IU should be updated to reflect new information
 - `revoke`: The IU should be revoked from the current hypothesis
 - `commit`: The IU should be committed and will not change in the future

An empty UpdateMessage might be instantiated with its constructor. Additionally, it can be instantiated from a single IU with the {meth}`from_iu<retico_core.abstract.UpdateMessage.from_iu>` class method or from a list of tuples (IncrementalUnit, UpdateType) with the {meth}`from_iu_list<retico_core.abstract.UpdateMessage.from_iu_list>` class method.

### Methods

IUs can be added to an UpdateMessage with the {meth}`add_iu<retico_core.abstract.UpdateMessage.add_iu>` method for a single IU or the {meth}`ad_ius<retico_core.abstract.UpdateMessage.ad_ius>` method for a list of tuples (IncrmentalUnit, UpdateType). For these two methods, the `strict_update_type` flag may be set to false. This way, an update type might be any string as opposed to the ones defined in the {class}`UpdateType<retico_core.abstract.UpdateType>` enum.

The method {meth}`has_valid_ius<retico_core.abstract.UpdateMessage.has_valid_ius>` takes an IU class or a list of IU classes as an argument and returns whether all IUs in the UpdateMessage are instances of that class (or list of classes).

The {meth}`update_types<retico_core.abstract.UpdateMessage.update_types>` and {meth}`incremental_units<retico_core.abstract.UpdateMessage.incremental_units>` methods are generators that give access to the update types or IUs, respectively. 

## Incremental Queue

The {class}`IncrementalQueue<retico_core.abstract.IncrementalQueue>` inherits from pythons own queue class and defines the queue used in each incremental module. The incremental queue provides access to `provider` and `consumer` attributes, which reference the modules that provide and consume the IUs of the queue, respectively.

## Incremental Modules

{class}`AbstractModules<retico_core.abstract.AbstractModule>` are the main processing classes of retico. An incremental module might take one or more types of IU as an input and outputs a single type of IU.

An incremental module might be instantiated with a specific `queue_class` (of type {class}`IncrementalQueue<retico_core.abstract.IncrementalQueue>`), that is used for transmitting the incremental units. Additionally, `meta_data` can be provided as a dict. This meta-information may be used by a user interface to store position and other information about a module. This meta-data is also preserved when the module is saved to disk.

Generally, an incremental module needs to implement the following methods: {meth}`name<retico_core.abstract.AbstractModule.name>`, {meth}`description<retico_core.abstract.AbstractModule.description>`, {meth}`input_ius<retico_core.abstract.AbstractModule.input_ius>`, and {meth}`output_iu<retico_core.abstract.AbstractModule.output_iu>`. The `name` method should return the name and the `description` method the description of the incremental module in a human readable format. The `input_ius` method should return a list of all incremental unit classes that are acceptable as an input to the module. The `output_iu` method should return the class of the incremental units that are produced by the module. 

### Connecting modules

A network of multiple incrmental modules can be created by connecting modules with an incremental queue. This connection can be performed with the {meth}`subscribe<retico_core.abstract.AbstractModule.subscribe>` method, which takes an incremental module as an input and creates an incremental queue in which the update messages of the module on which `subscribe` is called are routed to the left buffer of the module which is given as an argument. For example, `a.subscribe(b)` would create an incremental queue in which the updatge messages in the right buffer of `a` are routed into the left buffer of `b`. The resulting left and right buffers can be accessed with the {meth}`left_buffers<retico_core.abstract.AbstractModule.left_buffers>` and {meth}`right_buffers<retico_core.abstract.AbstractModule.right_buffers>` methods respectively.

The execution of a module can be started with the {meth}`run<retico_core.abstract.AbstractModule.run>` method, which runs the setup method per default. The argument `run_setup` defines whether the setup method should be exectued before the execution. The execution can be stopped with the {meth}`stop<retico_core.abstract.AbstractModule.stop>` method. An example on how to connect an run a network may look like this:

```python
m1 = Module1()
m2 = Module2()
m3 = Module3()

m1.subscribe(m2)
m2.subscribe(m3)

retico.network.run(m1)

# Wait for an input from the user
input()

retico.network.stop(m1)
```

### Main Update Loop

Each incremental module may override a {meth}`setup<retico_core.abstract.AbstractModule.setup>`, a {meth}`prepare_run<retico_core.abstract.AbstractModule.prepare_run>`, and a {meth}`shutdown<retico_core.abstract.AbstractModule.shutdown>` method. The `setup` method is intended to setup potential resources needed for the execution of the module. However, there is no guarantee that the module is run immediately after the `setup` method is executed. This setup method can be used to initialize all modules of a network before they are being executed and produce IUs. The `prepare_run` method is always executed right after the module is executed. No long setup routines should be executed in this method, as other modules in the network might already start producing IUs. The `shutdown` method is called after the network is stopped. This method may clear the buffers of the module and free resources. Generally, after the shutdown method is called, the module should be able to setup and run again.

The incremental module defines the {meth}`process_update<retico_core.abstract.AbstractModule.process_update>` method that can be used to handle incoming IUs and to produce new output IUs. The method gets called automatically if a new update message is appended to the left buffer. The method may process the included IUs of the update message and, as a result, produce one or more outputIUs. To produce correct IUs of the right type, the {meth}`create_iu<retico_core.abstract.AbstractModule.create_iu>` method of the incremental module should be used. This method returns an IU that has already connections to previously generated IUs of the module and sets the `grounded_in` connection (if it was provided as an argument). The {meth}`process_update<retico_core.abstract.AbstractModule.process_update>` method might return `None` or an UpdateMessage containing the generated IUs. This update message is automatically appended to the right buffer and forwarded to all connected modules. Alternatively, the {meth}`append<retico_core.abstract.AbstractModule.append>` method can be used to append an update message to the right buffer of the module.

### Event System

Incremental modules have an event system that can be used to create callbacks if certain events occur. To setup a callback for one event, the {meth}`event_subscribe<retico_core.abstract.AbstractModule.event_subscribe>` method has to be called with the `event_name` and a callback function. The `event_name` needs to be either a specific event implemented in the module or `*` to catch all events that are being called. The callback function has to take three arguments: the first argument is given the module that called the event, the second argument is the name of the event and the third argument is a dict that may contain additional information on the event. An example may look like this:

```python

def my_callback(module, event_name, data):
    print(f"{module} called event {event name} with data: {data}")

mymodule.event_subscribe("*", my_callback)
```

Incremental module may define their own events with the {meth}`event_call<retico_core.abstract.AbstractModule.event_call>` method, which takes an `event_name` and a `data` dictionary as an argument. Every callback that is subscribed to that event name is being called with the module, event name, and data that is provided in the dictionary. An event name can be any string except "*".

The AbstractModule defines and uses the following events:

| Event                        | Event Name             | Description                                                                                              |
|------------------------------|------------------------|----------------------------------------------------------------------------------------------------------|
| {meth}`EVENT_PROCESS_IU<retico_core.abstract.AbstractModule.EVENT_PROCESS_IU>`             | process_iu             | Gets called after an IU is processed with the IU as `iu` in the data.                                    |
| {meth}`EVENT_PROCESS_UPDATE_MESSAGE<retico_core.abstract.AbstractModule.EVENT_PROCESS_UPDATE_MESSAGE>` | process_update_message | Gets called after an update message is processed with the UpdateMessage as `update_message` in the data. |
| {meth}`EVENT_SUBSCRIBE<retico_core.abstract.AbstractModule.EVENT_SUBSCRIBE>`              | subscribe              | Gets called when another module subscribes to the module.                                                |
| {meth}`EVENT_START<retico_core.abstract.AbstractModule.EVENT_START>`                  | start                  | Gets called when the module is started.                                                                  |
| {meth}`EVENT_STOP<retico_core.abstract.AbstractModule.EVENT_STOP>`                   | stop                   | Gets called when the module is stopped.                                                                  |

### Producing Modules

The {class}`AbstractProducingModule<retico_core.abstract.AbstractProducingModule>` defines the general behavior of a moudle that does not have a left buffer and thus not takes any IUs as an input. This class might be used for the recording of external sources like a microphone.

In the producing module the `process_update` method is called continuously with `None` as an input. This is a simple solution to producing incremental units. The `input_ius` method returns an empty array and thus, it does not accept any input IUs. 

### Consuming Modules

Similar to producing modules, the {class}`AbstractConsumingModule<retico_core.abstract.AbstractConsumingModule>` does not produce any output IUs. This class might be used for the piping of data to externals sources like a loudspeaker.

In the consuming module, the `subscribe` method returns a ValueError and also the `output_iu` method returns `None`. This ensures that the module does not produce any outgoing IUs.


### Trigger Module

A trigger module is a form of a producing module that implements a {meth}`trigger<retico_core.abstract.AbstractTriggerModule.trigger>` method. This method may be called to produce an IU. This module makes it possible to introduce new IUs to the system for debug purposes or to connect user driven input to a network.

## Savind and loading incremental networks

The {class}`Network<retico_core.network>` module provides functions to save and load networks. The {meth}`save<retico_core.network.save>` function takes a module and an a filename as arguments. Through a discovery process, the network is extracted from the module and stored into a file. For the serialization pythons `pickle` functionality is used.


The {meth}`load<retico_core.network.load>` function loads the file given in the parameter and returns a list of modules and a list of connections between those module. The modules are already connected in the way they were saved. The connections list contains tuples of two modules that are connected to each other.