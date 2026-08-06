import pandas as pd
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import OWL, RDF, XSD

# 1. Load existing ontology graph
g = Graph()
g.parse("ontology_development_week3_updated.ttl", format="ttl")

NS = Namespace(
    "http://www.semanticweb.org/fatos/ontologies/2026/7/ontology_development_week3/"
)
excel_path = (
    "../materials/Week 2/Dataset 1_ Fatos Rama/DS1_SMT_2020_Model_Data_-_HVLM.xlsx"
)

# 2. Define Data Property Mappings for Breakdown
# Mapping format: 'Excel Column Name': ('OntologyPropertyName', XSD_Datatype)
bd_property_mappings = {
    "DOWN TYPE": ("hasDownType", XSD.string),
    "TTF DISTRIBUTION": ("hasTTFDistribution", XSD.string),
    "MTTF": ("hasMTTF", XSD.float),
    "MTTF UNITS": ("hasMTTFUnits", XSD.string),
    "TTR DISTRIBUTION": ("hasTTRDistribution", XSD.string),
    "MTTR": ("hasMTTR", XSD.float),
    "MTTR UNITS": ("hasMTTRUnits", XSD.string),
    "FIRST ONE AT DISTRIBUTION": ("hasFirstOneAtDistribution", XSD.string),
    "FOA": ("hasFOA", XSD.float),  # Reused from PM
    "FOA UNITS": ("hasFOAUnits", XSD.string),  # Reused from PM
}

# 3. Declare all data properties explicitly as owl:DatatypeProperty
for prop_name, _ in bd_property_mappings.values():
    g.add((NS[prop_name], RDF.type, OWL.DatatypeProperty))

# 4. Load and Process the Breakdown sheet
df_bd = pd.read_excel(excel_path, sheet_name="Breakdown")

for _, row in df_bd.iterrows():
    # Use DOWN EVENT NAME as the individual URI
    bd_uri = NS[str(row["DOWN EVENT NAME"])]

    # Iterate over columns and add datatype assertions
    for col_name, (prop_name, xsd_type) in bd_property_mappings.items():
        val = row.get(col_name)
        if pd.notna(val):
            typed_val = float(val) if xsd_type == XSD.float else str(val)
            g.add((bd_uri, NS[prop_name], Literal(typed_val, datatype=xsd_type)))

# 5. Save updated ontology graph
output_file = "ontology_development_week3_updated2.ttl"
g.serialize(output_file, format="ttl")
print(f"Breakdown data successfully mapped and saved to {output_file}!")