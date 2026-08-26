# Multi-Model RAG API

A FastAPI-based company knowledge assistant that combines role-based access control, LangChain agents, PostgreSQL user management, Qdrant vector search, Hugging Face embeddings, OpenAI generation, and Langfuse prompt/trace management.

## Live Demo

<a href="https://multi-model-rag-frontend.netlify.app/" target="_blank">
  🚀 Open Multi-Model RAG
</a>

## Features

- User signup and OAuth2-style login with JWT access tokens.
- Role-based document permissions for `employee`, `manager`, and `admin`.
- Department-level isolation for document access.
- PDF document upload and ingestion.
- Document search, retrieval, listing, viewing, updating, and deletion.
- Agent-based orchestration with:
  - Orchestrator Agent
  - Knowledge Base Agent
  - Document Management Agent
  - Upload Agent
- RAG pipeline using:
  - PyPDFLoader for PDF loading
  - Custom document chunking
  - `BAAI/bge-small-en-v1.5` embeddings
  - Qdrant for vector storage and similarity search
  - OpenAI chat model for answer generation
- Relevance filtering with a configured retrieval threshold.
- Langfuse callback tracing for API agent calls.

## Architecture

```text
Client
  |
  v
FastAPI
  |
  +--> /api/v1/auth
  |       |
  |       +--> UserService / AuthService
  |       +--> PostgreSQL
  |       +--> JWT
  |
  +--> /api/v1/documents/upload
  |       |
  |       v
  |   Orchestrator Agent
  |       |
  |       v
  |   Upload Agent
  |       |
  |       v
  |   upload_document
  |       |
  |       v
  |   Ingestion Pipeline
  |       |
  |       +--> PDF Loader
  |       +--> Chunker
  |       +--> Hugging Face Embeddings
  |       +--> Qdrant
  |
  +--> /api/v1/knowledge/ask
          |
          v
      Orchestrator Agent
          |
          +--> Knowledge Base Agent
          |       |
          |       v
          |   search_documents
          |       |
          |       v
          |   Retrieval Pipeline
          |       |
          |       +--> Embedding
          |       +--> Qdrant Search
          |       +--> Department Filter
          |       +--> Relevance Threshold
          |
          +--> Document Management Agent
                  |
                  +--> get_document
                  +--> list_documents
                  +--> search_documents
                  +--> delete_document
```

## Project Structure

```text
ritiksontakke-multi-model-rag/
├── requirements.txt
├── test.py
└── src/
    ├── main.py
    ├── access_control/
    │   ├── permission.py
    │   ├── permission_manager.py
    │   └── tool_registry.py
    ├── agents/
    │   ├── document_management_agent.py
    │   ├── knowledge_agent.py
    │   ├── Orchestrator_Agent.py
    │   └── upload_agent.py
    ├── api/v1/
    │   ├── auth.py
    │   ├── documents.py
    │   └── knowledge.py
    ├── auth/
    │   ├── auth_handler.py
    │   └── oauth.py
    ├── core/
    │   └── config.py
    ├── db/
    │   ├── base.py
    │   ├── database.py
    │   ├── init_db.py
    │   └── session.py
    ├── models/
    │   └── user.py
    ├── rag/
    │   ├── generation/
    │   ├── ingestion/
    │   └── retrieval/
    ├── repositories/
    │   └── user_repository.py
    ├── schemas/
    │   └── user_schemas.py
    ├── services/
    │   ├── auth_service.py
    │   └── user_service.py
    ├── tools/
    │   ├── delete_document.py
    │   ├── get_document.py
    │   ├── list_documents.py
    │   ├── search_documents.py
    │   └── upload_document.py
    └── utils/
        ├── model.py
        └── password.py
```

## Technology Stack

| Component | Technology |
|---|---|
| API | FastAPI |
| ASGI server | Uvicorn |
| Validation | Pydantic |
| Agent framework | LangChain |
| LLM | OpenAI via `langchain-openai` |
| Embeddings | Hugging Face `BAAI/bge-small-en-v1.5` |
| Vector database | Qdrant |
| Relational database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | JWT / OAuth2 password flow |
| Password hashing | pwdlib |
| PDF loading | LangChain PyPDFLoader |
| Observability | Langfuse |

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file with your PostgreSQL, Qdrant, OpenAI, JWT, and Langfuse credentials.

### 3. Start the project

```bash
uvicorn src.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

### Useful Commands

```bash
# Start API
uvicorn src.main:app --reload

# Run password test
python test.py
```

## API Endpoints

### Authentication

#### Signup

```http
POST /api/v1/auth/signup
```

Request body:

```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "department": "engineering"
}
```

New users are registered with the `employee` role by the current implementation.

#### Login

```http
POST /api/v1/auth/login
```

The endpoint uses `OAuth2PasswordRequestForm`, so send:

```text
username=<email>
password=<password>
```

The response contains a bearer access token.

### Document Upload

```http
POST /api/v1/documents/upload
```

Form fields:

- `department`
- `file`

The uploaded file must be a PDF.

Only `admin` and `manager` users can upload documents, and the department must match the authenticated user's department.

### Knowledge Query

```http
POST /api/v1/knowledge/ask
```

Request body:

```json
{
  "query": "What is the company's leave policy?"
}
```

The authenticated user's department is passed into the agent context and used to isolate knowledge-base retrieval.

## Roles and Permissions

| Operation | Employee | Manager | Admin |
|---|:---:|:---:|:---:|
| Search documents | Yes | Yes | Yes |
| Get document | Yes | Yes | Yes |
| List documents | No | Yes | Yes |
| Upload document | No | Yes | Yes |
| Update document | No | Yes | Yes |
| Delete document | No | Yes | Yes |

The implementation performs permission checks both when selecting tools for agents and inside sensitive document tools.

## RAG Pipeline

### Ingestion

The document ingestion flow is:

```text
PDF
  -> PyPDFLoader
  -> Document chunks
  -> BAAI/bge-small-en-v1.5 embeddings
  -> Qdrant
```

Each stored Qdrant point includes metadata such as:

- department
- uploaded_by
- content
- page
- chunk_index
- source

The Qdrant collection is named:

```text
company_documents
```

The configured vector size is:

```text
384
```

and cosine distance is used.

### Retrieval

The retrieval flow is:

```text
User Query
  -> Embedding
  -> Qdrant similarity search
  -> Department filter
  -> Relevance threshold
  -> Relevant document chunks
```

The retrieval threshold is currently:

```text
0.65
```

### Generation

The generator builds a context from retrieved document content and instructs the model to answer using only that context.

If the answer is not present in the supplied context, the generation prompt instructs the model to state that the information is not available in company documents.

## Agent Architecture

### Orchestrator Agent

The orchestrator is created with the following tools:

- `documentManagmentAgent`
- `knowledgeBaseAgent`
- `uploadDocumentAgent`

Its system prompt is loaded through Langfuse when available.

### Knowledge Base Agent

The Knowledge Base Agent is designed to:

1. Call `search_documents` for every knowledge question.
2. Use only retrieved content.
3. Avoid hallucinating or adding outside knowledge.
4. Preserve the language of the retrieved content.
5. Return a fallback when relevant information cannot be found.

### Document Management Agent

This agent routes document-management requests to the appropriate authorized tool.

Supported operations include:

- Get
- List
- Search
- Upload
- Update
- Delete

### Upload Agent

The Upload Agent is restricted to PDF upload operations and uses the `upload_document` tool after role validation.

## Security Model

The application uses several layers of access control.

### Authentication

JWT access tokens are created after successful login and expire after 12 hours.

### Role Authorization

Sensitive operations require:

```text
admin
manager
```

Employees are restricted from document listing, upload, update, and deletion.

### Department Isolation

Document retrieval is filtered by the authenticated user's department. Upload, update, and delete operations also verify department ownership.

### File Validation

The document upload API currently accepts only files whose content type is:

```text
application/pdf
```

## Database

PostgreSQL stores application users.

The `users` table contains:

- `id`
- `full_name`
- `email`
- `password_hash`
- `role`
- `department`

SQLAlchemy is used as the ORM.

## Qdrant

The application creates the `company_documents` collection during startup if it does not already exist.

Payload indexes are created for:

- `department`
- `source`

These fields support department isolation and source-based document operations.

## Testing

The repository currently contains a small `test.py` script for checking password hashing:

```bash
python test.py
```

The supplied project does not currently include a comprehensive automated API/integration test suite.

## Example Workflow

### 1. Register

Create an account through:

```text
POST /api/v1/auth/signup
```

### 2. Login

Authenticate through:

```text
POST /api/v1/auth/login
```

Save the returned bearer token.

### 3. Upload a PDF

Using a manager/admin account:

```text
POST /api/v1/documents/upload
```

Provide the user's department and PDF file.

### 4. Ask a Knowledge Question

Send:

```text
POST /api/v1/knowledge/ask
```

with a query such as:

```json
{
  "query": "What information is available in the uploaded document?"
}
```

The system retrieves relevant chunks only from the authenticated user's department and generates an answer from the retrieved context.

## Important Implementation Notes

- The application expects external PostgreSQL and Qdrant services.
- Environment variables are loaded with `python-dotenv`.
- The OpenAI model configured in the supplied code is `gpt-5.4-nano`.
- The embedding model is `BAAI/bge-small-en-v1.5`.
- Langfuse is used for prompt retrieval and tracing.
- Temporary PDF files created by the upload endpoint are cleaned up after processing.
- The supplied source contains some debug `print()` statements that may be better replaced with structured logging for production.
- The current `UserContext` schema appears twice in `src/schemas/user_schemas.py`; the later definition adds `file_path`.

## Production Recommendations

Before deploying to production, consider:

- Add a proper automated test suite for authentication, RBAC, department isolation, ingestion, retrieval, and document CRUD.
- Add database migrations, such as Alembic, instead of relying only on `create_all()`.
- Move secrets entirely to a secure secret manager.
- Replace debug prints with structured application logging.
- Add request size limits and stronger upload validation.
- Add rate limiting for authentication and knowledge endpoints.
- Validate and sanitize document/source identifiers consistently.
- Add pagination for large document listings and document retrieval.
- Add monitoring and error tracking around Qdrant, PostgreSQL, OpenAI, and Langfuse.
- Review Qdrant index creation so startup is idempotent with the deployed Qdrant version.
- Add explicit CORS configuration if the API will be called from a browser frontend.
- Pin dependency versions in `requirements.txt` for reproducible deployments.

## License

No license is specified in the supplied project. Add an appropriate license before distributing the repository.
