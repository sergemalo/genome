import requests
import json
import argparse


class GenePos:
    def __init__(self, chr, start, end):
        self.chr = chr
        self.start = start
        self.end = end


def get_gene_pos(gene_name):
    print(f"Getting info for gene: {gene_name}")

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

    print ("The gene " + gene_name + " is locared on Chromosome " + str(gp.chr) + ", starts at " + str(gp.start) + " and ends at ", str(gp.end))


def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Process some integers.")

    # Add arguments
    parser.add_argument('gene', type=str, help='The gene to get info from')

    # Parse the arguments
    args = parser.parse_args()

    gene_pos = get_gene_pos(args.gene)


if __name__ == "__main__":
    main()