# Redis Workshop Server

A simple server implementation with Redis protocol support.

## Project Structure

The project is organized into the following components:

```
redis_workshop/
├── src/
│   │── main.py              
│   │── server.py            
│   │── connection_handler.py
│   │── protocol_handler.py  
│   │── command_handler.py
│   │── datastore.py
│   │── log.aof
│   │── out.pstats
│   │── persistence.py
│   │── task_handler.py
tests/                  
│   ├── unit/               
│   │   ├── test_command.py
│   │   │── test_datastore.py
│   │   │── test_server.py
│   │   │── test_connection_handler.py
│   │   │── test_protocol_handler.py
│   │   │── test_command_handler.py
│   │   │── test_datastore.py
│   │   │── test_persistance.py
│   │   │── test_task_handler.py
│   ├── integration/
│   │   │── conftest.py
│   |   │── test_echo.py
│   │   │── test_exist_and_del.py
│   │   │── test_incr_decr.py
│   │   │── test_integration.py
│   │   │── test_list_commands.py
│   │   │── test_persistence.py
│   │   │── test_ping.py
│   │   │── test_set_and_get.py
└── pyprojec.toml

```

## Components

1. **Main Component** (`main.py`):
   - Handles command-line arguments
   - Parses port ranges
   - Creates and starts the server

2. **Server Component** (`server.py`):
   - Manages socket creation and binding
   - Handles TCP and UDP connections
   - Routes connections to appropriate handlers

3. **Connection Handler Component** (`connection_handler.py`):
   - Processes client data
   - Implements command handlers (echo, hex dump, etc.)
   - Manages client communication

## Testing Approach

The project uses pytest for testing with a hybrid approach:

1. **Unit Tests**:
   - Test individual components in isolation
   - Mock external dependencies
   - Focus on specific functionality

2. **Integration Tests**:
   - Test end-to-end functionality
   - Verify components work together correctly
   - Test real network communication

## Running Tests

To run all tests:

```bash
python -m pytest
```

To run specific test categories:

```bash
# Run only unit tests
python -m pytest tests/unit

# Run only integration tests
python -m pytest tests/integration

```

## Running the Server

Start the server with various options:

```bash
# Basic echo server on port 8888
python main.py -p 8888

# Basic port range scanner
python main.py -p 8888-9000
# UDP server on port 8889
python main.py -l udp -p 8889

# Server with hex dump on port 8890
python main.py -p 8890 -x true

# Server that executes commands from clients
python main.py -p 8891 -e true

***********************************
# Redis interactive Server on port 8001
python main.py -p 8001 -i I

```

## Performance
1) MVP: 
SET: 6796.25 requests per second, p50=5.023 msec                   
GET: 5263.43 requests per second, p50=7.023 msec 

2) Optimizations*:
   1) Background scan switched on:
      SET: 21222.41 requests per second, p50=1.567 msec
      GET: 26497.09 requests per second, p50=1.311 msec
      
   2) Background scan switched of:
      SET: 24709.66 requests per second, p50=1.375 msec
      GET: 24125.45 requests per second, p50=1.487 msec

_*using cache friendly datastructures_
## Benchmark (P.I.T):
SET: 71684.59 requests per second, p50=0.543 msec                   
GET: 73475.39 requests per second, p50=0.543 msec
