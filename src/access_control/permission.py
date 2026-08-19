ROLE_TOOLS = {
    "employee": [
        "search_documents",
        "get_document",
        "get_document_metadata",
    ],

    "manager": [
        "search_documents",
        "get_document",
        "get_document_metadata",
        "upload_document",
    ],

    "admin": [
        "search_documents",
        "get_document",
        "get_document_metadata",
        "upload_document",
        "delete_document",
        "reindex_document",
    ],
}