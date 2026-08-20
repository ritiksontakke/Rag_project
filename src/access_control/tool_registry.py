from src.tools.delete_document import delete_document
from src.tools.get_document import get_document
from src.tools.list_documents import list_documents
from src.tools.search_documents import search_documents
from src.tools.update_document import update_document
from src.tools.upload_document import upload_document

ALL_TOOLS = {
    delete_document.name : delete_document,
    get_document.name : get_document,
    list_documents.name : list_documents,
    search_documents.name : search_documents,
    update_document.name : update_document,
    upload_document.name : upload_document
}

print(ALL_TOOLS.keys())