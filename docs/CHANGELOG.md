# `clientity` -- changelog

## [0.1.8] -- Mar. 13th, 2026

### Added
+ **Descriptor-based `Bound[B, R]`**: `Bound` now inherits from `typical.Descriptor[B, R]`, carrying return type `R` as a second generic parameter for IDE inference
+ **`__client.Contract`**: Runtime-checkable protocol base for typed client contracts (`ct.client.Contract`)
+ **`__client.Factory[P]`**: Reusable typed client factory via `ct.client.factory(Contract)` 
+ **`__client.typed()`**: Static cast utility for casting clients to typed contracts without `type: ignore` in user code
+ **`client()` overloads**: `ct.client(interface, Contract)` returns the contract type directly for one-off typed creation
+ **`Descriptor[B, R]` base in `typical`**: Generic descriptor with `__get__`, `__set_name__`, `__access__` machinery — `Bound` inherits from it

### Changed
* **`Bound` generic signature**: `Bound[B]` → `Bound[B, R]`, all references updated (`WrappedEndpoint`, `Binds`, `__wrap`, `bound()`)
* **`Client.__matmul__`**: Returns `t.Self` for type preservation through `@` chaining
* **`Endpoint` TYPE_CHECKING stubs**: `__rshift__` now uses overloads to capture `R` from `t.Type[R]`, other operators return `Bound['Endpoint', t.Any]`
* **`Requesting`/`Responding` hint unions**: Updated in prior version, confirmed working with new `Bound[B, R]`

### Confirmed
* **Protocol-based contracts provide full IDE inference**: Return types, parameter signatures (user-declared), and attribute visibility all resolve correctly via `t.Protocol` contracts
* **Three typed client creation paths verified**: contract arg, factory, and `typed()` cast — all produce correct Pyright inference

---

## Current Agenda

### Immediate
1. Wire `__execute` refactor with directive detection in `http.py` (verify status)
2. Integration test directives through full pipeline
3. Clean up `type: ignore` sites (`Bound.__access__` return, `Client.__matmul__` Self return)

### Hinting Roadmap
- Phase 0: ✅ `Bound[B, R]` carries return type
- Phase 1: ✅ Protocol contracts give full return type inference
- Phase 2: ✅ `client()` overloads + `typed()` + `Factory` remove `type: ignore` from user code
- Phase 3: Free via user-declared Protocol signatures
- Phase 4: Subclass / declaration DSL (deferred)

### Pinned for Later
1. `Bound.__access__` return type — currently `type: ignore`, needs proper typing for descriptor instance access resolving to callable
2. Namespace factory tuple/subscript unpacking
3. `Payload`/`Query` field lists
4. Excess positional → payload resolution
5. Approach B protocol migration for directives
6. Logging throughout directives module

## [0.1.7] -- Mar. 9th, 2026

### Added
+ **Directives system**: Lightweight alternatives to full model classes for query/body/response handling
  - `Query`: Query param directive (field list support stubbed for later)
  - `Payload`: Body directive with key override (`payload['data']`)
  - `Unwrap`: Response extraction with method access (`.json`, `.text`, `.bytes`), path traversal (`['data']['items']`), and callable pipeline support
  - `Directive` protocol and `Specs` stubs for future expansion
  - Module-level singletons: `ct.query`, `ct.payload`, `ct.unwrap`
+ **No-paren grouping factories**: `ct.resource @ "users"` and `ct.namespace @ "https://api.com"` via `__matmul__` on factory objects
+ **Top-level method shortcuts**: `ct.get`, `ct.post`, `ct.put`, `ct.patch`, `ct.delete`, `ct.head`, `ct.options` as aliases
+ **Top-level aliases**: `ct.rs`, `ct.ns`, `ct.ep`

### Changed
* **`__execute` refactored**: Extracted `__query`, `__body`, `__response` methods to eliminate if/elif chains in `__call__`
* **`Requesting`/`Responding` type hints**: Now include `Payload`, `Query`, `Unwrap` in their unions for proper IDE support

### Confirmed
* **Pathless endpoints already work**: `ct.get << Model >> Response` (no `@ ""` needed) confirmed functional

---

## Current Agenda

### Immediate
1. Wire `__execute.__query`, `__execute.__body`, `__execute.__response` with directive detection (partially implemented)
2. Integration test directives through full Client → Adapter → Response pipeline
3. Hinting / IDE compliance improvements

### Pinned for Later
1. `Payload` field lists and typed fields (`payload['data', ['id', 'cat']]`, `payload[{'id': int}]`)
2. `Query` field lists (`query['q', 'limit']`)
3. `Namespace` factory tuple/subscript unpacking (`ct.namespace[httpx.AsyncClient] @ "base"`)
4. Approach B migration (unified `Requesting`/`Responding` protocols) if directive surface grows
5. Excess positional → payload resolution after path claims
6. Built-in utilities suite (cross-cutting, tiered)


## [0.1.6] -- Jan. 6th, 2026

### Added
+ **Execution utilities**: `http.execute` and `http.respond` extracted from Client/Namespace
+ **`groupings()` iterator**: On `Grouping` base class for iterating nested Resource/Namespace
+ **Integration test suite**: Full flow tests for Client → Resource → Namespace → Endpoint

### Changed
* **Operator mappings**: `%` for query model, `&` for prehook, `|` for posthook (precedence fix)
* **Phantom types for DX**: Operators return `Bound[Endpoint]` to type checkers via `TYPE_CHECKING` block
* **`embody()` fallback**: Now calls `dictate()` for unknown object types

### Fixed
* `Resource.__nest__` / `Namespace.__nest__` double-prepend bug (strips child location prefix)
* `Client.__sourced` nested grouping re-nesting (bypass `__setattr__` with `object.__setattr__`)
* `Grouping.__setattr__` changed `if` to `elif` for Grouping check
* Various type hints: `Stringable` for URL params, `respond` overloads, `AsyncInterface` return types

---

## Current Agenda

### Immediate
1. Revisit DX typing for nested resource/namespace attribute access (`client.users.list` shows `Any`)

### Pinned for Later
1. IDE typing / signatures (`Unpack[TypedDict]` for kwargs autocomplete)
2. Iterable response models
3. WebSocket clients
4. CLI generation

## [0.1.5] -- Jan. 4th, 2026

### Added
+ **Grouping system**: Base `Grouping` class for organizing endpoints
  - `Resource`: Dependent grouping with relative `location`, prepends path to nested endpoints
  - `Namespace`: Independent grouping with absolute `base`, optional own `interface`/`adapter`
  - Nested resource support with `__nest__` and `Located` protocol
  - `endpoints()` iterator utility on base `Grouping`

+ **Adapters**: Library-specific request building and sending
  - `Adapter` ABC with `build()` and `send()` methods
  - `RequestsAdapter` for `requests` library
  - `HttpxAdapter` for `httpx` library  
  - `AiohttpAdapter` for `aiohttp` library (fire-and-forget or session reuse modes)
  - `adapt()` factory function with `Compatible()` detection

+ **Utilities**:
  - `synced`: Inverse of `asynced` - wraps async callables to sync with `eval` option
  - `dictate`: Extract dict from model instances (pydantic, dataclass, etc.)
  - `sift.instructions()`: Convenience method for sifting with `Instructions`
  - `domain()`: Extract domain name from URL
  - `bound()`: Moved to utils/typers.py

+ **Type hints**:
  - `Located` protocol for objects with `location` attribute
  - `Requested` hint for embody input
  - `Responded` hint for execution return type
  - `WrappedEndpoint` = `Union[Endpoint, Bound[Endpoint]]`

### Changed
* `Location.__new__`: Now idempotent - returns existing Location unchanged
* `Location.name`: Property returning PascalCase name from path segments (excluding params)
* `Endpoint.mutate()`: Public method exposing `__copy` for modification
* `Client.__init__`: Now accepts `Interfacing` (interface or callable returning interface)
* `embody()`: Parameter type changed from `Requesting` to `Optional[Requested]`

### Fixed
* `synced`/`asynced` overload signatures for proper type inference
* Name mangling issues with abstract methods (`__wrap__` -> `__wrap__`)

---

## Current Agenda

### Immediate
1. Update `Client` to handle `Resource` and `Namespace` assignment in `__setattr__`
2. Extract shared execution logic from `Client.__x` and `Namespace.__x` into utility
3. Test full flow: Client -> Resource -> Endpoint -> execution

### Pending
- IDE typing / signatures (`Unpack[TypedDict]` for kwargs autocomplete)
- `domain()` utility implementation (currently raises)

### Pinned for Later
1. **Iterable response models**: Handle `list[Item]` responses, sequence parsing, `__responds__` for collections
2. **WebSocket clients**: Different protocol handling, maybe `ws_endpoint` or separate client type
3. **CLI generation**: `clientity generate --source /path/to/spec --destination /path/to/client.py` from OpenAPI/FastAPI/Flask specs

---

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
