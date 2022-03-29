# class HashPipeline:
#     def process_item(self, item, spider):
#         hash_id = hash(frozenset(item.items()))
#         item['offer_id'] = hash_id
#         return item