import vcfpy
import requests
import re
import json
import argparse
import copy
from datetime import datetime

def stringify(s):
    if isinstance(s, str):
        return s.replace(",", ";")
    elif isinstance(s, list):
        return stringify('; '.join(s))
    else:
        return str(s)

class GenePos:
    def __init__(self, chr, start, end):
        self.chr = chr
        self.start = start
        self.end = end

class SNPInfo:
    def __init__(self, variant_id, reference, quality, snp_type, snp_value):
        self.variant_id = variant_id
        self.reference = reference
        self.quality = quality
        self.snp_type = snp_type
        self.snp_value = snp_value
        self.attributes = {}
        

class SNPQuery:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields


def get_gene_pos(gene_name):
    print(f"Gene,{gene_name}")

    # Query the MyGene.info API
    response = requests.get(f"https://mygene.info/v3/query?q={gene_name}&fields=genomic_pos&species=human")
    data = response.json()

    hits = data['hits']
    if len(hits) == 0:
        #print(f"Gene {gene_name} not found.")
        raise Exception("Gene not found")

    if len(hits) > 1:
        #print(f"Gene {gene_name} not found.")
        raise Exception("More than one gene found - Don't know which one to use.")

    first_hit = hits[0]
    genomic_pos = first_hit['genomic_pos']
    gp = GenePos(genomic_pos['chr'], genomic_pos['start'], genomic_pos['end'])

    #print ("The gene " + gene_name + " is locared on Chromosome " + str(gp.chr) + ", starts at " + str(gp.start) + " and ends at ", str(gp.end))
    print ("Chromosome," + str(gp.chr))
    print ("Start Position," + str(gp.start))
    print ("End Position," + str(gp.end))

    return gp

def get_snp_list(vcf, gene_pos):

    snp_list = []

    vcf_file = vcf + ".vcf.gz"
    print ("VCF File,", vcf)
    reader = vcfpy.Reader.from_path(vcf_file)

    recs = list(reader)

    # TODO: Find a way to look a bit before and after the gene
    #   I think that we have to find an exact SNP pos
    start_pos = max(gene_pos.start-1000, 0)
    end_pos = gene_pos.end+1000
    chr_name = "chr" + str(gene_pos.chr)
    #start_pos = gene_pos.start-1
    #end_pos = gene_pos.end

    #print ("CHR:" + chr_name + ", S=" + str(start_pos) + " E=" + str(end_pos) + " Number of records: ", reader.parsed_samples)
    reader.fetch(chr_name, start_pos, end_pos)
    #reader.fetch("chr1", 11785723, 11806455)

    pattern = re.compile(r"Substitution\(type_='(\w+)',\s*value='(\w+)'\)")

    # Iterate through each record in the VCF file
    for record in reader:
        snp_idx = 0
        for id in record.ID:
            #print("SNP: ", record.ID[snp_idx])
            #print("SNP: ", record.REF)
            #print("SNP: ", record.QUAL)
            #print("SNP: ", record.ALT[snp_idx])
        
            alt = str(record.ALT[snp_idx])
            # Search using the pattern
            match = pattern.search(alt)

            if match:
                snp_type = match.group(1)
                snp_value = match.group(2)
                #print("Type:", type_, "Value:", value_)

            else:
                print("Unable to parse alt:", alt)
                raise("Unable to parse alt")

            snp_info = SNPInfo(record.ID[snp_idx], record.REF, record.QUAL, snp_type, snp_value)
            snp_list.append(snp_info)

            snp_idx = snp_idx + 1

    return snp_list


def get_query_results(hit, query):
    results = []
    #print ("CUR = " + query[0])
    if query[0] in hit:

        if len(query) == 1:
            if isinstance(hit[query[0]], list):
                #print("FINAL - LIST")
                for r in hit[query[0]]:
                    results.append(copy.deepcopy(r))
            else:
                results.append(copy.deepcopy(hit[query[0]]))
        else:
            if isinstance(hit[query[0]], list):
                #print("LIST")
                for r in hit[query[0]]:
                    results.extend(copy.deepcopy(get_query_results(r, query[1:])))
            else:
                #print("NOT LIST")
                results.extend(copy.deepcopy(get_query_results(hit[query[0]], query[1:])))
    return results

def build_snp_queries():
    queries = []

    query = SNPQuery("gene", ["dbsnp", "gene", "symbol"])
    queries.append(copy.deepcopy(query))
    query = SNPQuery("consequence", ["cadd", "consequence"])
    queries.append(copy.deepcopy(query))
    query = SNPQuery("impact", ["snpeff", "ann", "putative_impact"])
    queries.append(copy.deepcopy(query))
    query = SNPQuery("descriptions", ["civic", "evidence_items", "description"])
    queries.append(copy.deepcopy(query))

    fields = "fields=" + queries[0].fields[0]
    for f in queries[0].fields[1:]:
        fields = fields + "." + f
    for q in queries[1:]:
        fields = fields + "," + q.fields[0]
        for f in q.fields[1:]:
            fields = fields + "." + f

    return queries, fields

def get_snp_details(snp_list):
    
    queries, fields = build_snp_queries()
    #print("Fields: " + fields)

    new_snp_list = []
    for snp in snp_list:
        cur_snp = snp

        response = requests.get(f"https://myvariant.info/v1/variant/query?q={snp.variant_id}&{fields}")
        data = response.json()


        for hit in data['hits']:
            for query in queries:
                results = get_query_results(hit, query.fields)
                #print("RESULTS: " + query.name + " = " + str(results))
                cur_snp.attributes['SubId'] = hit["_id"]
                cur_snp.attributes[query.name] = results
            new_snp_list.append(copy.deepcopy(cur_snp))

    return new_snp_list

def filter_snps(gene_name, snp_list):
    filtered_list = []

    for snp in snp_list:
        alt_len = len(snp.snp_value)
        sub_id_len = len(snp.attributes['SubId'])
        #if (gene_name in snp.attributes['gene']) and (snp.snp_value.lower() == snp.attributes['SubId'][sub_id_len-alt_len:sub_id_len-1].lower()):
        if (gene_name in snp.attributes['gene']):
            filtered_list.append(copy.deepcopy(snp))

    return filtered_list

def main():

    # Create the parser
    parser = argparse.ArgumentParser(description="Process some integers.")

    # Add arguments
    parser.add_argument('--gene', required=True, type=str, help='The gene to get info from')
    parser.add_argument('--vcf', required=True, type=str, help='The filename of the VCF file')

    # Parse the arguments
    args = parser.parse_args()


    print ("Script,gene-snp-info.py")
    print ("Version,1.0")
    print ("Format Version,1")
    current_date = datetime.now().strftime('%Y-%m-%d')
    print("Date," + current_date)


    gene_pos = get_gene_pos(args.gene)

    print("")
    snp_list = get_snp_list(args.vcf, gene_pos)
    snp_list = get_snp_details(snp_list)
    snp_list = filter_snps(args.gene, snp_list)

    print ("Number of SNPs," + str(len(snp_list)))
    snp_attributes = "SNP,REF,ALT,Quality,Type"
    for a in snp_list[0].attributes.keys():
        snp_attributes = snp_attributes + "," + a

    print(snp_attributes)
    for snp in snp_list:
        cur_snp_values = snp.variant_id + "," + snp.reference + "," + snp.snp_value + "," + stringify(snp.quality) + "," + snp.snp_type

        for a in snp.attributes.keys():
            cur_snp_values = cur_snp_values + "," + stringify(snp.attributes[a])

        print(cur_snp_values)

if __name__ == "__main__":
    main()