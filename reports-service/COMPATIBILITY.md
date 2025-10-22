# Compatibility Notes

## Python Version Compatibility

### Current Status
The Reports Service has been tested and validated with the following Python versions:

- ✅ **Python 3.9**: Fully supported
- ✅ **Python 3.10**: Fully supported  
- ✅ **Python 3.11**: Fully supported
- ✅ **Python 3.12**: Fully supported
- ⚠️ **Python 3.13**: Limited support (see issues below)

### Python 3.13 Known Issues

#### Strawberry GraphQL Compatibility
- **Issue**: `ImportError: cannot import name '_create_fn' from 'dataclasses'`
- **Cause**: Strawberry GraphQL has compatibility issues with Python 3.13's updated dataclasses module
- **Status**: Upstream issue, waiting for Strawberry GraphQL update
- **Workaround**: Use Python 3.12 or earlier for full functionality

#### FastAPI Multipart
- **Issue**: `cgi` module deprecation warnings
- **Cause**: Python 3.13 deprecated the `cgi` module used by `python-multipart`
- **Status**: Non-blocking warnings, functionality works
- **Workaround**: Warnings can be ignored, or use Python 3.12

### Recommended Python Version

For production deployment, we recommend:
- **Python 3.11** or **Python 3.12** for optimal compatibility
- Avoid Python 3.13 until upstream dependencies are updated

### Dependency Version Constraints

The following dependencies have version constraints for compatibility:

```
strawberry-graphql[fastapi]>=0.215.1,<0.220.0
python-multipart>=0.0.6,<0.1.0
fastapi>=0.104.1,<0.110.0
```

### Testing Matrix

| Python Version | Core Services | GraphQL | REST API | SOAP Client | Status |
|----------------|---------------|---------|----------|-------------|---------|
| 3.9            | ✅            | ✅       | ✅        | ✅           | Full    |
| 3.10           | ✅            | ✅       | ✅        | ✅           | Full    |
| 3.11           | ✅            | ✅       | ✅        | ✅           | Full    |
| 3.12           | ✅            | ✅       | ✅        | ✅           | Full    |
| 3.13           | ✅            | ❌       | ⚠️        | ✅           | Limited |

### Migration Path for Python 3.13

When Python 3.13 support is needed:

1. **Monitor upstream dependencies**:
   - Strawberry GraphQL Python 3.13 support
   - FastAPI/python-multipart updates

2. **Update requirements.txt**:
   - Remove version constraints when compatible versions are available
   - Test thoroughly with new versions

3. **Update compatibility matrix**:
   - Update this document with new test results
   - Update CI/CD pipelines if applicable

### Development Recommendations

- **Local Development**: Use Python 3.11 or 3.12
- **Production**: Use Python 3.11 or 3.12
- **Docker**: Base images should use Python 3.12
- **CI/CD**: Test against Python 3.9, 3.10, 3.11, and 3.12

### Checking Your Python Version

```bash
python --version
# or
python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
```

### Installing Compatible Python Version

If you have Python 3.13 and need to use an earlier version:

#### Using pyenv (Linux/Mac)
```bash
pyenv install 3.12.0
pyenv local 3.12.0
```

#### Using conda
```bash
conda create -n reports-service python=3.12
conda activate reports-service
```

#### Using Docker
```bash
docker run -it python:3.12-slim bash
```

### Future Updates

This compatibility document will be updated as:
- New Python versions are released
- Dependency compatibility improves
- Issues are resolved upstream

Last updated: December 2024