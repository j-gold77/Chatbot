import pandas as pd

catalogPath = "./opendata/CATALOG.csv"
openCatalogPath = "./opendata/CU_SR_OPEN_DATA_CATALOG.csv"
openCatalogDescPath = "./opendata/CU_SR_OPEN_DATA_CATALOG_DESC.csv"

catalog = pd.read_csv(catalogPath, header=0)
openCatalog = pd.read_csv(openCatalogPath, header=0, encoding='unicode_escape')
openCatalogDesc = pd.read_csv(
    openCatalogDescPath, header=0, encoding='unicode_escape')

# merge description with open catalog
openDataDesc = pd.merge(openCatalog, openCatalogDesc,
                        on='Course ID', how='left')

# only use relevant columns from catalog
catalogFiltered = catalog[["Key", "Faculty", "Department", "Program", "Degree",
                          "Subject", "Catalog", "Website"]]

# merge open catalog + catalog
dataSet = pd.merge(openDataDesc, catalogFiltered, on=[
                   'Subject', 'Catalog'], how='left')

# used only to visualize the data set, can be removed before submission
dataSet.to_csv("./opendata/output.csv")
