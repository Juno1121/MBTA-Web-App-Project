# MBTA Web App Project

**Team Member:** Juno Park

---

## 1. Project Overview

This project is a Flask web application that helps users find the nearest MBTA (Massachusetts Bay Transportation Authority) station to any location in the Greater Boston area. The app takes a place name or address as input, geocodes it using the Mapbox API to get coordinates, and then finds the nearest MBTA stop using the MBTA V3 API. The application displays the station name and whether it is wheelchair accessible.

**Core Features:**
- Interactive web form with autocomplete suggestions
- Real-time location search using Mapbox geocoding API
- Nearest MBTA station finder using MBTA V3 API
- Wheelchair accessibility information display
- User-friendly error handling and validation
- Responsive design with helpful guidance for users

**Key Technologies:**
- Python with Flask web framework
- Mapbox Search Box API for geocoding and autocomplete
- MBTA V3 API for public transit data
- HTML/CSS/JavaScript for frontend
- Environment variables for secure API key management

---

## 2. Reflection

### Development Process

**What went well:**
- Breaking the problem into smaller functions (`get_json`, `get_lat_lng`, `get_nearest_station`, `find_stop_near`) made the code modular and easier to test
- Testing each function individually in `main()` before integrating into the Flask app helped catch errors early
- Using the Mapbox and MBTA API documentation was essential for understanding the response structures
- Implementing error handling early prevented many issues during development

**What was challenging:**
- Initially, the MBTA API's default radius filter was too restrictive, causing locations like Babson College to return no results. I solved this by implementing a two-tier search approach: first trying the filtered search for nearby stops, then falling back to a broader search that calculates distances manually using the Haversine formula
- The autocomplete dropdown wasn't appearing initially because the Mapbox suggest endpoint structure was different than expected. I switched to using the forward geocoding endpoint and parsing the features array instead
- Handling edge cases like very specific addresses (e.g., "Babson College Drive, Wellesley, Massachusetts 02481, United States") required simplifying the address format and implementing fallback geocoding attempts
- Understanding the JSON response structures from both APIs required careful debugging with `pprint` and testing API calls directly

**How I approached problem-solving:**
- Started by reading API documentation thoroughly before writing code
- Tested API calls manually in the browser and Python console to understand response formats
- Used print statements and error messages to debug step-by-step
- Broke down complex problems into smaller, testable pieces
- Iteratively improved the user experience based on testing

**What I would change if doing the project again:**
- I would implement the autocomplete feature earlier in the development process, as it significantly improved the user experience
- I would add more comprehensive error messages from the start rather than adding them incrementally
- I would test with a wider variety of location types (landmarks, addresses, neighborhoods) earlier to catch edge cases
- I would consider caching API responses for common locations to reduce API calls during development

### Teamwork & Work Division

I worked independently on this project. I managed my tasks by:
- Starting with Part 1 (helper functions) and completing it fully before moving to Part 2 (Flask app)
- Creating a checklist of required features and checking them off as completed
- Testing each component thoroughly before moving to the next
- Using git commits to track progress and save working versions

### Learning & Use of AI Tools

**What I learned:**
- **APIs and JSON data:** I gained hands-on experience working with REST APIs, understanding request/response formats, URL encoding, and parsing nested JSON structures. Learning to navigate API documentation was crucial
- **Flask and backend web development:** I learned how to create routes, handle POST requests, render templates, and pass data between the frontend and backend. Understanding the request-response cycle was fundamental
- **Project organization:** Organizing code into separate modules (`mbta_helper.py` for API logic, `app.py` for Flask routes, templates for HTML) made the project maintainable
- **Debugging:** I learned to use browser developer tools, Python's error messages, and API testing to systematically identify and fix issues

**AI Tools Experience:**
- **AI Assistant (Cursor):** I used an AI coding assistant extensively throughout this project
  - **How AI helped:**
    - Generated boilerplate code for Flask routes and HTML templates, saving time on repetitive tasks
    - Suggested improvements to error handling and user experience features
    - Helped debug API response parsing issues by explaining JSON structures
    - Provided code examples for implementing autocomplete functionality
    - Assisted with git commands and GitHub workflow
    - Suggested optimizations like the two-tier search approach for finding MBTA stations
  - **Limitations discovered:**
    - Sometimes suggested API endpoints or parameters that didn't match the actual API documentation
    - Generated code that needed adjustment for the specific API response formats
    - Occasionally suggested overly complex solutions when simpler approaches worked better
  - **What I wish I had known earlier:**
    - Always verify AI suggestions against official API documentation
    - Test AI-generated code incrementally rather than implementing large blocks at once
    - Use AI as a starting point but understand the code before using it
    - AI is great for generating structure but human testing is essential for correctness

The combination of learning from documentation, hands-on experimentation, and AI assistance created an effective development workflow that helped me complete the project successfully.

---

**Author:** Juno Park
