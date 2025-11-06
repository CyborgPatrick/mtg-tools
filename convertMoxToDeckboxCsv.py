#!/usr/bin/env python3
import csv
import argparse
from decimal import Decimal, InvalidOperation

# --- CLI argument setup ---
parser = argparse.ArgumentParser(description="Convert and clean up a card inventory CSV file.")
parser.add_argument("input_file", help="Path to input CSV file")
parser.add_argument("output_file", help="Path to output CSV file")
args = parser.parse_args()

# Deckbox uses it's own codes for some sets
# Moxfield edition code to Deckbox edition code map
edition_code_map = {
    "PLST": "PLIST",
    "3ED": "3E",
    "F11": "FNMP",
    "MIR": "MI",
    "ICE": "IA",
    "ULG": "GU"
}

# Deckbox uses the Edition column to decide on which set the card is from not the Edition Code
# Moxfield does not export Set name
# Moxfield edition code to Deckbox Edition (set name) map 
edition_map = {
    'ISD': 'Innistrad',
    'INR': 'Innistrad Remastered',
    'CMM': 'Commander Masters',
    'BLC': 'Bloomburrow Commander',
    'TDM': 'Tarkir: Dragonstorm',
    'OTC': 'Outlaws of Thunder Junction Commander',
    'MH3': 'Modern Horizons 3',
    'M13': 'Magic 2013',
    'DSK': 'Duskmourn: House of Horror',
    'EOE': 'Edge of Eternities',
    'M3C': 'Modern Horizons 3 Commander',
    'TDC': 'Tarkir: Dragonstorm Commander',
    'AVR': 'Avacyn Restored',
    'MRD': 'Mirrodin',
    'LTR': 'The Lord of the Rings: Tales of Middle-earth',
    'ONE': 'Phyrexia: All Will Be One',
    'MKC': 'Murders at Karlov Manor Commander',
    'BLB': 'Bloomburrow',
    'EOC': 'Edge of Eternities Commander',
    'LTC': 'The Lord of the Rings: Tales of Middle-earth Commander',
    'C20': 'Commander 2020',
    'SLD': 'Secret Lair Drop Series',
    'DKA': 'Dark Ascension',
    'LCC': 'The Lost Caverns of Ixalan Commander',
    'EOS': 'Edge of Eternities: Stellar Sights',
    'FDN': 'Foundations',
    'CLU': 'Ravnica: Clue Edition',
    'SCG': 'Scourge',
    '3ED': 'Revised Edition',
    'PLST': 'The List',
    'C21': 'Commander 2021',
    'M14': 'Magic 2014 Core Set',
    'M12': 'Magic 2012',
    '2X2': 'Double Masters 2022',
    'FNMP': 'Friday Night Magic',
    'DOM': 'Dominaria',
    'DSC': 'Duskmourn: House of Horror Commander',
    'AKH': 'Amonkhet',
    'SOM': 'Scars of Mirrodin',
    'SPG': 'Special Guests',
    'RVR': 'Ravnica Remastered',
    'C13': 'Commander 2013',
    'TOR': 'Torment',
    'DIS': 'Dissension',
    'OGW': 'Oath of the Gatewatch',
    'MBS': 'Mirrodin Besieged',
    'MH2': 'Modern Horizons 2',
    'HOU': 'Hour of Devastation',
    'BRR': "The Brothers' War Retro Artifacts",
    '40K': 'Warhammer 40,000',
    'MH1': 'Modern Horizons',
    'SCD': 'Starter Commander Decks',
    '2XM': 'Double Masters',
    'F11': 'Friday Night Magic',
    'MIR': 'Mirage',
    'ICE': 'Ice Age',
    'ULG': "Urza's Legacy",
}


# --- Output columns (exact order requested) ---
output_columns = [
    "Count",
    "Tradelist Count",
    "Name",
    "Edition",
    "Edition Code",
    "Card Number",
    "Condition",
    "Language",
    "Foil",
    "Signed",
    "Artist Proof",
    "Altered Art",
    "Misprint",
    "Promo",
    "Textless",
    "Printing Id",
    "Printing Note",
    "Tags",
    "My Price",
]

# --- Helper: format price as $X.YY ---
def format_price(value):
    if value is None or value == "":
        return "$0.00"
    s = str(value).strip()
    if s.startswith("$"):
        s = s[1:].strip()
    try:
        d = Decimal(s)
    except (InvalidOperation, ValueError):
        return "$0.00"
    return f"${d.quantize(Decimal('0.01'))}"

# --- Conversion logic ---
def convert_row(old_row):
    new_row = {col: "" for col in output_columns}

    # Source values
    count = old_row.get("Count", "")
    name = old_row.get("Name", "")
    edition_code = (old_row.get("Edition", "") or "").strip().upper()
    collector_num = old_row.get("Collector Number", "")
    condition = old_row.get("Condition", "")
    language = old_row.get("Language", "")
    foil = old_row.get("Foil", "")
    tags = old_row.get("Tags", "")
    purchase_price = old_row.get("Purchase Price", "")

    # Fill fields
    new_row["Count"] = count
    new_row["Tradelist Count"] = "0"  # static value
    new_row["Name"] = name
    new_row["Edition"] = edition_map.get(edition_code.upper()) # Map Moxfield edition code to Deckbox Edition ( set name )
    new_row["Edition Code"] = edition_code_map.get(edition_code, edition_code) # Convert to custom Deckbox edition codes if any, else use same code
    new_row["Card Number"] = collector_num
    new_row["Condition"] = condition
    new_row["Language"] = language
    new_row["Foil"] = foil
    new_row["Signed"] = ""
    new_row["Artist Proof"] = ""
    new_row["Altered Art"] = ""
    new_row["Misprint"] = ""
    new_row["Promo"] = ""
    new_row["Textless"] = ""
    new_row["Printing Id"] = ""
    new_row["Printing Note"] = ""
    new_row["Tags"] = tags
    new_row["My Price"] = format_price(purchase_price)

    return new_row

# --- Process CSV ---
with open(args.input_file, mode="r", newline="", encoding="utf-8") as infile, \
     open(args.output_file, mode="w", newline="", encoding="utf-8") as outfile:

    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=output_columns)
    writer.writeheader()

    for in_row in reader:
        out_row = convert_row(in_row)
        writer.writerow(out_row)

print(f"✅ Conversion complete! Output written to: {args.output_file}")
