import xml.etree.ElementTree as ET

root = ET.parse("out.xml")


for record in root.findall(f".//http://www.openarchives.org/OAI/2.0/"):
    metadata = record.find()

