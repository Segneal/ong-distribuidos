# Testing Guide for Messaging Service

This document provides comprehensive information about the testing suite for the messaging service.

## Overview

The messaging service includes a complete testing suite with:

- **Unit Tests**: Test individual components in isolation with mocks
- **Integration Tests**: Test complete flows with real Kafka and database connections
- **Error Handling Tests**: Test error scenarios and recovery mechanisms

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Unit test fixtures and configuration
├── test_producers.py              # Unit tests for message producers
├── test_consumers.py              # Unit tests for message consumers
├── test_models.py                 # Unit tests for data models
├── test_kafka_connection.py       # Unit tests for Kafka connection management
├── test_message_validation.py     # Unit tests for message format validation
└── integration/
    ├── __init__.py
    ├── conftest.py                # Integration test fixtures
    ├── test_kafka_integration.py  # Kafka integration tests
    ├── test_database_integration.py # Database integration tests
    ├── test_end_to_end_flows.py   # Complete flow tests
    └── test_error_handling.py     # Error handling integration tests
```

## Prerequisites

### For Unit Tests
- Python 3.8+
- pytest
- pytest-mock
- pytest-cov

### For Integration Tests
- All unit test requirements
- Apache Kafka running on localhost:9093 (or configured broker)
- PostgreSQL test database
- Network connectivity

## Running Tests

### Unit Tests Only
```bash
python run_unit_tests.py
```

### Integration Tests Only
```bash
python run_integration_tests.py --integration-only
```

### All Tests
```bash
python run_integration_tests.py --all
```

### Specific Test Categories
```bash
# Run only unit tests
pytest tests/ -m "not integration"

# Run only integration tests
pytest tests/integration/ -m "integration"

# Run tests with coverage
pytest tests/ --cov=messaging --cov-report=html
```

## Test Configuration

### Environment Variables

#### Unit Tests
```bash
TESTING=true
KAFKA_BROKERS=localhost:9092
ORGANIZATION_ID=test-org
KAFKA_GROUP_ID=test-group
```

#### Integration Tests
```bash
TESTING=true
KAFKA_TEST_BROKERS=localhost:9093
ORGANIZATION_ID=test-org
KAFKA_GROUP_ID=test-integration-group

# Database configuration
TEST_DB_HOST=localhost
TEST_DB_PORT=5432
TEST_DB_NAME=test_ong_management
TEST_DB_USER=test_user
TEST_DB_PASSWORD=test_pass
```

### Test Database Setup

Create a test database for integration tests:

```sql
CREATE DATABASE test_ong_management;
CREATE USER test_user WITH PASSWORD 'test_pass';
GRANT ALL PRIVILEGES ON DATABASE test_ong_management TO test_user;
```

### Kafka Setup for Integration Tests

For integration tests, you need Kafka running on a different port (9093) to avoid conflicts:

```bash
# Start Kafka on port 9093 for testing
kafka-server-start.sh config/server-test.properties
```

## Test Categories

### Unit Tests

#### Producer Tests (`test_producers.py`)
- Message envelope creation
- Message validation
- Kafka publishing with mocks
- Error handling in producers
- All message types (requests, offers, transfers, events, adhesions)

#### Consumer Tests (`test_consumers.py`)
- Message consumption and processing
- Message filtering (own vs external messages)
- Handler registration and execution
- Error handling in consumers
- Consumer lifecycle management

#### Model Tests (`test_models.py`)
- Data model serialization/deserialization
- Model validation
- Field requirements
- Type checking

#### Kafka Connection Tests (`test_kafka_connection.py`)
- Connection management
- Producer/consumer creation
- Admin client operations
- Topic creation
- Connection error handling

#### Message Validation Tests (`test_message_validation.py`)
- Message format validation
- Schema compliance
- Required field checking
- Data type validation

### Integration Tests

#### Kafka Integration (`test_kafka_integration.py`)
- Real Kafka producer-consumer flows
- Multiple topic messaging
- Message ordering
- Consumer groups
- Connection failure recovery

#### Database Integration (`test_database_integration.py`)
- Database synchronization
- External data storage
- Transaction handling
- Concurrent access
- Data integrity

#### End-to-End Flows (`test_end_to_end_flows.py`)
- Complete donation request flow
- Complete donation offer flow
- Complete transfer flow
- Complete event flow
- Complete adhesion flow
- Multi-organization scenarios

#### Error Handling (`test_error_handling.py`)
- Connection failure recovery
- Message processing errors
- Database error handling
- Serialization errors
- Timeout handling
- Resource cleanup

## Test Data

### Sample Test Data
The tests use realistic sample data for:
- Donation requests
- Donation offers
- Donation transfers
- Solidarity events
- Event adhesions
- Volunteer information

### Test Fixtures
Common fixtures provide:
- Mock Kafka components
- Mock database connections
- Sample message data
- Test configuration
- Helper functions

## Coverage Requirements

- **Unit Tests**: Minimum 80% code coverage
- **Integration Tests**: Focus on critical paths and error scenarios
- **Combined**: Target 85%+ overall coverage

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: python run_unit_tests.py
  
  integration-tests:
    runs-on: ubuntu-latest
    services:
      kafka:
        image: confluentinc/cp-kafka:latest
        ports:
          - 9093:9093
      postgres:
        image: postgres:13
        env:
          POSTGRES_DB: test_ong_management
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run integration tests
        run: python run_integration_tests.py --integration-only
```

## Troubleshooting

### Common Issues

#### Kafka Connection Errors
```
kafka.errors.NoBrokersAvailable: NoBrokersAvailable
```
**Solution**: Ensure Kafka is running on the configured port (9093 for integration tests)

#### Database Connection Errors
```
psycopg2.OperationalError: could not connect to server
```
**Solution**: Ensure PostgreSQL is running and test database exists

#### Import Errors
```
ModuleNotFoundError: No module named 'messaging'
```
**Solution**: Ensure src directory is in Python path (handled by test runners)

#### Test Timeouts
```
kafka.errors.KafkaTimeoutError: KafkaTimeoutError
```
**Solution**: Increase timeout values or check Kafka connectivity

### Debug Mode

Run tests with verbose output:
```bash
pytest tests/ -v -s --tb=long
```

Run specific test:
```bash
pytest tests/test_producers.py::TestBaseProducer::test_publish_donation_request -v
```

### Performance Testing

For performance testing of messaging flows:
```bash
pytest tests/integration/ -k "performance" --durations=0
```

## Best Practices

### Writing Tests
1. **Isolation**: Each test should be independent
2. **Mocking**: Use mocks for external dependencies in unit tests
3. **Cleanup**: Ensure proper cleanup of resources
4. **Assertions**: Use descriptive assertion messages
5. **Data**: Use realistic test data

### Test Organization
1. **Naming**: Use descriptive test names
2. **Grouping**: Group related tests in classes
3. **Documentation**: Document complex test scenarios
4. **Fixtures**: Reuse common setup through fixtures

### Error Testing
1. **Edge Cases**: Test boundary conditions
2. **Failures**: Test failure scenarios
3. **Recovery**: Test error recovery mechanisms
4. **Timeouts**: Test timeout handling

## Metrics and Reporting

### Coverage Reports
- HTML coverage reports generated in `htmlcov/`
- Terminal coverage summary
- Coverage badges for documentation

### Test Reports
- JUnit XML reports for CI integration
- Test duration reports
- Failure analysis

### Performance Metrics
- Message throughput testing
- Latency measurements
- Resource usage monitoring

## Future Enhancements

### Planned Improvements
1. **Load Testing**: Add performance/load tests
2. **Chaos Testing**: Add failure injection tests
3. **Contract Testing**: Add API contract tests
4. **Security Testing**: Add security-focused tests
5. **Monitoring**: Add test result monitoring

### Test Automation
1. **Pre-commit Hooks**: Run tests before commits
2. **Automated Regression**: Run tests on schedule
3. **Performance Benchmarks**: Track performance over time
4. **Test Data Management**: Automated test data generation