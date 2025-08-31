# Database Setup and Migration Guide

This document explains how to set up and manage the IntelliTrust database using Alembic.

## Database Configuration

The application uses PostgreSQL as the database. The connection details are:

- **Host**: localhost
- **Port**: 5432
- **Database**: intellitrust
- **User**: postgres
- **Password**: 1234
- **URL**: `postgresql://postgres:1234@localhost:5432/intellitrust`

## Initial Setup

### 1. Install PostgreSQL

If you haven't installed PostgreSQL yet:

```bash
# On macOS with Homebrew
brew install postgresql@14
brew services start postgresql@14
```

### 2. Create Database and User

```bash
# Connect to PostgreSQL as superuser
psql -h localhost -p 5432 -U startechnologiesinc -d postgres

# Create user and database
CREATE USER postgres WITH PASSWORD '1234' CREATEDB;
CREATE DATABASE intellitrust OWNER postgres;
\q
```

### 3. Initialize Alembic

Alembic is already initialized in this project. The configuration files are:

- `alembic.ini` - Main configuration file
- `migrations/env.py` - Environment configuration
- `migrations/versions/` - Migration files directory

## Managing Migrations

### Using the Helper Script

We provide a convenient helper script `migrate.py` for managing migrations:

```bash
# Show current migration
python migrate.py current

# Create a new migration
python migrate.py create "Add new feature"

# Apply all pending migrations
python migrate.py upgrade

# Rollback last migration
python migrate.py downgrade

# Show migration history
python migrate.py history
```

### Using Alembic Directly

You can also use Alembic commands directly:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1

# Show current status
alembic current

# Show history
alembic history
```

## Database Models

The application includes the following models:

### Core Models
- **User** - User accounts with roles (ADMIN, ISSUER, HOLDER, VERIFIER)
- **Organization** - Organizations that can issue credentials
- **Document** - Digital documents with versions and metadata
- **Credential** - Verifiable credentials
- **Verification** - Document and credential verification records

### Supporting Models
- **DocumentVersion** - Version history for documents
- **DocumentMetadata** - Metadata for documents
- **CredentialType** - Types of credentials that can be issued
- **VerificationLog** - Log of verification activities
- **BlockchainTransaction** - Blockchain transaction records
- **AIAnalysis** - AI analysis results for documents
- **AIAnalysisResult** - Detailed AI analysis results

## Migration Workflow

### 1. Making Model Changes

When you modify the SQLAlchemy models:

1. Update the model files in `app/models/`
2. Create a new migration: `python migrate.py create "Description"`
3. Review the generated migration file
4. Apply the migration: `python migrate.py upgrade`

### 2. Reviewing Migrations

Always review generated migrations before applying them:

```bash
# Show migration details
python migrate.py show <revision_id>
```

### 3. Testing Migrations

Test migrations in development before applying to production:

```bash
# Create a test database
createdb intellitrust_test

# Apply migrations to test database
DATABASE_URL=postgresql://postgres:1234@localhost:5432/intellitrust_test alembic upgrade head
```

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Ensure PostgreSQL is running: `brew services list | grep postgresql`
   - Check connection details in `alembic.ini`

2. **Import Errors**
   - Ensure virtual environment is activated: `source venv/bin/activate`
   - Check that all dependencies are installed: `pip install -r requirements.txt`

3. **Migration Conflicts**
   - If migrations conflict, you may need to reset the database
   - Drop and recreate the database, then reapply migrations

### Resetting Database

If you need to reset the database:

```bash
# Drop and recreate database
dropdb intellitrust
createdb intellitrust

# Reapply all migrations
python migrate.py upgrade
```

## Production Considerations

For production deployment:

1. **Environment Variables**: Use environment variables for database credentials
2. **Backup Strategy**: Implement regular database backups
3. **Migration Testing**: Always test migrations in staging environment
4. **Rollback Plan**: Have a plan for rolling back problematic migrations

## Useful Commands

```bash
# Check database connection
psql -h localhost -p 5432 -U postgres -d intellitrust -c "SELECT version();"

# List all tables
psql -h localhost -p 5432 -U postgres -d intellitrust -c "\dt"

# Check Alembic version
psql -h localhost -p 5432 -U postgres -d intellitrust -c "SELECT * FROM alembic_version;"
```
