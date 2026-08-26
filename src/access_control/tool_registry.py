from src.tools.delete_document import delete_document
from src.tools.get_document import get_document
from src.tools.list_documents import list_documents
from src.tools.search_documents import search_documents
from src.tools.upload_document import upload_document
from src.tools.external_search import external_search

ALL_TOOLS = {
    delete_document.name : delete_document,
    get_document.name : get_document,
    list_documents.name : list_documents,
    search_documents.name : search_documents,
    external_search.name : external_search,
    upload_document.name : upload_document
}

print(ALL_TOOLS.keys())