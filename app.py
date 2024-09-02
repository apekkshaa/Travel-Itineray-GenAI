import streamlit as st
import google.generativeai as genai
from ics import Calendar, Event
import json
import re

# Initialize the Google PaLM API client
try:
    api_key = st.secrets["general"]["PALM_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError as e:
    st.error(f"API key not found: {e}")
    st.stop()
except Exception as e:
    st.error(f"Error initializing API client: {e}")
    st.stop()

# Define a constant for currency
CURRENCY = "USD"


def generate_itinerary(city, start_date, end_date, budget, interests, duration):
    prompt = (
        f"Generate a personalized travel itinerary for a trip to {
            city} from {start_date} to {end_date}. "
        f"Include activities based on the following preferences: Budget: {
            budget} {CURRENCY}, Interests: {interests}, "
        f"Trip Duration: {
            duration} days. Provide details like activity titles, descriptions, locations, timings, "
        f"and estimated costs in a structured JSON format."
    )

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        raw_response = response.text.strip()  # Remove leading/trailing whitespace

        # Extract JSON-like structure from the raw response using regex
        json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)

        if json_match:
            json_string = json_match.group(0)
            try:
                json_data = json.loads(json_string)
                return json_data
            except json.JSONDecodeError as e:
                st.error(f"JSON Parse error: {
                         e}. The response received: {json_string}")
                return {}
        else:
            st.error("Could not find JSON in the response.")
            st.write(f"Raw response: {raw_response}")
            return {}

    except Exception as e:
        st.error(f"Error generating itinerary: {e}")
        return {}


def parse_cost(cost_str):
    # Handle cases where the cost is specified as "free" or similar
    if cost_str.lower() in ['free', 'no cost', 'complimentary']:
        return 0.0

    # Handle cases where the cost is specified as "variable" or "unknown"
    if 'variable' in cost_str.lower():
        return 'Variable'  # Return a string indicating variable cost
    elif 'unknown' in cost_str.lower():
        return 'Unknown'  # Return a string indicating unknown cost

    # Remove any non-numeric characters except for the decimal point
    cost_str = re.sub(r'[^\d.]+', '', cost_str)
    try:
        return float(cost_str)
    except ValueError:
        st.warning(f"Invalid cost format detected. Received: {
                   cost_str}. Setting as Unknown.")
        return 'Unknown'  # Default to unknown for non-parsable values


def create_icalendar(events):
    cal = Calendar()
    for event in events:
        e = Event()
        e.name = event.get('title', 'No Title')
        e.begin = event.get('start_time', '2024-01-01T00:00:00')
        e.end = event.get('end_time', '2024-01-01T01:00:00')
        e.description = event.get('description', 'No Description')
        e.location = event.get('location', 'No Location')
        cal.events.add(e)

    try:
        # Save calendar to file
        with open('itinerary.ics', 'w') as f:
            f.write(str(cal))
    except Exception as e:
        st.error(f"Error creating calendar file: {e}")


def display_itinerary(itinerary):
    st.header("Your Personalized Itinerary")

    if 'itinerary' in itinerary:
        total_cost = 0  # Initialize total cost
        variable_costs = False  # Track if there are variable costs
        unknown_costs = False  # Track if there are unknown costs
        for day_info in itinerary.get('itinerary', []):
            st.subheader(day_info.get('day', 'Unknown Day'))
            for activity in day_info.get('activities', []):
                st.markdown(f"**{activity.get('title', 'No Title')}**")
                st.markdown(f"_{activity.get('timing', 'No Timing')}_ at {
                            activity.get('location', 'No Location')}")
                st.markdown(activity.get('description', 'No Description'))
                cost = activity.get('cost', 'Not Provided')

                # Parse and update total cost
                parsed_cost = parse_cost(cost)
                if parsed_cost == 'Variable':
                    variable_costs = True  # Mark that there's a variable cost
                    st.markdown(f"Cost: Variable")
                elif parsed_cost == 'Unknown':
                    unknown_costs = True  # Mark that there's an unknown cost
                    st.markdown(f"Cost: Unknown")
                elif parsed_cost is None:
                    st.markdown("Cost: Unknown")
                else:
                    total_cost += parsed_cost
                    st.markdown(f"Cost: {parsed_cost} {CURRENCY}")

                st.markdown("---")

        # Display total estimated cost
        st.subheader(f"Estimated Total Cost: ${total_cost:.2f}")

        # Inform user about variable and unknown costs if any
        if variable_costs:
            st.warning(
                "Some activities have variable costs, which are not included in the total cost estimate.")
        if unknown_costs:
            st.warning(
                "Some activities have unknown costs, which are not included in the total cost estimate.")
    else:
        st.warning("No itinerary data available to display.")


# Streamlit app layout
st.title("Personalized Travel Itinerary Generator")

city = st.text_input("City")
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")
budget = st.number_input(f"Budget ({CURRENCY})", min_value=0, value=1000)
interests = st.text_area("Interests (e.g., art, museums, outdoor activities)")
duration = st.number_input("Trip Duration (days)", min_value=1, value=3)

if st.button("Generate Itinerary"):
    if city and start_date and end_date:
        itinerary = generate_itinerary(
            city, start_date, end_date, budget, interests, duration)

        if itinerary:
            display_itinerary(itinerary)  # Display the itinerary

            # Convert itinerary to a list of events (example format based on API response)
            events = []
            for day in itinerary.get('itinerary', []):
                for activity in day.get('activities', []):
                    event = {
                        "title": activity.get('title', 'No Title'),
                        # Placeholder timing
                        "start_time": f"{start_date}T10:00:00",
                        # Placeholder timing
                        "end_time": f"{start_date}T12:00:00",
                        "description": activity.get('description', 'No Description'),
                        "location": activity.get('location', 'No Location')
                    }
                    events.append(event)

            create_icalendar(events)
            st.success("Itinerary generated and saved as 'itinerary.ics'")
        else:
            st.error("Could not generate itinerary. Please try again.")
    else:
        st.error("Please fill in all fields.")
