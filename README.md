# COMMO

Use the following to recompile thrift:

```
thrift -r --gen py --out schemas commo.thrift
```

=========================================

For a simple test to start the Game server, run
```
python server.py
```

To run the server on a remote host, change the IP address in config.py

=========================================

A single client can be joined via
```
python client.py
```

If you want to render the GameState for a client, start the client with:
```
python client.py --render
```

Choose the client type via the --player-type parameter:
```
python client.py --render --player-type PLAYER1
```
