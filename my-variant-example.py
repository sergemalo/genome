import requests

# Example SNP identifier
snp_id = "RS1801133"

# Query the MyVariant.info API
response = requests.get(f"https://myvariant.info/v1/variant/{snp_id}")
data = response.json()

# Extract gene information
#gene = data.get('gene', {}).get('symbol')
#print(f"SNP: {snp_id} | Gene: {gene}")

print (data)