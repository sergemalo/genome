import requests
import copy

class SNPDetails:
    def __init__(self, gene, name,snp_id):
        self.gene = gene
        self.name = name
        self.snp_id = snp_id


# A query is a list of strings
# fields is a list of queries

# My Variant will return a list of hists.
# Each hit might contain our fields.

# Example SNP identifier
snp_id = "rs1801133"
#snp_id = "rs2151655"

class Query:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields


queries = []

query = Query("gene", ["dbsnp", "gene", "symbol"])
queries.append(copy.deepcopy(query))

query = Query("consequence", ["cadd", "consequence"])
queries.append(copy.deepcopy(query))

query = Query("impact", ["snpeff", "ann", "putative_impact"])
queries.append(copy.deepcopy(query))



# Query the MyVariant.info API
#response = requests.get(f"https://myvariant.info/v1/variant/{snp_id}")
#response = requests.get(f"https://myvariant.info/v1/variant/query?q={snp_id}&fields=dbsnp.gene.symbol")
fields = "fields=" + queries[0].fields[0]
for f in queries[0].fields[1:]:
    fields = fields + "." + f
for q in queries[1:]:
    fields = fields + "," + q.fields[0]
    for f in q.fields[1:]:
        fields = fields + "." + f
    
print("Fields: " + fields)    
response = requests.get(f"https://myvariant.info/v1/variant/query?q={snp_id}&{fields}")
data = response.json()


print(data)
print("")

def get_query_results(hit, query):
    results = []
    print ("CUR = " + query[0])
    if query[0] in hit:


        if len(query) == 1:
            if isinstance(hit[query[0]], list):
                print("FINAL - LIST")
                for r in hit[query[0]]:
                    results.append(copy.deepcopy(r))
            else:
                results.append(copy.deepcopy(hit[query[0]]))
        else:
            if isinstance(hit[query[0]], list):
                print("LIST")
                for r in hit[query[0]]:
                    results.extend(copy.deepcopy(get_query_results(r, query[1:])))
            else:
                print("NOT LIST")
                results.extend(copy.deepcopy(get_query_results(hit[query[0]], query[1:])))
    return results


for hit in data['hits']:
    for query in queries:

        results = get_query_results(hit, query.fields)

        print("RESULTS: " + query.name + " = " + str(results))
