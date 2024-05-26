import vcfpy
import requests
import json
import argparse
from datetime import datetime


class GenePos:
    def __init__(self, chr, start, end):
        self.chr = chr
        self.start = start
        self.end = end

class SNPInfo:
    def __init__(self, variant_id, alt, quality):
        self.variant_id = variant_id
        self.alt = alt
        self.quality = quality
        

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

    print ("CHR:" + chr_name + ", S=" + str(start_pos) + " E=" + str(end_pos) + " Number of records: ", reader.parsed_samples)
    reader.fetch(chr_name, start_pos, end_pos)
    #reader.fetch("chr1", 11785723, 11806455)

    count = 0

    # Iterate through each record in the VCF file
    for record in reader:

        snp_idx = 0
        for id in record.ID:
            print("SNP: ", record.ID[snp_idx])
            print("SNP: ", record.ALT[snp_idx])
            print("SNP: ", record.QUAL)
        
            snp_info = SNPInfo(record.ID[snp_idx], record.ALT[snp_idx], record.QUAL)
            snp_list.append(snp_info)

            snp_idx = snp_idx + 1

    return snp_list

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

    print ("Number of SNPs," + str(len(snp_list)))
    print("SNP,Alt,Quality")
    for snp in snp_list:
        #print (snp.variant_id + "," + snp.alt + "," + str(snp.quality))
        print (snp.variant_id+ "," + str(snp.alt) + "," + str(snp.quality))

if __name__ == "__main__":
    main()