import pandas as pd
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import OWL, RDF, XSD

# 1. Load existing ontology graph
g = Graph()
g.parse("ontology_development_week3_updated4.ttl", format="ttl")

NS = Namespace(
    "http://www.semanticweb.org/fatos/ontologies/2026/7/ontology_development_week3/"
)
excel_path = (
    "../materials/Week 2/Dataset 1_ Fatos Rama/DS1_SMT_2020_Model_Data_-_HVLM.xlsx"
)

# 2. Map Excel columns to property names and XSD datatypes
data_property_mappings = {
    "PM TYPE": ("hasPMType", XSD.string),
    "MTBeforePM": ("hasMTBeforePM", XSD.float),
    "MTBPM UNITS": ("hasMTBPMUnits", XSD.string),
    "TTR DISTRIBUTION": ("hasTTRDistribution", XSD.string),
    "MEAN": ("hasTTRMean", XSD.float),
    "OFFSET": ("hasTTROffset", XSD.float),
    "TTR UNITS": ("hasTTRUnits", XSD.string),
    "FIRST ONE AT DISTRIBUTION": ("hasFirstOneAtDistribution", XSD.string),
    "FOA": ("hasFOA", XSD.float),
    "FOA UNITS": ("hasFOAUnits", XSD.string),
}

# 3. Explicitly declare properties as owl:DatatypeProperty in the graph
for prop_name, _ in data_property_mappings.values():
    g.add((NS[prop_name], RDF.type, OWL.DatatypeProperty))

# 4. Process PM Sheet
df_pm = pd.read_excel(excel_path, sheet_name="PM")

for _, row in df_pm.iterrows():
    pm_uri = NS[str(row["PM EVENT NAME"])]

    for col_name, (prop_name, xsd_type) in data_property_mappings.items():
        val = row.get(col_name)
        if pd.notna(val):
            # Cast numeric types to float/int if required by XSD
            typed_val = float(val) if xsd_type == XSD.float else str(val)
            g.add((pm_uri, NS[prop_name], Literal(typed_val, datatype=xsd_type)))

# 5. Save updated ontology graph
g.serialize("ontology_development_week3_updated.ttl", format="ttl")
print("Data successfully mapped as DatatypeProperties and saved!")