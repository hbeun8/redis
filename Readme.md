# Redis Workshop Server

A simple server implementation with Redis protocol support.

## Project Structure

The project is organized into the following components:

```
redis_workshop/
├── src/
|   |── main.py              # Entry point and command-line argument handling
|   |── server.py            # Server setup and connection management
├   |── connection_handler.py# Client connection handling and command processing
├   |── protocol_handler.py  # Redis protocol parsing implementation
├── tests/                  # Test suite
│   ├── unit/               # Unit tests for individual components
│   │   ├── test_command.py
│   │   └── test_datastore.py
    |   |── test_expiry.py
    |   |── test_main.py
    |   |── test_protocol.py
    |   |── test_server.py
│   ├── integration/        # Integration tests for server functionality
│   │   └── conftest.py
    |   |── test_echo.py
    |   |── test_exist_and_del.py
    |   |── test_incr_decr.py
        |── test_integration.py
│       |── test_list_commands.py
|       |── test_persistence.py
|       |── test_ping.py
|       |── test_set_and_get.py
└── pytest.ini              # Pytest configuration
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
   1) pypy:
      SET: 16286.65 requests per second, p50=2.127 msec                   
      GET: 19470.40 requests per second, p50=1.815 msec 
   2) Code Improvements (builtin):
      SET: 20691.08 requests per second, p50=1.935 msec
      GET: 24160.43 requests per second, p50=1.671 msec
   3) Concurrency (aysncio):
      
## BENCHMARK:
SET: 71684.59 requests per second, p50=0.543 msec                   
GET: 73475.39 requests per second, p50=0.543 msec