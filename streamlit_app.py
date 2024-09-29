import streamlit as st
import pandas as pd

from pandas_datareader import wb
from datetime import date

# Data of Head of States in respect to country and date (PLAD Harvard)
dataHOS = pd.read_csv('PLAD_April_2024.tab', sep='\t')
# Take only: country code; HOS; start year of HOS; end year of HOS
dataHOS = dataHOS[['country', 'leader', 'startdate', 'enddate', 'startyear', 'endyear']] # Use 'startyear' / 'endyear' for just years rather than dates
# Normalize column type (float -> str)
dataHOS = dataHOS.astype({'startyear': int})
dataHOS = dataHOS.astype({'startyear': str})
dataHOS = dataHOS.astype({'endyear': int})
dataHOS = dataHOS.astype({'endyear': str})

# Singular tables of data if needed

# Inflation data (World Bank)
# dataInf = wb.data.DataFrame("NY.GDP.DEFL.KD.ZG")

# Unemployment data (World Bank)
# dataUnem = wb.data.DataFrame("SL.UEM.TOTL.ZS")

# Annual GDP growth data (World Bank)
# dataGdpGrowth = wb.data.DataFrame("NY.GDP.MKTP.KD.ZG")

# Annual GDP per capita growth data (World Bank)
# dataGdpPcGworth = wb.data.DataFrame("NY.GDP.PCAP.KD.ZG")

# Data, starting from 1989, for: Inflation rate; Unemployment rate; Annual GDP growth data; Annual GDP per capita growth
dataGeneral = wb.download(indicator=['NY.GDP.DEFL.KD.ZG', 'SL.UEM.TOTL.ZS', 'NY.GDP.MKTP.KD.ZG', 'NY.GDP.MKTP.KD.ZG'], start=1948, end=date.today().year, country=["AFG"])
# Format it as pandas dataframe
dataGeneral = pd.DataFrame(dataGeneral)
# Renaming columns of general data
dataGeneral.rename(columns={'NY.GDP.DEFL.KD.ZG': 'Inflation Rate', 'SL.UEM.TOTL.ZS': 'Unemployment Rate', 'NY.GDP.MKTP.KD.ZG': 'GDP Growth','NY.GDP.PCAP.KD.ZG': 'GDP Per Capita'}, inplace=True)
# To make 'year' as a column
dataGeneral.reset_index(inplace=True)

# Merge on 'startyear' == 'year'
dataStart = dataHOS.merge(dataGeneral, left_on=['startyear', 'country'], right_on=['year', 'country'])
# Merge on 'endyear' == 'year'
dataEnd = dataHOS.merge(dataGeneral, left_on=['endyear', 'country'], right_on=['year', 'country'])

# Make main dataframe
dataMain = dataStart.merge(dataEnd, how='outer')
# Sort first by 'country', then by'startdate', then by 'leader'
dataMain.sort_values(by=['country', 'startdate', 'leader'], inplace=True) # NEED TO NORMALIZE COUNTRY NAMES: (example) UNITED STATES OF AMERICA -> UNITED STATES

st.set_page_config(page_title="Polistats", page_icon="🏛️")
st.title("🏛️ Polistats")

# Dictionary holding the statistics for each president
president_data = {
    'Obama': pd.DataFrame({
        'Metric': ['GDP Growth', 'Unemployment Rate', 'Inflation Rate'],
        'Value': [2.3, 5.0, 1.6]
    }),
    'Trump': pd.DataFrame({
        'Metric': ['GDP Growth', 'Unemployment Rate', 'Inflation Rate', 'Tariff Rates'],
        'Value': [2.5, 3.9, 1.8, 12.0]
    }),
    'Biden': pd.DataFrame({
        'Metric': ['GDP Growth', 'Unemployment Rate', 'COVID-19 Recovery'],
        'Value': [3.0, 4.5, 70.0]
    })
}

# Let users select two presidents to compare
presidents = st.multiselect("Select two presidents to compare", list(president_data.keys()), default=["Obama", "Trump"])

# Ensure that exactly two presidents are selected
if len(presidents) == 2:
    # Get the two selected DataFrames
    df1 = president_data[presidents[0]]
    df2 = president_data[presidents[1]]

    # Merge on 'Metric' to find common statistics
    df_comparison = pd.merge(df1, df2, on='Metric', suffixes=(f'_{presidents[0]}', f'_{presidents[1]}'))

    if not df_comparison.empty:
        st.write(f"### Comparison between {presidents[0]} and {presidents[1]}")
        # Use st.dataframe for an interactive table
        st.dataframe(df_comparison)
    else:
        st.write(f"No common statistics found between {presidents[0]} and {presidents[1]}")
else:
    st.write("Please select exactly two presidents to compare.")
