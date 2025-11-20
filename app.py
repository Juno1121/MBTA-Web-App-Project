from flask import Flask, render_template, request, jsonify
import mbta_helper
import urllib.request
import urllib.parse
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


@app.route("/")
def index():
    """
    Renders the index page with a form to input a place name.
    """
    return render_template("index.html")


@app.route("/autocomplete")
def autocomplete():
    """
    Returns autocomplete suggestions for a given search query using Mapbox API.
    """
    query = request.args.get("q", "").strip()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    mapbox_token = os.getenv("MAPBOX_TOKEN")
    if not mapbox_token:
        return jsonify([])
    
    try:
        # Use Mapbox Search Box API forward endpoint for autocomplete
        # This endpoint returns features that we can use as suggestions
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.mapbox.com/search/searchbox/v1/forward?q={encoded_query}&access_token={mapbox_token}&limit=5"
        
        with urllib.request.urlopen(url) as resp:
            response_text = resp.read().decode("utf-8")
            response_data = json.loads(response_text)
            
            suggestions = []
            if "features" in response_data:
                for feature in response_data["features"]:
                    properties = feature.get("properties", {})
                    
                    # Extract address components from Mapbox response
                    name = properties.get("name", "")
                    address = properties.get("address", "")
                    place_formatted = properties.get("place_formatted", "")
                    context = properties.get("context", {})
                    feature_type = properties.get("feature_type", "")
                    
                    # Prefer simpler names for better geocoding results
                    # Prioritize place names over specific addresses
                    display_name = ""
                    
                    # For places (cities, neighborhoods), use just name + region
                    if feature_type in ["place", "locality", "neighborhood"]:
                        if name and isinstance(context, dict):
                            region = context.get("region", {})
                            if isinstance(region, dict):
                                region_name = region.get("name", "")
                                if region_name:
                                    display_name = f"{name}, {region_name}"
                                else:
                                    display_name = name
                            else:
                                display_name = name
                        elif name:
                            display_name = name
                    # For addresses, use name + city/region (not full address with zip)
                    elif name:
                        if isinstance(context, dict):
                            region = context.get("region", {})
                            district = context.get("district", {})
                            if isinstance(region, dict):
                                region_name = region.get("name", "")
                                if region_name:
                                    display_name = f"{name}, {region_name}"
                                else:
                                    display_name = name
                            elif isinstance(district, dict):
                                district_name = district.get("name", "")
                                if district_name:
                                    display_name = f"{name}, {district_name}"
                                else:
                                    display_name = name
                            else:
                                display_name = name
                        else:
                            display_name = name
                    elif place_formatted:
                        # Use place_formatted but remove country if present
                        parts = place_formatted.split(',')
                        if len(parts) > 2:
                            display_name = ','.join(parts[:2]).strip()  # Just city, state
                        else:
                            display_name = place_formatted
                    else:
                        continue  # Skip if no usable text
                    
                    # Use the display name as the value to submit
                    suggestions.append({
                        "text": display_name,
                        "value": display_name
                    })
            
            return jsonify(suggestions)
    except Exception as e:
        # Log error for debugging but return empty list
        print(f"Autocomplete error: {e}")
        return jsonify([])


@app.route("/nearest_mbta", methods=["POST"])
def nearest_mbta():
    """
    Handles the form submission, finds the nearest MBTA stop, and displays the result.
    """
    place_name = request.form.get("place_name", "").strip()
    
    # Validate input
    if not place_name:
        return render_template("error.html", 
                             error_message="Please enter a place name or address. The field cannot be empty.")
    
    if len(place_name) < 2:
        return render_template("error.html", 
                             error_message="Please enter at least 2 characters. Your input is too short.")
    
    # Additional validation - check if it's mostly special characters
    if not any(c.isalpha() for c in place_name):
        return render_template("error.html", 
                             error_message="Please enter a valid place name or address. Include letters in your input.")
    
    try:
        # Find the nearest MBTA stop
        station_name, wheelchair_accessible = mbta_helper.find_stop_near(place_name)
        
        # Render the result page
        return render_template("mbta_station.html", 
                             place_name=place_name,
                             station_name=station_name,
                             wheelchair_accessible=wheelchair_accessible)
    except ValueError as e:
        error_str = str(e)
        
        # Check if it's a "no MBTA station nearby" error (should rarely happen now)
        if error_str == "NO_MBTA_STATION_NEARBY":
            error_message = f"⚠️ Unable to find any MBTA stations.\n\n" \
                           f"This is unusual. Please try:\n\n" \
                           f"• Check your internet connection\n" \
                           f"• Try a different location\n" \
                           f"• Make sure the location is in the Greater Boston area"
        elif "No coordinates found" in error_str:
            error_message = f"Could not find location '{place_name}'. Please try:\n\n" \
                           f"• Check your spelling\n" \
                           f"• Use a simpler address (e.g., 'Babson College' instead of full street address)\n" \
                           f"• Try a well-known landmark (e.g., 'Boston Common', 'Fenway Park')\n" \
                           f"• Use just the city or neighborhood name (e.g., 'Wellesley', 'Boston')"
        else:
            error_message = f"Could not find location '{place_name}'. Please try:\n\n" \
                           f"• Check your spelling\n" \
                           f"• Use a simpler location name (e.g., 'Babson College' instead of full address)\n" \
                           f"• Try a well-known landmark (e.g., 'Boston Common', 'Fenway Park')\n" \
                           f"• Make sure the location is in the Greater Boston area"
        
        return render_template("error.html", error_message=error_message)
    except Exception as e:
        # Handle any other errors (e.g., API errors, network issues)
        error_message = f"An error occurred while searching: {str(e)}\n\nPlease try again with a different location or check your internet connection."
        return render_template("error.html", error_message=error_message)


if __name__ == "__main__":
    app.run(debug=True)
