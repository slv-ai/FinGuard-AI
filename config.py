import os
from dotenv import load_dotenv
# paths--------------------------------------
base_dir=os.path.dirname(os.path.abspath(__file__))
print(base_dir)
data_dir=os.path.join(base_dir,'data')
print(data_dir)
RAW_TRANSACTIONS_DIR = os.path.join(DATA_DIR, "raw", "transactions")
RAW_REGULATIONS_DIR = os.path.join(DATA_DIR, "raw", "regulations")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
OFAC_SDN_URL = "https://www.treasury.gov/ofac/downloads/sdn.xml"