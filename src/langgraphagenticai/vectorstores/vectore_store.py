from chromadb import PersistentClient, EmbeddingFunction, Embeddings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from typing import List
import json


MODEL_NAME = 'dunzhang/stella_en_1.5B_v5'
DB_PATH = './.chroma_db'
FAQ_FILE_PATH= './data/FAQ.json'
INVENTORY_FILE_PATH = './data/inventory.json'

class Product:
    def __init__(self, name: str, id: str, description: str, type: str, price: float, quantity: int):
        self.name = name
        self.id = id
        self.description = description
        self.type = type
        self.price = price
        self.quantity = quantity

class QuestionAnswerPairs:
    def __init__(self, question: str, answer: str):
        self.question = question
        self.answer = answer

class CustomEmbeddingClass(EmbeddingFunction):
    def __init__(self, model_name):
        self.embedding_model = HuggingFaceEmbedding(model_name=MODEL_NAME)

    def __call__(self, input_texts: List[str]) -> Embeddings:
        return [self.embedding_model.get_text_embedding(text) for text in input_texts]

class FAQCollection:
    def __init__(self):
        self.documents = []
        self.ids = []
        self.metadatas = []

    def add(self, documents, ids, metadatas):
        self.documents.extend(documents)
        self.ids.extend(ids)
        self.metadatas.extend(metadatas)

    def display(self):
        for doc, id_, meta in zip(self.documents, self.ids, self.metadatas):
            print(f"ID: {id_}, Document: {doc}, Metadata: {meta}")

# Define the InventoryCollection class
class InventoryCollection:
    def __init__(self):
        self.documents = []
        self.ids = []
        self.metadatas = []

    def add(self, documents, ids, metadatas):
        self.documents.extend(documents)
        self.ids.extend(ids)
        self.metadatas.extend(metadatas)

    def display(self):
        for doc, id_, meta in zip(self.documents, self.ids, self.metadatas):
            print(f"ID: {id_}, Document: {doc}, Metadata: {meta}")




class FlowerShopVectorStore:
    def __init__(self):
        db = PersistentClient(path=DB_PATH)

        custom_embedding_function = CustomEmbeddingClass(MODEL_NAME)

        self.faq_collection = db.get_or_create_collection(name='FAQ', embedding_function=custom_embedding_function)
        self.inventory_collection = db.get_or_create_collection(name='Inventory', embedding_function=custom_embedding_function)

        if self.faq_collection.count() == 0:
            try :
                self._load_faq_collection(FAQ_FILE_PATH)
            except Exception as e:
                raise ValueError(e)
                

        if self.inventory_collection.count() == 0:
            self._load_inventory_collection(INVENTORY_FILE_PATH)

    def _load_faq_collection(self, faq_file_path: str):
        try:
            
            with open(faq_file_path, 'r') as f:
                faqs = json.load(f)
                
            # Create an instance of FAQCollection
            obj_faq_collection = FAQCollection()

            obj_faq_collection.add(
                documents=[faq['question'] for faq in faqs] + [faq['answer'] for faq in faqs],
                ids=[str(i) for i in range(0, 2*len(faqs))],
                metadatas = faqs + faqs
            )
            self.faq_collection = obj_faq_collection
        except Exception as ex:
            raise ValueError(ex)

    def _load_inventory_collection(self, inventory_file_path: str):
        with open(inventory_file_path, 'r') as f:
            inventories = json.load(f)
            
        # Create an instance of InventoryCollection
        obj_inventory_collection = InventoryCollection()

        obj_inventory_collection.add(
            documents=[inventory['description'] for inventory in inventories],
            ids=[str(i) for i in range(0, len(inventories))],
            metadatas = inventories
        )
        self.inventory_collection = obj_inventory_collection

    def query_faqs(self, query: str): 
        return self.faq_collection.query(query_texts=[query], n_results=5)
    
    def query_inventories(self, query: str):
        return self.inventory_collection.query(query_texts=[query], n_results=5)