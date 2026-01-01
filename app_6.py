import streamlit as st
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
import httpx
import json
import pandas as pd

# Include the dict_iata dictionary
dict_iata = {
    "Tirana": ["TIA"],
    "Graz": ["GRZ"],
    "Innsbruck": ["INN"],
    "Salzburg": ["SZG"],
    "Vienna": ["VIE"],
    "Antwerp": ["ANR"],
    "Brussels": ["BRU"],
    "Charleroi": ["CRL"],
    "Burgas": ["BOJ"],
    "Sofia": ["SOF"],
    "Varna": ["VAR"],
    "Dubrovnik": ["DBV"],
    "Pula": ["PUY"],
    "Split": ["SPU"],
    "Zadar": ["ZAD"],
    "Zagreb": ["ZAG"],
    "Larnaca": ["LCA"],
    "Paphos": ["PFO"],
    "Brno": ["BRQ"],
    "Prague": ["PRG"],
    "Aalborg": ["AAL"],
    "Billund": ["BLL"],
    "Copenhagen": ["CPH"],
    "Tallinn": ["TLL"],
    "Helsinki": ["HEL"],
    "Rovaniemi": ["RVN"],
    "Turku": ["TKU"],
    "Bordeaux": ["BOD"],
    "Lyon": ["LYS"],
    "Marseille": ["MRS"],
    "Nice": ["NCE"],
    "Paris": ["CDG", "ORY", "BVA"],
    "Berlin": ["BER"],
    "Cologne/Bonn": ["CGN"],
    "Düsseldorf": ["DUS"],
    "Frankfurt": ["FRA"],
    "Hamburg": ["HAM"],
    "Munich": ["MUC"],
    "Stuttgart": ["STR"],
    "Athens": ["ATH"],
    "Heraklion": ["HER"],
    "Rhodes": ["RHO"],
    "Thessaloniki": ["SKG"],
    "Budapest": ["BUD"],
    "Reykjavik": ["KEF"],
    "Cork": ["ORK"],
    "Dublin": ["DUB"],
    "Shannon": ["SNN"],
    "Milan": ["MXP", "LIN", "BGY"],
    "Naples": ["NAP"],
    "Rome": ["FCO", "CIA"],
    "Venice": ["VCE"],
    "Riga": ["RIX"],
    "Vilnius": ["VNO"],
    "Luxembourg": ["LUX"],
    "Luqa": ["MLA"],
    "Podgorica": ["TGD"],
    "Amsterdam": ["AMS"],
    "Eindhoven": ["EIN"],
    "Bergen": ["BGO"],
    "Oslo": ["OSL"],
    "Krakow": ["KRK"],
    "Warsaw": ["WAW", "WMI"],
    "Lisbon": ["LIS"],
    "Porto": ["OPO"],
    "Bucharest": ["OTP"],
    "Belgrade": ["BEG"],
    "Bratislava": ["BTS"],
    "Ljubljana": ["LJU"],
    "Barcelona": ["BCN"],
    "Madrid": ["MAD"],
    "Malaga": ["AGP"],
    "Palma": ["PMI"],
    "Stockholm": ["ARN"],
    "Geneva": ["GVA"],
    "Zurich": ["ZRH"],
    "Istanbul": ["IST"],
    "Birmingham": ["BHX"],
    "Edinburgh": ["EDI"],
    "London": ["LHR", "LGW", "STN"],
    "Manchester": ["MAN"],
    "New York": ["JFK"],
    "Dusseldorf": ["DUS"],
    "Cologne": ["CGN"],
    "Hannover": ["HAJ"],
    "Dresden": ["DRS"],
    "Leipzig": ["LEJ"],
    "Nuremberg": ["NUE"],
    "Bremen": ["BRE"],
    "Dortmund": ["DTM"],
    "Rotterdam": ["RTM"],
    "Linz": ["LNZ"],
    "Gdansk": ["GDN"],
    "Wroclaw": ["WRO"],
    "Poznan": ["POZ"],
    "Sarajevo": ["SJJ"],
    "Skopje": ["SKP"],
    "Ankara": ["ESB"],
    "Izmir": ["ADB"],
    "Antalya": ["AYT"],
    "Valletta": ["MLA"],
    "Faro": ["FAO"],
    "Seville": ["SVQ"],
    "Valencia": ["VLC"],
    "Alicante": ["ALC"],
    "Palma de Mallorca": ["PMI"],
    "Ibiza": ["IBZ"],
    "Tenerife South": ["TFS"],
    "Gran Canaria": ["LPA"],
    "Lanzarote": ["ACE"],
    "Fuerteventura": ["FUE"],
    "Kaunas": ["KUN"],
    "Katowice": ["KTW"],
    "Rzeszow": ["RZE"],
    "Lublin": ["LUZ"],
    "Bydgoszcz": ["BZG"],
    "Szczecin": ["SZZ"],
    "Lodz": ["LCJ"],
    "Chisinau": ["KIV"],
    "Kyiv": ["KBP"],
    "Lviv": ["LWO"],
    "Odessa": ["ODS"],
    "Kharkiv": ["HRK"],
    "Dnipro": ["DNK"]
}

def get_iata_code(city_name: str) -> list[str] | None:
    """Returns the IATA code(s) for a given city name from dict_iata."""
    iata_codes = dict_iata.get(city_name)
    if iata_codes:
        return iata_codes
    else:
        return None

async def search_kiwi_flights(flyFrom: str, flyTo: str, dateFrom: str, dateTo: str):
    url = "https://mcp.kiwi.com"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(url, timeout=5)
            response.raise_for_status()
    except httpx.RequestError as e:
        st.error(f"Error connecting to {url}: {e}. Please check the URL and your network connection.")
        return None
    except httpx.HTTPStatusError as e:
        st.error(f"HTTP status error from {url}: {e}. The server responded with an error status.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while checking {url}: {e}")
        return None

    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tool_name = "search-flight"
            arguments = {
                "flyFrom": flyFrom,
                "flyTo": flyTo,
                "departureDate": dateFrom,
                "returnDate": dateTo,
                "trip_type": "round"
            }

            try:
                result = await session.call_tool(tool_name, arguments)
                flight_json_string = ""
                for content in result.content:
                    if content.type == "text":
                        flight_json_string += content.text
                return flight_json_string
            except Exception as e:
                return None

# Streamlit app layout
st.set_page_config(layout='wide', page_title='✨Wanderlust')
st.title('✨Wanderlust - Find the Cheapest Getaway With Your Bestie!')

# Input widgets
countries = sorted(list(dict_iata.keys()))

departure_city_name_1 = st.selectbox('Your Departure City', countries)
departure_city_name_2 = st.selectbox('Your Bestie Departure City', [''] + countries, index=0)
departure_date = st.date_input('Departure Date')
return_date = st.date_input('Return Date')

# New multiselect for destination cities
selected_destination_cities = st.multiselect(
    'Where do you want to go? Leave as-is if you want to search everywhere, or clear selection with X in the right corner, and pick only cities you like.',
    options=countries,
    default=countries # All selected by default
)

if st.button('Search Flights to Selected Destinations'):
    if departure_city_name_1 and departure_date and return_date and selected_destination_cities:
        if departure_date >= return_date:
            st.error("Departure date cannot be on or after return date. Please select valid dates.")
        else:
            selected_departure_cities = [departure_city_name_1]
            if departure_city_name_2 and departure_city_name_2 != departure_city_name_1:
                selected_departure_cities.append(departure_city_name_2)

            formatted_departure_date = departure_date.strftime('%d/%m/%Y')
            formatted_return_date = return_date.strftime('%d/%m/%Y')

            comparison_results = [] # Initialize list to store results for comparison

            # Filter out destinations that are also selected departure cities to avoid self-searches.
            effective_destination_cities = [city for city in selected_destination_cities if city not in selected_departure_cities]

            # Total number of searches to show progress accurately
            total_destinations_to_search = len(effective_destination_cities)
            total_searches_per_dep_city = 0
            if total_destinations_to_search > 0:
                # This is an estimate, as cities can have multiple IATA codes
                total_searches_per_dep_city = sum(len(get_iata_code(city) or ["N/A"]) * sum(len(get_iata_code(dest) or ["N/A"]) for dest in effective_destination_cities) for city in selected_departure_cities)
            
            total_searches = total_searches_per_dep_city # This will be the actual number of API calls
            current_search_count = 0

            progress_text = st.empty()
            progress_bar = st.progress(0)

            st.subheader(f"Searching for cheapest direct flights from {', '.join(selected_departure_cities)} from {formatted_departure_date} to {formatted_return_date} to selected destinations...")

            for destination_city_name in effective_destination_cities:
                destination_data = {'Destination': destination_city_name}

                for dep_idx, current_departure_city_name in enumerate(selected_departure_cities):
                    all_iata_flights_for_pair = []
                    departure_iata_codes = get_iata_code(current_departure_city_name)
                    destination_iata_codes = get_iata_code(destination_city_name)

                    if departure_iata_codes and destination_iata_codes:
                        for fly_from_code in departure_iata_codes:
                            for fly_to_code in destination_iata_codes:
                                current_search_count += 1
                                progress_percent = current_search_count / total_searches if total_searches > 0 else 0
                                progress_bar.progress(progress_percent)
                                progress_text.text(f"Searching from {current_departure_city_name} ({fly_from_code}) to {destination_city_name} ({fly_to_code}): {current_search_count}/{total_searches} searches ({int(progress_percent*100)}%) of selected destinations")

                                raw_flight_results = asyncio.run(search_kiwi_flights(flyFrom=fly_from_code, flyTo=fly_to_code, dateFrom=formatted_departure_date, dateTo=formatted_return_date))

                                if raw_flight_results:
                                    try:
                                        flight_data = json.loads(raw_flight_results)
                                        # Filter for direct flights among all returned flights for this IATA pair
                                        direct_flights = [f for f in flight_data if not f.get('layovers') or len(f.get('layovers', [])) == 0]
                                        if direct_flights:
                                            all_iata_flights_for_pair.extend(direct_flights)
                                    except json.JSONDecodeError:
                                        pass # Continue if JSON decode fails for a specific result

                    # After checking all IATA combinations for the current city-to-city pair:
                    cheapest_direct_flight_for_pair = None
                    if all_iata_flights_for_pair:
                        cheapest_direct_flight_for_pair = min(all_iata_flights_for_pair, key=lambda x: x['price'])

                    city_label = f"City {dep_idx + 1}"
                    if cheapest_direct_flight_for_pair:
                        destination_data[f'From {city_label}'] = cheapest_direct_flight_for_pair['cityFrom']
                        destination_data[f'Price ({city_label})'] = f"{cheapest_direct_flight_for_pair['price']} {cheapest_direct_flight_for_pair['currency']}"
                        destination_data[f'Link ({city_label})'] = cheapest_direct_flight_for_pair['deepLink']
                        destination_data[f'PriceValue ({city_label})'] = cheapest_direct_flight_for_pair['price'] # For sorting
                    else:
                        destination_data[f'From {city_label}'] = current_departure_city_name
                        destination_data[f'Price ({city_label})'] = 'N/A'
                        destination_data[f'Link ({city_label})'] = ''
                        destination_data[f'PriceValue ({city_label})'] = float('inf')

                comparison_results.append(destination_data)

            progress_text.empty()
            progress_bar.empty()

            if comparison_results:
                results_df = pd.DataFrame(comparison_results)

                # Calculate Average Price and Price Difference
                if len(selected_departure_cities) == 2:
                    price_col_1 = 'PriceValue (City 1)'
                    price_col_2 = 'PriceValue (City 2)'

                    results_df['Average Price'] = 'N/A'
                    results_df['Price Difference'] = 'N/A'

                    valid_prices_mask = (results_df[price_col_1] != float('inf')) & (results_df[price_col_2] != float('inf'))

                    results_df.loc[valid_prices_mask, 'Average Price'] = \
                        (results_df[price_col_1] + results_df[price_col_2]) / 2
                    results_df.loc[valid_prices_mask, 'Price Difference'] = \
                        abs(results_df[price_col_1] - results_df[price_col_2])

                price_cols = [col for col in results_df.columns if col.startswith('PriceValue')]
                if price_cols:
                    results_df['CheapestOverallPrice'] = results_df[price_cols].min(axis=1)
                    results_df = results_df.sort_values(by='CheapestOverallPrice').drop(columns=['CheapestOverallPrice'])

                if 'Average Price' in results_df.columns:
                    results_df = results_df.sort_values(by='Average Price', key=lambda x: x.apply(lambda val: float(val) if isinstance(val, (int, float)) or (isinstance(val, str) and val.replace('.', '', 1).isdigit()) else float('inf')))

                for col in results_df.columns:
                    if col.startswith('Link (') and results_df[col].dtype == 'object':
                        results_df[col] = results_df[col].apply(lambda x: f"[Book Now]({x})" if x else '')

                results_df = results_df.drop(columns=[col for col in results_df.columns if col.startswith('PriceValue')])

                st.subheader("Cheapest Direct Round Trip Flight Comparisons to Selected Destinations:")
                st.markdown(results_df.to_html(escape=False, index=False), unsafe_allow_html=True)
            else:
                st.warning(f"No direct round trip flights found from the selected departure cities to any of the selected destinations for {formatted_departure_date} to {formatted_return_date}.")
    else:
        st.warning("Please select at least one departure city, a departure date, a return date, and at least one destination city.")
