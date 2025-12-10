from itemadapter import ItemAdapter

class OllamaSummarizationPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if not adapter.get('description'):
            adapter['summary'] = "Không có mô tả để tóm tắt."
        return item