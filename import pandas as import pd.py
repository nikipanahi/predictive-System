import pandas as pd
import json
with open('data.json', 'r', encoding='utf-8') as f:
    live_data = json.load(f)
if 'data' in live_data:
    df = pd.DataFrame(live_data['data'])
else:
    df = pd.DataFrame(live_data) # اگر ساختار لیست مستقیم بود
cdf=df['part_info']
cdf=cdf.groupby(by=['903-1342']).sum()
print(cdf.head())