-- Database initialization script
-- This script is run when the PostgreSQL container is first created

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for additional crypto functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create initial database user if needed (already created by POSTGRES_USER env var)
-- The database itself is created by POSTGRES_DB env var

-- Set default timezone
SET timezone = 'UTC';

-- Create a schema for the application (optional, using public schema by default)
-- CREATE SCHEMA IF NOT EXISTS adminory;

-- Note: Actual table creation will be handled by Alembic migrations
-- This file is primarily for database initialization and extensions
