# Integration Testing Documentation

This document describes the integration tests implemented for the reports-service as part of task 10.2.

## Overview

The integration tests validate three main areas:
1. **Database Integration** - Connection and basic operations
2. **Excel Generation Integration** - File creation and manipulation
3. **SOAP Integration** - External service connectivity

## Test Files

### 1. `tests/test_integration.py`
Comprehensive pytest-based integration tests with proper mocking and error handling.

**Test Classes:**
- `TestDatabaseIntegration` - Database connectivity tests
- `TestExcelIntegration` - Excel file generation tests  
- `TestSOAPIntegration` - SOAP service integration tests
- `TestServiceIntegration` - Service layer integration tests

### 2. `test_integration_simple.py`
Standalone integration test script that doesn't require pytest. Useful for quick validation.

### 3. `run_integration_tests.py`
Test runner script for executing pytest integration tests with proper configuration.

## Running the Tests

### Option 1: Using pytest (Recommended)
```bash
# Run all integration tests
python -m pytest tests/test_integration.py -v

# Run specific test class
python -m pytest tests/test_integration.py::TestExcelIntegration -v

# Run with integration marker
python -m pytest tests/test_integration.py -m integration -v
```

### Option 2: Using the test runner script
```bash
python run_integration_tests.py

# Run specific test class
python run_integration_tests.py TestDatabaseIntegration
```

### Option 3: Using the simple test script
```bash
python test_integration_simple.py
```

## Test Coverage

### Database Integration Tests

**What is tested:**
- Database connection establishment
- Database session creation and management
- Model imports and instantiation
- Basic SQL query execution
- Table existence verification

**Expected behavior:**
- Tests gracefully handle database connection failures in test environments
- Model classes can be imported and instantiated
- Database sessions can be created when connection is available

**Limitations:**
- Tests skip database operations if connection is not available
- Uses default database configuration from settings

### Excel Integration Tests

**What is tested:**
- Excel service initialization
- Workbook creation with multiple sheets
- File I/O operations
- Filename generation with filters
- Excel formatting and data population

**Expected behavior:**
- Excel files can be created and saved
- Workbooks contain properly formatted data
- File operations work correctly on the filesystem
- Temporary files are cleaned up properly

**Mock dependencies:**
- Database sessions are mocked
- Settings are mocked for storage paths
- Donation data is mocked for testing

### SOAP Integration Tests

**What is tested:**
- SOAP client initialization
- Service method calls (president data, organization data)
- Combined data queries
- Error handling (Fault, TransportError, generic exceptions)
- Connection testing

**Expected behavior:**
- SOAP client can be initialized with proper configuration
- Service methods return expected data structures
- Errors are properly caught and converted to custom exceptions
- Tests gracefully handle zeep/cgi compatibility issues in Python 3.13

**Mock dependencies:**
- zeep.Client is mocked to avoid external service dependencies
- SOAP responses are mocked with realistic data structures

### Service Integration Tests

**What is tested:**
- Service class imports and instantiation
- Configuration loading and validation
- Service method availability
- Basic service functionality

**Expected behavior:**
- All service classes can be imported and instantiated
- Configuration settings are properly loaded
- Services have expected methods and attributes

## Test Environment Considerations

### Database Connection
- Tests expect MySQL database with specific credentials
- Connection failures are handled gracefully with skip messages
- Tests can run without database connectivity

### SOAP Service Compatibility
- Python 3.13 has compatibility issues with zeep library (missing cgi module)
- Tests detect this and skip SOAP tests with appropriate messages
- SOAP functionality is tested through mocking when direct testing isn't possible

### File System Operations
- Tests use temporary directories for file operations
- Windows file locking issues are handled with retry logic
- Temporary files are cleaned up after tests

## Test Results Interpretation

### Successful Test Run
```
🎉 All integration tests passed!
Tests passed: 4/4
  ✅ Database Integration
  ✅ Excel Integration  
  ✅ SOAP Integration
  ✅ Service Integration
```

### Partial Success (Expected in some environments)
```
⚠️  Some integration tests failed.
Tests passed: 3/4
  ⚠️  Database Integration (connection not available)
  ✅ Excel Integration
  ⚠️  SOAP Integration (zeep compatibility issue)
  ✅ Service Integration
```

### Common Issues and Solutions

**Database Connection Errors:**
- Expected in test environments without MySQL setup
- Tests will skip database operations but still validate model imports
- Solution: Set up MySQL with proper credentials or accept skipped tests

**SOAP/zeep Import Errors:**
- Common in Python 3.13 due to removed cgi module
- Tests will skip SOAP operations but validate through mocking
- Solution: Use Python 3.11/3.12 or accept mocked testing

**File Permission Errors (Windows):**
- Excel files may be locked by antivirus or other processes
- Tests include retry logic and graceful cleanup
- Solution: Temporary, tests will eventually succeed

## Integration with CI/CD

The integration tests are designed to work in various environments:

1. **Development Environment**: Full testing with real database and services
2. **CI Environment**: Graceful degradation with mocking and skipping
3. **Production Environment**: Should not be run in production

## Future Improvements

1. **Database Testing**: Add Docker-based MySQL for consistent test database
2. **SOAP Testing**: Update to zeep-compatible Python version or alternative SOAP library
3. **Performance Testing**: Add timing and performance validation
4. **Coverage Reporting**: Add code coverage metrics for integration tests

## Troubleshooting

### Test Failures
1. Check database connectivity and credentials
2. Verify all required Python packages are installed
3. Ensure temporary directory permissions are correct
4. Check for conflicting processes using test files

### Environment Issues
1. Python version compatibility (3.11-3.12 recommended)
2. Package version conflicts (check requirements.txt)
3. Operating system specific issues (Windows file locking)

### Debug Mode
Run tests with verbose output to see detailed error messages:
```bash
python -m pytest tests/test_integration.py -v -s --tb=long
```