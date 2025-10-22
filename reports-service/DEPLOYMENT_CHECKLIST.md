# Deployment Checklist

## Pre-Deployment Checklist

### System Requirements
- [ ] Python 3.9-3.12 installed (avoid 3.13 for now)
- [ ] MySQL 5.7+ or 8.0+ available
- [ ] Minimum 512MB RAM available
- [ ] 100MB+ disk space for Excel files
- [ ] Network access to SOAP service (https://soap-applatest.onrender.com)

### Environment Setup
- [ ] `.env` file created and configured
- [ ] `DATABASE_URL` updated with correct MySQL credentials
- [ ] `JWT_SECRET_KEY` changed from default value
- [ ] `CORS_ORIGINS` configured for your domains
- [ ] `EXCEL_STORAGE_PATH` directory exists and is writable

### Database Setup
- [ ] MySQL server is running
- [ ] Database `ong_management` exists
- [ ] Required tables exist (usuarios, donaciones, eventos)
- [ ] Database user has appropriate permissions
- [ ] Connection test successful

### Dependencies
- [ ] Python virtual environment created (recommended)
- [ ] All requirements installed (`pip install -r requirements.txt`)
- [ ] No import errors when running `python validate_system.py`

### Directory Structure
- [ ] `storage/excel` directory exists
- [ ] `logs` directory exists (optional)
- [ ] Appropriate file permissions set

## Deployment Steps

### 1. Quick Installation (Automated)
```bash
# Linux/Mac
./install.sh

# Windows
install.bat
```

### 2. Manual Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Create directories
mkdir -p storage/excel logs

# Validate installation
python validate_system.py
```

### 3. Configuration Validation
```bash
# Test basic functionality
python validate_system.py

# Test service startup (quick test)
python -c "from src.config import settings; print('Config loaded successfully')"
```

### 4. Service Startup
```bash
# Development mode
python start.py --mode dev

# Production mode
python start.py --mode prod

# Simple mode (fallback)
python start.py --mode simple
```

## Post-Deployment Verification

### Health Checks
- [ ] Service starts without errors
- [ ] Health endpoint responds: `GET http://localhost:8000/health`
- [ ] API documentation accessible: `http://localhost:8000/docs`
- [ ] GraphQL endpoint accessible: `http://localhost:8000/api/graphql`

### Functional Tests
- [ ] Database connection working
- [ ] GraphQL queries execute successfully
- [ ] REST endpoints respond correctly
- [ ] Excel export functionality works
- [ ] SOAP client can connect (if service is available)

### Integration Tests
- [ ] API Gateway routes configured (if applicable)
- [ ] Frontend components can connect
- [ ] Authentication/authorization working
- [ ] CORS headers configured correctly

## Production Deployment

### Security Checklist
- [ ] `JWT_SECRET_KEY` is a secure, unique value
- [ ] `DEBUG=false` in production
- [ ] CORS origins restricted to production domains
- [ ] Database credentials are secure
- [ ] HTTPS enabled (if applicable)
- [ ] Firewall rules configured

### Performance Configuration
- [ ] `WORKERS` set appropriately (typically 2-4)
- [ ] `DATABASE_POOL_SIZE` configured for load
- [ ] `MAX_CONCURRENT_REQUESTS` set appropriately
- [ ] Excel file cleanup scheduled

### Monitoring Setup
- [ ] Log files location configured
- [ ] Log rotation configured
- [ ] Health check monitoring enabled
- [ ] Error alerting configured (optional)

## Docker Deployment (Optional)

### Docker Setup
- [ ] Dockerfile builds successfully
- [ ] Docker Compose configuration updated
- [ ] Environment variables passed correctly
- [ ] Volumes mounted for persistent storage
- [ ] Network configuration correct

### Docker Commands
```bash
# Build image
docker build -t reports-service .

# Run with docker-compose
docker-compose -f docker-compose.reports.yml up -d

# Check logs
docker logs ong_reports_service

# Health check
docker exec ong_reports_service curl -f http://localhost:8000/health
```

## Integration with Existing System

### API Gateway Integration
- [ ] Routes added to API Gateway:
  - `/api/graphql` → reports-service:8000/api/graphql
  - `/api/reports/*` → reports-service:8000/api/reports/*
  - `/api/filters/*` → reports-service:8000/api/filters/*
  - `/api/network/*` → reports-service:8000/api/network/*
- [ ] Authentication middleware configured
- [ ] CORS headers properly forwarded

### Frontend Integration
- [ ] New routes added to React Router:
  - `/reports/donations`
  - `/reports/events`
  - `/network/consultation`
- [ ] Apollo Client configured for GraphQL
- [ ] Navigation menu updated
- [ ] Components properly integrated

### Database Integration
- [ ] New tables created:
  - `filtros_guardados`
  - `archivos_excel`
- [ ] Existing tables accessible
- [ ] Proper foreign key relationships

## Troubleshooting

### Common Issues
- [ ] **Port 8000 already in use**: Change PORT in .env or stop conflicting service
- [ ] **Database connection failed**: Check DATABASE_URL, MySQL service, credentials
- [ ] **Import errors**: Check Python version (3.9-3.12), reinstall requirements
- [ ] **Permission denied on storage**: Check directory permissions, create if missing
- [ ] **SOAP timeout**: Check network connectivity, increase SOAP_TIMEOUT

### Diagnostic Commands
```bash
# Check service status
curl http://localhost:8000/health

# Check logs
tail -f logs/reports-service.log

# Test database connection
python -c "from src.utils.database_utils import check_database_health; print(check_database_health())"

# Validate system
python validate_system.py

# Check Python version
python --version
```

## Rollback Plan

### If Deployment Fails
1. Stop the reports service
2. Restore previous configuration
3. Check logs for error details
4. Fix issues and redeploy
5. Verify integration points still work

### Database Rollback
1. Drop new tables if needed:
   ```sql
   DROP TABLE IF EXISTS archivos_excel;
   DROP TABLE IF EXISTS filtros_guardados;
   ```
2. Restore database backup if necessary

## Maintenance

### Regular Tasks
- [ ] Clean up expired Excel files (automatic)
- [ ] Monitor log file sizes
- [ ] Check for dependency updates
- [ ] Verify SOAP service connectivity
- [ ] Monitor database performance

### Update Process
1. Test updates in development environment
2. Backup current configuration
3. Update dependencies
4. Run validation tests
5. Deploy to production
6. Verify functionality

## Sign-off

### Development Team
- [ ] Code review completed
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Documentation updated

### Operations Team
- [ ] Infrastructure ready
- [ ] Monitoring configured
- [ ] Backup procedures in place
- [ ] Rollback plan tested

### Business Team
- [ ] User acceptance testing completed
- [ ] Training materials prepared
- [ ] Go-live communication sent

---

**Deployment Date**: ___________
**Deployed By**: ___________
**Version**: ___________
**Environment**: ___________