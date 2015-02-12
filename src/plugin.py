
class PluginManager():

    #List of all listeners
    listeners = []
    mem_list  = []

    def add(listener, list_type):
        #Add a new listener to the list
        PluginManager.listeners.append(listener)

        #Type Memory
        if(list_type == 1):
            PluginManager.mem_list.append(listener)
            print("[PLUGIN] Added new Memory Listener:", listener)

    def notify(event, data):
        if(event == 1):
            for listener in PluginManager.mem_list:
                listener.notify(data)
            
class MemoryListener():
    def __init__(self, action):
        #Register the plugin with the manager
        PluginManager.add(self, 1)

        #Action to perform on notify
        self.action = action

    def notify(self, data):
        self.action(data)
