# `clientity` -- changelog

## [0.1.0] -- Dec. 29, 2025
* Initial project scaffolding and core primitives

### Added
+ **Project Structure**: Established base package layout with `core/`, `exc/`, and logging infrastructure
+ **Logging**: Configurable logging via `CLIENTITYLOGS` environment variable with `devnull` fallback
+ **Exceptions**: Base `ClientityError` exception class

+ **Protocols**:
  - `SyncInterface` / `AsyncInterface`: Runtime-checkable protocols for HTTP engines (requests, httpx, aiohttp, etc.)
  - `Requestable`: Protocol for request models with `__request__()` method and optional `RequestKey` class var
  - `Responsive`: Protocol for response models with `__respond__()` classmethod

+ **Primitives**:
  - `Location`: Path fragment class with parameter extraction (`{id}`), `/` operator for joining, and `resolve()` for substitution
  - `URL`: Full URL class combining base + location, with `resolve()` for final string output
  - `MethodType`: Literal type for HTTP methods with constants (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`)
  - `Hooks`: Container for pre/post request hooks with async conversion via `before`/`after` properties
  - `Instructions`: Core instruction set containing method, location, hooks, and models (querying, requesting, responding) with `merge()` and `prepend()` methods

+ **Endpoint**:
  - `Endpoint`: Builder class for constructing `Instructions` via method chaining
  - `endpoint` factory with method-specific properties (`.get`, `.post`, `.put`, etc.)
  - Operator overloads: `@` (location), `|` (hooks), `<<` (request models), `>>` (response model)

+ **Utilities**:
  - `asynced`: Utility for wrapping sync callables as async
  - `embody`: Utility for encoding request objects to `(key, data)` tuples

### Architecture
+ **Reverse-cascade design**: Endpoints return instruction sets that bubble up to client for execution
+ **Engine agnostic**: Interface protocols accept any HTTP library that quacks correctly
+ **Sift pattern** (pending): kwargs distributed to path/query/body based on model field introspection

## [0.0.0] -- Dec. 28, 2025
* Project Initialized
