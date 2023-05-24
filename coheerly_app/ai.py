import os
from langchain.document_loaders import PyPDFDirectoryLoader
import weaviate
from PySide2.QtCore import Slot


class SmartDoc:

    @Slot()
    def __init__(self, path=r'/Users/connordaly/papers') -> None:
        self.path = path
        loader = PyPDFDirectoryLoader(self.path)
        docs = loader.load()
        self.client = weaviate.Client(
            url="https://paper-summarizer-z7q6am1u.weaviate.network",
            additional_headers={
                # Replace with your API key
                os.environ['OPEN_AI_API_KEY'],

            }
        )

        query = """{
                    Aggregate {
                    GoodDocument (groupBy: ["file"]){
                    groupedBy {
                        value
                    } meta {
                        count
                    }
                    }
                }
                }"""
        result = self.client.query.raw(query)
        existing_files = set([x['groupedBy']['value']
                             for x in result['data']['Aggregate']['GoodDocument']])

        # class_obj = {
        #     "class": "GoodDocument",
        #     "vectorizer": "text2vec-openai",
        #     "moduleConfig": {
        #         "generative-openai": {
        #             "model": "gpt-3.5-turbo"
        #         }
        #     }
        # }

        # self.client.schema.create_class(class_obj)
        unloaded_docs = [
            doc for doc in self.docs if doc.metadata['source'] not in existing_files]
        with self.client.batch as batch:
            batch.batch_size = 50
            # Batch import all Questions
            for i, doc in enumerate(unloaded_docs):
                print(f"importing document: {i+1}")

                properties = {
                    "page_content": doc.page_content,
                    "file": doc.metadata['source'],
                    "page_number": doc.metadata['page']
                }

                self.client.batch.add_data_object(properties, "GoodDocument")

    def get_result(self, generatePrompt, source='/Users/connordaly/papers/perceiver.pdf'):
        where_filter = {
            "path": ["file"],
            "operator": "Equal",
            "valueString": source
        }
        return (
            self.client.query
            .get("GoodDocument", ["file", "page_content", "page_number"])
            .with_generate(grouped_task=generatePrompt)
            .with_where(where_filter)
            .with_limit(2)
        ).do()
