import pandas as pd
from rdflib import Graph, Namespace, Literal, RDF, OWL
from rdflib.namespace import XSD

# 1. Configuration & File Paths
ttl_file = "ontology_development_week3_patched.ttl"
output_file = "ontology_development_week3_updated4.ttl"
excel_file = "../materials/Week 2/Dataset 1_ Fatos Rama/DS1_SMT_2020_Model_Data_-_HVLM.xlsx"

# 2. Load the RDF Graph
g = Graph()
g.parse(ttl_file, format="turtle")

# Define your ontology namespace
ns1 = Namespace("http://www.semanticweb.org/fatos/ontologies/2026/7/ontology_development_week3/")
g.bind("ns1", ns1)

# 3. Define the list of target properties and explicitly declare them as DatatypeProperties
# This prevents them from being treated/created as annotation properties.
data_properties = [
    ns1.hasToolGroupLocation,
    ns1.hasDispatchingStrategy,
    ns1.hasRanking1,
    ns1.hasRanking2,
    ns1.hasRanking3,
    ns1.hasToolWakeUpRanking
]

for prop in data_properties:
    # Ensure each property is typed as an OWL DatatypeProperty (avoiding duplication)
    g.add((prop, RDF.type, OWL.DatatypeProperty))

# 4. Load the Toolgroups sheet from the Excel datasheet
df = pd.read_excel(excel_file, sheet_name="Toolgroups")
print(f"Processing {len(df)} toolgroups from the datasheet...")

# 5. Iterate and assign data property values to Tool_Group individuals
for _, row in df.iterrows():
    tg_name = str(row["TOOLGROUP"]).strip()
    if not tg_name or pd.isna(tg_name):
        continue

    # Construct the individual URI
    tg_uri = ns1[tg_name]

    # Helper function to cleanly assign string data properties without duplicating statements
    def assign_data_property(prop_uri, value):
        if pd.notna(value) and str(value).strip() != "":
            clean_value = str(value).strip()
            # Remove any existing value to prevent duplicates on re-runs
            g.remove((tg_uri, prop_uri, None))
            # Add the new literal with explicit string datatype
            g.add((tg_uri, prop_uri, Literal(clean_value, datatype=XSD.string)))

    # Map Excel columns to ontology data properties
    assign_data_property(ns1.hasToolGroupLocation, row.get("TOOLGROUPLOCATION"))
    assign_data_property(ns1.hasDispatchingStrategy, row.get("DISPATCHING"))
    assign_data_property(ns1.hasRanking1, row.get("Ranking 1"))
    assign_data_property(ns1.hasRanking2, row.get("Ranking 2"))
    assign_data_property(ns1.hasRanking3, row.get("Ranking 3"))
    assign_data_property(ns1.hasToolWakeUpRanking, row.get("TOOL WAKE UP Ranking"))

# 6. Serialize and save the updated ontology
g.serialize(destination=output_file, format="turtle")
print(f"Success! Updated ontology saved to '{output_file}' with proper Data Property assertions.")