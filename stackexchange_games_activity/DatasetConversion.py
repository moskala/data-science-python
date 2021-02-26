import xml.etree.ElementTree as ET
import pandas as pd
import os


def xml2csv(fname, delcols=[]):
    """
    Funkcja konwertuje oryginalne zbiory XML na CSV.
    Źródło: http://www.gagolewski.com/resources/data/travel_stackexchange_com/readme.txt
    """
    tree = ET.parse(fname)
    root = tree.getroot()
    d = pd.DataFrame([e.attrib for e in root])
    for name in delcols: del d[name]
    d.to_csv(fname + ".csv", index=False)


def generate_all_csv(folder):
    """
    Funkcja zapisuje wszystkie osiem tabel z podanego folderu w formacie csv.
    """
    xml2csv(os.path.join(folder, "Badges.xml"))
    xml2csv(os.path.join(folder, "PostLinks.xml"))
    xml2csv(os.path.join(folder, "Posts.xml"), ["Body", "Tags", "OwnerDisplayName", "LastEditorDisplayName"])
    xml2csv(os.path.join(folder, "Tags.xml"))
    xml2csv(os.path.join(folder, "Users.xml"), ["AboutMe", "WebsiteUrl", "ProfileImageUrl"])
    xml2csv(os.path.join(folder, "Votes.xml"))
    xml2csv(os.path.join(folder, "Comments.xml"), ["Text", "UserDisplayName"])
    xml2csv(os.path.join(folder, "PostHistory.xml"))