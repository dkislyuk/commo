# COMMO

Use the following to recompile thrift:

```
thrift -r --gen py --out schemas commo.thrift
```

For a simple test to start the Game server, run
```
python server.py
```

A single client can be joined via
```
python client.py
```

If you want to render the GameState for a client, start the client with:
```
python client.py --render
```

