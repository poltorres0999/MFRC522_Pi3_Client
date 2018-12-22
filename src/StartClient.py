from NFCClient import NFCClient

server_ip = "192.168.1.160"
server_port = 4445

client = NFCClient(server_ip, server_port)
client.init_client()
client.run_client()


