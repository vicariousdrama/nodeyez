import copy, json, random, select, socket, sys, threading, time

mockMinerFile = "../mock-data/miner-braiins.json"
mockMinerFile = "../mock-data/miner-microbt.json"
mockMinerFile = "../mock-data/miner-antminers19.json"

maximumClients = 5
bindAddress = 'localhost'
bindPort = 4028
selectTimeout = 1


def change_value(dictItem, arrayOfOrderedKeys, lowPercentage=.95, highPercentage=1.05):
    if len(arrayOfOrderedKeys) == 0: return
    keyName = arrayOfOrderedKeys.pop(0) # get next element from array.should be key in dict
    if len(arrayOfOrderedKeys) > 0:
        if keyName in dictItem:
            copyOfOrderedKeys = copy.deepcopy(arrayOfOrderedKeys)
            keyValueObject = dictItem[keyName]
            if type(keyValueObject) is dict: 
                change_value(keyValueObject, copyOfOrderedKeys, lowPercentage, highPercentage) # traverse nested dict
            if type(keyValueObject) is list:
                for keyValueItem in keyValueObject: 
                    copyOfOrderedKeys = copy.deepcopy(arrayOfOrderedKeys)
                    change_value(keyValueItem, copyOfOrderedKeys, lowPercentage, highPercentage) # each array item should be a dict
    else:
        if keyName in dictItem:
            originalValue = dictItem[keyName]
            modifiedValue = originalValue
            if type(originalValue) is float:
                lowValue = originalValue * lowPercentage
                highValue = originalValue * highPercentage
                modifiedValue = (random.random() * (highValue - lowValue)) + lowValue
            elif type(originalValue) is int:
                lowValue = int(originalValue * lowPercentage)
                highValue = int(originalValue * highPercentage)
                modifiedValue = random.randint(lowValue,highValue)
            if modifiedValue != originalValue:
                print(f"changing {keyName} from {originalValue} to {modifiedValue}")
                dictItem[keyName] = modifiedValue

def change_hashrate(r):
    change_value(r, ["STATS", "GHS 5s"], .95, 1.05)             # antminers19
    change_value(r, ["summary","SUMMARY","MHS 1m"], .95, 1.05)  # microbt, braiins


def change_power(r):
    change_value(r, ["summary", "SUMMARY", "Power"], .98, 1.01)             # microbt
    change_value(r, ["tunerstatus", "TUNERSTATUS", "ApproximateMinerPowerConsumption"], .98, 1.02) # braiins

def change_fans(r):
    change_value(r, ["STATS", "fan1"], .95, 1.05)                           # antminers19
    change_value(r, ["STATS", "fan2"], .95, 1.05)                           # antminers19
    change_value(r, ["STATS", "fan3"], .95, 1.05)                           # antminers19
    change_value(r, ["STATS", "fan4"], .95, 1.05)                           # antminers19
    change_value(r, ["fans", "FANS", "RPM"], .75, 1.05)                     # braiins
    change_value(r, ["summary", "SUMMARY", "Fan Speed In"], .60, 1.05)      # microbt
    change_value(r, ["summary", "SUMMARY", "Fan Speed Out"], .80, 1.05)     # microbt
    pass

def change_temps(r):
    for t in range(3):
        change_value(r, ["STATS", f"temp{t+1}"], .95, 1.05)                 # antminers19
        change_value(r, ["STATS", f"temp2_{t+1}"], .95, 1.05)               # antminers19
    change_value(r, ["devs", "DEVS", "Chip Temp Max"], .95, 1.05)           # microbt
    change_value(r, ["devs", "DEVS", "Temperature"], .95, 1.05)             # microbt
    change_value(r, ["temps", "TEMPS", "Board"], .95, 1.05)                 # braiins
    change_value(r, ["temps", "TEMPS", "Chip"], .95, 1.05)                  # braiins
    pass

def handle_client(client, address):
    print(f"Handling client from {address}")
    while True:
        request_bytes = None
        try:
            request_bytes = b"" + client.recv(1024)
        except BlockingIOError as e:
            print(e)
        # dump if no bytes
        if not request_bytes or request_bytes is None:
            print(f"- client was closed at {address}")
            client.close()
            return
        # parse the bytes into a string
        print(f"- decoding data from {address}")
        request_str = ""
        try:
            request_str = request_bytes.decode()
        except Exception as e:
            print(f"- request_bytes could not be decoded from {address}")
            request_str = ""
        j = {}
        try:
            j = json.loads(request_str)
        except Exception as e:
            print(f"- client {address} sent data that is not json: {request_str}")
            j = {}
        if "command" not in j:
            print(f"- invalid request from {address}")
            client.sendall(b"{\"error\":\"invalid request. json with command expected\"}")
            client.shutdown(1)
        else:
            result = {}
            # add parts to the result based on command given
            command = j["command"]
            commandParts = command.split("+")
            for commandPart in commandParts:
                if commandPart in minerDefinition:
                    print(f"- assembling {commandPart} for {address}")
                    partDefinition = minerDefinition[commandPart]
                    result[commandPart] = copy.deepcopy(partDefinition)
            if len(result.keys()) == 0: # antminer-s19 uses uppercase and no nesting
                for commandPart in commandParts:
                    ucommandPart = str(commandPart).upper()
                    if ucommandPart in minerDefinition:
                        print(f"- assembling {ucommandPart} for {address}")
                        partDefinition = minerDefinition[ucommandPart]
                        result[ucommandPart] = copy.deepcopy(partDefinition)
            # manipulate the data to simulate changes over time
            change_hashrate(result)
            change_power(result)
            change_fans(result)
            change_temps(result)
            # send it back
            print(f"- sending result to {address}")
            resultj = json.dumps(result)
            try:
                client.sendall(bytes(resultj, "UTF-8"))
                client.shutdown(1)
            except OSError as e:
                print(e)
    
if __name__ == '__main__':

    print("Initializing mock miner.")
    print(f"Default bind address     {bindAddress}")
    print(f"Default bind port:       {bindPort}")
    print(f"Default maximum clients: {maximumClients}")
    print(f"Default select timeout:  {selectTimeout}")
    print(f"Default mock miner file: {mockMinerFile}")

    if len(sys.argv) > 1:
        l = len(sys.argv)
        for i in range(l):
            if i >= l: break
            if sys.argv[i] in ['-a', '--address']:
                v = sys.argv[i+1]
                if bindAddress != v:
                    bindAddress = v
                    print(f"Override bind address set to {bindAddress}")
            if sys.argv[i] in ['-c', '--maxclients']:
                v = int(sys.argv[i+1])
                if maximumClients != v:
                    maximumClients = v
                    print(f"Override maximum clients set to {maximumClients}")
            if sys.argv[i] in ['-f', '--file']:
                v = sys.argv[i+1]
                if mockMinerFile != v:
                    mockMinerFile = v
                    print(f"Override mock miner file set to {mockMinerFile}")
            if sys.argv[i] in ['-p', '--port']:
                v = int(sys.argv[i+1])
                if bindPort != v:
                    bindPort = v
                    print(f"Override bind port set to {bindPort}")
            if sys.argv[i] in ['-t', '--selecttimeout']:
                v = int(sys.argv[i+1])
                if selectTimeout != v:
                    selectTimeout = v
                    print(f"Override select timeout set to {selectTimeout}")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(False)
    tryagain = True
    while tryagain:
        try:
            server.bind((bindAddress, bindPort))
            tryagain = False
        except OSError as e:
            print(e)
            print("Retrying  to bind to address and port in 2 seconds")
            time.sleep(2)
    server.listen(maximumClients)
    inputs = [server]
    outputs = []
    message_queues = {}
    totalClients = 0

    with open(mockMinerFile) as f: minerDefinition = json.load(f)
    while inputs:
        time.sleep(1)
        print(f"Connected clients: {len(inputs)}. Total served: {totalClients}")
        inputs2 = []
        for input in inputs:
            if not input._closed:
                inputs2.append(input)
        inputs = inputs2
        readable, writable, exceptional = select.select(
            inputs, outputs, inputs, selectTimeout)
        for s in readable:
            if s is server:
                connection, client_address = s.accept()
                connection.setblocking(False)
                inputs.append(connection)
                totalClients += 1
                threading.Thread(target=handle_client, args=(connection, client_address)).start()