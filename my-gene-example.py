import requests
import json
import argparse

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Process some integers.")

    # Add arguments
    parser.add_argument('gene', type=str, help='The gene to get info from')

    # Parse the arguments
    args = parser.parse_args()

    
    print(f"Getting info for gene: {args.gene}")



    # Query the MyGene.info API
    response = requests.get(f"https://mygene.info/v3/query?q={args.gene}&fields=genomic_pos&species=human")
    data = response.json()

    #print (data)

    hits = data['hits']
    first_hit = hits[0]
    genomic_pos = first_hit['genomic_pos']
    chromosome = genomic_pos['chr']
    start = genomic_pos['start']
    end = genomic_pos['end']

    print ("The gene " + args.gene + " is locared on Chromosome " + str(chromosome) + ", starts at " + str(start) + " and ends at ", str(end))


if __name__ == "__main__":
    main()