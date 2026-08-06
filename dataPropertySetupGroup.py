import pandas as pd
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import OWL, RDF, XSD

# 1. Load existing ontology graph
g = Graph()
g.parse("ontology_development_week3_with_step_properties.ttl", format="ttl")

NS = Namespace(
    "http://www.semanticweb.org/fatos/ontologies/2026/7/ontology_development_week3/"
)
excel_path = (
    "../materials/Week 2/Dataset 1_ Fatos Rama/DS1_SMT_2020_Model_Data_-_HVLM.xlsx"
)

# 2. Define Data Property Mappings for Setup / Setup_Group
# Format: 'OntologyPropertyName': (List of possible Excel Column Names, XSD_Datatype)
setup_property_mappings = {
    "hasSetupTime": (["SETUP TIME"], XSD.float),
    "hasSetupTimeUnits": (["ST UNITS"], XSD.string),
    "hasMinimalRunLength": (
        ["MINIMAL NUMBER OF RUNS", "MINMAL NUMBER OF RUNS"],
        XSD.integer,
    ),
    "hasSetupWhenCondition": (["WHEN"], XSD.string),
}

# 3. Declare all data properties explicitly as owl:DatatypeProperty
for prop_name, (_, _) in setup_property_mappings.items():
    g.add((NS[prop_name], RDF.type, OWL.DatatypeProperty))

# 4. Load and Process the Setups sheet (FIXED: sheet_name="Setups")
df_setup = pd.read_excel(excel_path, sheet_name="Setups")

for idx, row in df_setup.iterrows():
    # Construct individual URI dynamically based on available columns
    curr_setup = row.get("CURRENT SETUP")
    new_setup = row.get("NEW SETUP")
    setup_group = row.get("SETUP GROUP NAME")

    if pd.notna(curr_setup) and pd.notna(new_setup):
        setup_id = f"Setup_{curr_setup}_to_{new_setup}"
    elif pd.notna(setup_group) and pd.notna(new_setup):
        setup_id = f"Setup_{setup_group}_{new_setup}"
    elif pd.notna(new_setup):
        setup_id = f"Setup_{new_setup}"
    elif pd.notna(row.get("SETUP EVENT NAME")):
        setup_id = str(row.get("SETUP EVENT NAME"))
    else:
        setup_id = f"Setup_Event_{idx + 1}"

    setup_uri = NS[str(setup_id).strip().replace(" ", "_")]

    # Iterate over data property mappings and add RDF assertions
    for prop_name, (possible_cols, xsd_type) in setup_property_mappings.items():
        # Find the value from the first matching Excel column name
        val = None
        for col in possible_cols:
            if col in row and pd.notna(row[col]):
                val = row[col]
                break

        if val is not None:
            # Cast to the appropriate Python type
            try:
                if xsd_type == XSD.float:
                    typed_val = float(val)
                elif xsd_type == XSD.integer:
                    typed_val = int(val)
                else:
                    typed_val = str(val)

                g.add(
                    (
                        setup_uri,
                        NS[prop_name],
                        Literal(typed_val, datatype=xsd_type),
                    )
                )
            except (ValueError, TypeError):
                continue

# 5. Save updated ontology graph
output_file = "ontology_development_week3_updated5.ttl"
g.serialize(output_file, format="ttl")
print(f"Setups data successfully mapped and saved to {output_file}!")