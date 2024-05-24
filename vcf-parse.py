import vcfpy
from bioservices import Ensembl

# Initialize the Ensembl service
ensembl = Ensembl()

# Open the VCF file
reader = vcfpy.Reader.from_path('ST-Small.vcf')

count = 0

# Iterate through each record in the VCF file
for record in reader:
    if count >= 10:
        break
    chrom = record.CHROM
    pos = record.POS
    id = record.ID
    ref = record.REF
    alt = record.ALT[0]  # Assuming a single ALT allele
    
    #variant_id = f"{chrom}:{pos}_{ref}/{alt}"
    #print(f"SNP: {variant_id}")
    variant_id = str(id)
    print("SNP: ", variant_id)
    
    response = ensembl.get_vep_by_id(variant_id, "human")
    print (response)
    
    # Process the response to get gene information
    #for consequence in response:
    #    gene_name = consequence.get('gene_symbol')
    #    impact = consequence.get('impact')
    #    print(f"SNP: {variant_id} | Gene: {gene_name} | Impact: {impact}")

    count += 1    
