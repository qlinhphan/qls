import pymongo

def mongodb(address):
    myclient = pymongo.MongoClient(address)
    mydb = myclient["app"]
    mycol = mydb["rag"]
    return mycol

def save_data_mongodb(list_path_file, load_data, mycol, get_embedding):
    name_docs = []
    attentions = []
    content_table = []
    for i in range(len(list_path_file)):
        chunks = load_data(file_name=list_path_file[i])
        chunks = [chunks[i] for i in range(len(chunks)) if len(chunks[i][0]) > 0]
        # print(chunks)
        # name_docs.append(chunks[0][0])
        name_docs.append(list_path_file[i].split("/")[-1])
        attentions.append(chunks[-1][0])
        content = chunks[2 : len(chunks) - 1]

        data_need = []
        for cont in content:
            table = {}
            table['DẤU HIỆU LÂM SÀNG GỢI Ý'] = cont[1]
            table['PHƯƠNG PHÁP'] = cont[2]
            table['GHI CHÚ'] = cont[3]
            data_need.append(table)
        content_table.append(data_need)
        

            # break
    # print(name_docs) #6
    # print(attentions) #6
    # print(content_table) #6  

    for nd, a , ct in zip(name_docs, attentions, content_table):
        for c in ct:
            save = {}
            save["name_doc"] = nd
            save['content'] = 'DẤU HIỆU LÂM SÀNG GỢI Ý: '+ c['DẤU HIỆU LÂM SÀNG GỢI Ý'] + ", " + 'PHƯƠNG PHÁP: ' + c['PHƯƠNG PHÁP'] + ", " + 'GHI CHÚ: ' + c['GHI CHÚ'] +", " + 'LƯU Ý: ' + a
            save["vector"] = get_embedding(save['content'])
            mycol.insert_one(save)

    print("saved knowledge into db successfully!!!")

if __name__ == "__main__":
    mycol = mongodb()