# SENTENSI Blocking Engine

A standalone content moderation and blocking engine built with Django and GraphQL.

The Blocking Engine receives user-generated content, sends it through a detection component, applies predefined blocking rules, and produces a final `ALLOW` or `BLOCK` decision.

The detection model is intentionally separated from the Blocking Engine so that an external ML model can be integrated later without changing the core blocking workflow.

---

## Features

* Content validation
* Detection service abstraction
* Offensive-content blocking
* Safe-content allowance
* Detection confidence validation
* Blocking decision persistence
* GraphQL API
* Controlled error handling
* Application logging
* Environment-based configuration
* Automated testing
* Separation of API, business logic, detection, and persistence

---

## Architecture

```text
User / Frontend
       │
       ▼
   GraphQL API
       │
       ▼
 BlockingService
       │
       ├── Validate Content
       │
       ▼
 DetectionService
       │
       │ Detection Result
       │ { label, confidence }
       ▼
 BlockingRules
       │
    ┌──┴───┐
    │      │
  ALLOW   BLOCK
    │      │
    └──┬───┘
       ▼
 DecisionService
       │
       ▼
    Database
```

---

## Project Structure

```text
SENTENSI_BLOCKING_ENGINEE/
│
├── venv/
│
├── src/
│   │
│   ├── Manager/
│   │   └── Manage.py
│   │
│   └── BlockingEngine/
│       │
│       ├── Config/
│       │   ├── __init__.py
│       │   ├── Settings.py
│       │   ├── Urls.py
│       │   ├── Asgi.py
│       │   └── Wsgi.py
│       │
│       ├── Blocking/
│       │   ├── __init__.py
│       │   ├── Apps.py
│       │   ├── Admin.py
│       │   ├── models/
│       │   │   ├── __init__.py
│       │   │   └── BlockingDecision.py
│       │   ├── migrations/
│       │   └── Tests/
│       │       ├── __init__.py
│       │       └── testBlockingEngine.py
│       │
│       ├── Services/
│       │   ├── __init__.py
│       │   ├── BlockingService.py
│       │   ├── DetectionService.py
│       │   └── DecisionService.py
│       │
│       ├── Rules/
│       │   ├── __init__.py
│       │   └── BlockingRules.py
│       │
│       ├── GraphQL/
│       │   ├── __init__.py
│       │   ├── Schema.py
│       │   ├── Queries.py
│       │   ├── Mutations.py
│       │   └── Types.py
│       │
│       └── Core/
│           ├── __init__.py
│           ├── Constants.py
│           ├── Exceptions.py
│           └── Responses.py
│
├── .env
├── .env.example
├── .gitignore
└── README.md
```

---

## Technology Stack

* Python 3.12+
* Django 6.1
* Graphene
* Graphene-Django
* GraphQL
* Django ORM
* SQLite for current development
* python-dotenv

---

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd SENTENSI_BLOCKING_ENGINEE
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install django==6.1 graphene graphene-django python-dotenv
```

### 5. Configure Environment Variables

Create the environment file:

```bash
cp .env.example .env
```

Configure the required values inside `.env`.

### 6. Run Migrations

```bash
python src/Manager/Manage.py migrate
```

### 7. Check the Project

```bash
python src/Manager/Manage.py check
```

---

## Running the Server

Start the Django development server:

```bash
python src/Manager/Manage.py runserver
```

The GraphQL API will be available at:

```text
http://127.0.0.1:8000/graphql/
```

GraphiQL is enabled for development and testing.

---

## GraphQL API

### Health Check

Use the following query:

```graphql
query {
  health
}
```

Expected response:

```json
{
  "data": {
    "health": "Blocking Engine is running"
  }
}
```

---

## Evaluate Content

The Blocking Engine exposes a GraphQL mutation for evaluating submitted content.

```graphql
mutation {
  evaluateContent(content: "Hello world") {
    id
    content
    allowed
    action
    reason
    confidence
  }
}
```

Example response:

```json
{
  "data": {
    "evaluateContent": {
      "id": "1",
      "content": "Hello world",
      "allowed": true,
      "action": "ALLOW",
      "reason": "SAFE_CONTENT",
      "confidence": 1.0
    }
  }
}
```

For offensive content, the expected decision is:

```json
{
  "allowed": false,
  "action": "BLOCK",
  "reason": "OFFENSIVE_CONTENT"
}
```

---

## Detection Contract

The detection component communicates with the Blocking Engine using a defined contract.

A valid detection result contains:

```python
{
    "label": "safe",
    "confidence": 0.97
}
```

or:

```python
{
    "label": "offensive",
    "confidence": 0.94
}
```

### Supported Labels

```text
safe
offensive
```

### Confidence

Confidence must be a numeric value between:

```text
0.0 and 1.0
```

Invalid detection results are rejected before reaching the blocking rules.

This protects the Blocking Engine from malformed or unexpected output from the detection component.

---

## Blocking Rules

The current business rules are:

```text
Detection Result
       │
       ├── safe
       │     │
       │     ▼
       │   ALLOW
       │
       └── offensive
             │
             ▼
           BLOCK
```

The detection component identifies the content.

The Blocking Engine determines what action should be taken.

This separation allows the ML model to evolve independently from the blocking logic.

---

## Services

### BlockingService

`BlockingService` coordinates the complete blocking workflow.

Responsibilities:

1. Validate submitted content.
2. Request a detection result.
3. Apply blocking rules.
4. Save the final decision.
5. Return the normalized result.

---

### DetectionService

`DetectionService` defines the boundary between the Blocking Engine and the detection model.

The current implementation is a temporary detector used for development and testing.

The production ML model can replace this implementation later without requiring changes to the GraphQL layer or blocking rules.

---

### DecisionService

`DecisionService` handles persistence of completed blocking decisions.

Database operations are isolated inside this service so that the rest of the engine does not directly depend on Django ORM operations.

---

### BlockingRules

`BlockingRules` contains the business logic that converts detection results into final actions.

Example:

```text
safe       → ALLOW
offensive  → BLOCK
```

---

## Data Model

The engine stores completed decisions using the `BlockingDecision` model.

A decision contains:

* ID
* Content
* Action
* Reason
* Confidence
* Creation timestamp

Supported actions:

```text
ALLOW
BLOCK
```

Supported reasons:

```text
SAFE_CONTENT
OFFENSIVE_CONTENT
UNKNOWN
```

---

## Error Handling

The engine uses domain-specific exceptions:

```text
BlockingEngineError
├── InvalidContentError
└── DetectionError
```

### InvalidContentError

Used when submitted content does not satisfy the engine's input requirements.

Examples:

* Empty content
* Whitespace-only content
* Non-string content

### DetectionError

Used when the detection component returns an invalid result or fails to produce a valid detection result.

Examples:

* Missing required fields
* Unsupported detection label
* Invalid confidence value
* Non-numeric confidence
* Confidence outside the `0.0 - 1.0` range

---

## Security

The engine includes several security-focused configurations:

* Environment-based secret configuration
* `DEBUG` controlled through environment variables
* Explicit allowed hosts
* CSRF middleware
* `X-Frame-Options`
* Content-type sniffing protection
* Referrer policy configuration
* Controlled domain-specific errors
* No user-generated content written to application logs

---

## Environment Variables

The project uses environment variables for configuration.

Example:

```env
DJANGO_SECRET_KEY=
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=
```

The `.env` file must not be committed to Git.

Use `.env.example` as the configuration template.

---

## Logging

Application logging is configured through Django's logging system.

The engine records operational events such as:

* Detection failures
* Completed content evaluations
* Blocking decisions

User-submitted content is intentionally not written into application logs.

This reduces the risk of exposing private or sensitive messages through log files.

---

## Testing

Run the Blocking Engine tests using:

```bash
python src/Manager/Manage.py test BlockingEngine.Blocking.Tests.testBlockingEngine
```

The test suite covers:

* Safe content
* Offensive content
* Blocking decisions
* Decision persistence
* Empty content
* Whitespace-only content
* Invalid content types
* Valid detection results
* Missing detection fields
* Unsupported detection labels
* Confidence values above `1.0`
* Negative confidence values
* Boolean confidence values

Current test status:

```text
Found 13 test(s).

Ran 13 tests

OK
```

---

## ML Model Integration

The ML model is not implemented inside this project.

The Blocking Engine provides a clear integration boundary through:

```text
src/BlockingEngine/Services/DetectionService.py
```

The future ML model only needs to return a valid detection result:

```python
{
    "label": "safe",
    "confidence": 0.95
}
```

or:

```python
{
    "label": "offensive",
    "confidence": 0.95
}
```

The Blocking Engine does not need to know how the ML model performs its prediction internally.

This allows the ML component to be developed independently.

---

## Integration Flow

The intended integration with the larger Sentensi Safi platform is:

```text
Sentensi Safi Frontend
        │
        ▼
Friend's Backend
        │
        │ Submit Message
        ▼
Blocking Engine
        │
        ▼
Detection Model
        │
        ▼
Detection Result
        │
        ▼
Blocking Rules
        │
     ┌──┴──┐
     │     │
   ALLOW  BLOCK
     │     │
     ▼     X
Message   Message
continues rejected
```

The Blocking Engine is designed as an independent component so it can be integrated with the existing backend later without coupling its internal implementation to that backend.

---

## Development Status

### Completed

* [x] Django project setup
* [x] Standalone Blocking Engine architecture
* [x] Blocking decision model
* [x] Detection service boundary
* [x] Blocking rules
* [x] Decision service
* [x] GraphQL API
* [x] Input validation
* [x] Error handling
* [x] Security configuration
* [x] Environment configuration
* [x] Application logging
* [x] Automated tests
* [x] 13 tests passing

### Future Work

* [ ] Integrate production ML detection model
* [ ] Connect with Sentensi Safi backend that has other backend features
* [ ] Add production authentication/authorization integration
* [ ] Production database configuration
* [ ] Production deployment configuration
* [ ] API documentation expansion

---

## Design Principles

The Blocking Engine follows separation of responsibilities.

```text
GraphQL
   │
   ▼
API Boundary
   │
   ▼
BlockingService
   │
   ▼
Workflow Orchestration
   │
   ▼
DetectionService
   │
   ▼
ML Detection Boundary
   │
   ▼
BlockingRules
   │
   ▼
Business Decision
   │
   ▼
DecisionService
   │
   ▼
Persistence
```

Each component has a specific responsibility and can be modified independently.

The architecture is intentionally designed to make future ML and backend integration easier while keeping the Blocking Engine maintainable and testable.

---

## License

This project is currently developed as part of the Sentensi Safi system.

