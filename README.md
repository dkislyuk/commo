# COMMO

Use the following to recompile thrift:

```
thrift -r --gen py --out schemas commo.thrift
```

For a simple test to start the BoringGame server, run
```
python server.py
```

A single client can be joined via
```
python client.py
```
