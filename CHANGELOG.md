# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0-beta.1] - 2025-11-24

### Added
- 🚀 **Project scaffolding** with `crudfull new`
  - Support for SQL (PostgreSQL), MongoDB, and Ghost (in-memory) databases
  - Optional Docker support with `--docker` flag
  - Docker dev environment for rapid development
  - Automatic generation of `pytest.ini` for async tests

- 🏗️ **CRUD resource generation** with `crudfull generate resource`
  - Modular architecture (schemas, models, service, router)
  - Auto-registration of routers in `main.py`
  - Automatic test generation for each resource
  - Support for field types: `str`, `int`, `float`, `bool`, `datetime`, `uuid`
  - Optional fields with `?` suffix

- 🔐 **JWT Authentication** with `crudfull add auth`
  - Complete auth module with register, login, and me endpoints
  - Automatic test generation for auth endpoints
  - Auto-registration of auth router
  - Compatible with SQL and MongoDB

- 🛡️ **Route protection** with `crudfull protect`
  - Protect routes by action (list, create, read, update, delete, all)
  - Protect specific functions with `--func` option
  - Automatic injection of authentication dependencies

- ⚙️ **Utilities**
  - `crudfull sync-routers run` - Sync all routers with main.py
  - `crudfull version show` - Display version
  - Context-aware CLI (detects `crudfull.json`)

- 📦 **Installation options**
  - Full installation with all dependencies
  - Lite installation (`crudfull[lite]`) - CLI only
  - Test tools (`crudfull[test]`) - pytest and httpx
  - Auth dependencies (`crudfull[auth]`) - JWT and password hashing

### Fixed
- ✅ Pydantic 2.12+ compatibility with `ConfigDict`
- ✅ SQLAlchemy 2.0 compatibility with proper `declarative_base` import
- ✅ Conditional imports in auth schemas (SQL vs MongoDB)
- ✅ Bcrypt version pinned to 4.0.1 for passlib compatibility
- ✅ Async test configuration with pytest

### Documentation
- 📚 Complete README with examples
- 📚 Installation instructions for different use cases
- 📚 CLI command reference
- 📚 Testing guide with PYTHONPATH instructions
- 🎨 Professional logo and branding

[0.1.0-beta.1]: https://github.com/matiasvagli/crudfull/releases/tag/v0.1.0-beta.1
