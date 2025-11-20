import os
import json
import urllib.request
import urllib.parse

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys from environment variables
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
MBTA_API_KEY = os.getenv("MBTA_API_KEY")

# Optional: helpful error messages if keys are missing
if MAPBOX_TOKEN is None:
    raise RuntimeError("MAPBOX_TOKEN is not set. Check your .env file.")
if MBTA_API_KEY is None:
    raise RuntimeError("MBTA_API_KEY is not set. Check your .env file.")

# Useful base URLs (you need to add the appropriate parameters for each API request)
MAPBOX_BASE_URL = "https://api.mapbox.com/search/searchbox/v1/forward"
MBTA_BASE_URL = "https://api-v3.mbta.com/"


# A little bit of scaffolding if you want to use it
def get_json(url: str) -> dict:
    """
    Given a properly formatted URL for a JSON web API request, return a Python JSON object containing the response to that request.

    Both get_lat_lng() and get_nearest_station() might need to use this function.
    """
    with urllib.request.urlopen(url) as resp:
        response_text = resp.read().decode("utf-8")
        response_data = json.loads(response_text)
        return response_data


def get_lat_lng(place_name: str) -> tuple[str, str]:
    """
    Given a place name or address, return a (latitude, longitude) tuple with the coordinates of the given place.

    See https://docs.mapbox.com/api/search/search-box/#search-request for Mapbox Search API URL formatting requirements.
    """
    # Try the full place name first
    query = urllib.parse.quote(place_name)
    url = f"{MAPBOX_BASE_URL}?q={query}&access_token={MAPBOX_TOKEN}"
    
    try:
        response_data = get_json(url)
        
        # Extract latitude and longitude from the first feature
        if response_data.get("features") and len(response_data["features"]) > 0:
            coordinates = response_data["features"][0]["geometry"]["coordinates"]
            # Mapbox returns [longitude, latitude], so we need to reverse the order
            longitude = str(coordinates[0])
            latitude = str(coordinates[1])
            return (latitude, longitude)
    except Exception:
        pass
    
    # If full address fails, try simplifying it
    # Remove zip codes and extra details
    simplified = place_name.split(',')[0].strip()  # Just take the first part before comma
    if simplified != place_name:
        query = urllib.parse.quote(simplified)
        url = f"{MAPBOX_BASE_URL}?q={query}&access_token={MAPBOX_TOKEN}"
        try:
            response_data = get_json(url)
            if response_data.get("features") and len(response_data["features"]) > 0:
                coordinates = response_data["features"][0]["geometry"]["coordinates"]
                longitude = str(coordinates[0])
                latitude = str(coordinates[1])
                return (latitude, longitude)
        except Exception:
            pass
    
    raise ValueError(f"No coordinates found for place: {place_name}")


def get_nearest_station(latitude: str, longitude: str) -> tuple[str, bool]:
    """
    Given latitude and longitude strings, return a (station_name, wheelchair_accessible) tuple for the nearest MBTA station to the given coordinates. wheelchair_accessible is True if the stop is marked as accessible, False otherwise.

    See https://api-v3.mbta.com/docs/swagger/index.html#/Stop/ApiWeb_StopController_index for URL formatting requirements for the 'GET /stops' API.
    """
    import math
    
    lat = float(latitude)
    lng = float(longitude)
    
    # First, try with the filter (for nearby stops - faster)
    url = f"{MBTA_BASE_URL}stops?api_key={MBTA_API_KEY}&sort=distance&filter[latitude]={latitude}&filter[longitude]={longitude}"
    
    try:
        response_data = get_json(url)
        
        if response_data.get("data") and len(response_data["data"]) > 0:
            nearest_stop = response_data["data"][0]
            station_name = nearest_stop["attributes"]["name"]
            
            # Check wheelchair accessibility
            wheelchair_boarding = nearest_stop["attributes"].get("wheelchair_boarding", 0)
            wheelchair_accessible = (wheelchair_boarding == 1)
            
            return (station_name, wheelchair_accessible)
    except Exception:
        pass
    
    # If no results with filter, search more broadly by getting stops in the area
    # Try searching without the filter but with a bounding box or get all stops and calculate distance
    # For now, let's try getting stops and calculating distance manually
    # We'll search for stops in Massachusetts (rough bounding box)
    
    # Calculate distance helper function
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points in miles using Haversine formula"""
        R = 3959  # Earth radius in miles
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    # Try to get stops in a wider area - search for stops with coordinates
    # We'll fetch a larger set and find the nearest one
    # Use a bounding box approach - search within ~10 miles
    # Actually, let's just get stops and calculate distance for all of them
    # But that might be too many. Let's try a different approach:
    # Search for stops in the general Boston area first
    
    # Try searching without lat/long filter but with sort=distance (if API supports it)
    # Or search for stops in a bounding box
    # For simplicity, let's search for all stops and find the nearest
    
    # Get stops - we'll limit to first 1000 and find nearest
    # Note: This is not ideal but will work for finding the nearest station
    url = f"{MBTA_BASE_URL}stops?api_key={MBTA_API_KEY}&page[limit]=1000"
    
    try:
        response_data = get_json(url)
        
        if response_data.get("data") and len(response_data["data"]) > 0:
            nearest_stop = None
            min_distance = float('inf')
            
            for stop in response_data["data"]:
                stop_lat = stop["attributes"].get("latitude")
                stop_lng = stop["attributes"].get("longitude")
                
                if stop_lat is not None and stop_lng is not None:
                    distance = haversine_distance(lat, lng, stop_lat, stop_lng)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_stop = stop
            
            if nearest_stop:
                station_name = nearest_stop["attributes"]["name"]
                wheelchair_boarding = nearest_stop["attributes"].get("wheelchair_boarding", 0)
                wheelchair_accessible = (wheelchair_boarding == 1)
                return (station_name, wheelchair_accessible)
    except Exception as e:
        pass
    
    # If still no results, raise error
    raise ValueError("NO_MBTA_STATION_NEARBY")


def find_stop_near(place_name: str) -> tuple[str, bool]:
    """
    Given a place name or address, return the nearest MBTA stop and whether it is wheelchair accessible.

    This function might use all the functions above.
    """
    # Get coordinates for the place
    latitude, longitude = get_lat_lng(place_name)
    
    # Find the nearest MBTA station
    station_name, wheelchair_accessible = get_nearest_station(latitude, longitude)
    
    return (station_name, wheelchair_accessible)


def main():
    """
    You should test all the above functions here
    """
    print("Testing get_lat_lng('Boston Common'):")
    try:
        lat, lng = get_lat_lng("Boston Common")
        print(f"  Latitude: {lat}, Longitude: {lng}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\nTesting find_stop_near('Boston Common'):")
    try:
        station, accessible = find_stop_near("Boston Common")
        print(f"  Station: {station}")
        print(f"  Wheelchair Accessible: {accessible}")
    except Exception as e:
        print(f"  Error: {e}")


if __name__ == "__main__":
    main()
