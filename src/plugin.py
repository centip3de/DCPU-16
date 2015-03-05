
class PluginManager():

    #List of all listeners
    listeners = []
    mem_list  = []
    reg_list  = []
    pnt_list  = []

    def add(listener, list_type):
        #Add a new listener to the list
        PluginManager.listeners.append(listener)

        #Type Memory
        if(list_type == 1):
            PluginManager.mem_list.append(listener)
            print("[PLUGIN] Added new Memory Listener:", listener)

        if(list_type == 2):
            PluginManager.reg_list.append(listener)
            print("[PLUGIN] Added new Register Listener:", listener)

        if(list_type == 3):
            PluginManager.pnt_list.append(listener)
            print("[PLUGIN] Added new Print Listener:", listener)

    def notify(event, data):
        if(event == 1):
            for listener in PluginManager.mem_list:
                listener.notify(data)

        if(event == 2):
            for listener in PluginManager.reg_list:
                listener.notify(data)

        if(event == 3):
            for listener in PluginManager.pnt_list:
                listener.notify(data)

    def unregister(listener):
        PluginManager.listeners.remove(listener)

        if(listener in PluginManager.mem_list):
            PluginManager.mem_list.remove(listener)

        elif(listener in PluginManager.reg_list):
            PluginManager.reg_list.remove(listener)

        elif(listener in PluginManager.pnt_list):
            PluginManager.pnt_list.remove(listener)

        print("[PLUGIN] Removed listner:", listener)
            
class MemoryListener():
    def __init__(self, action):
        #Register the plugin with the manager
        PluginManager.add(self, 1)

        #Action to perform on notify
        self.action = action

    def notify(self, data):
        self.action(data)

    def unregister(self):
        PluginManager.unregister(self)

class RegisterListener():
    def __init__(self, action):
        PluginManager.add(self, 2)

        self.action = action

    def notify(self, data):
        self.action(data)

    def unregister(self):
        PluginManager.unregister(self)

class PrintListener():
    def __init__(self, action):
        PluginManager.add(self, 3)

        self.action = action

    def notify(self, data):
        self.action(data)

    def unregister(self):
        PluginManager.unregister(self)

