import streamlit as st
import google.generativeai as genai
from ics import Calendar, Event
import json
import re
import io

try:
    api_key = st.secrets["general"]["PALM_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError as e:
    st.error(f"API key not found: {e}")
    st.stop()
except Exception as e:
    st.error(f"Error initializing API client: {e}")
    st.stop()

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
        raw_response = response.text.strip()

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
    if cost_str.lower() in ['free', 'no cost', 'complimentary']:
        return 0.0
    if 'variable' in cost_str.lower():
        return 'Variable'
    elif 'unknown' in cost_str.lower():
        return 'Unknown'

    cost_str = re.sub(r'[^\d.]+', '', cost_str)
    try:
        return float(cost_str)
    except ValueError:
        st.warning(f"Invalid cost format detected. Received: {
                   cost_str}. Setting as Unknown.")
        return 'Unknown'


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
        ical_buffer = io.StringIO()
        ical_buffer.write(str(cal))
        ical_buffer.seek(0)
        return ical_buffer
    except Exception as e:
        st.error(f"Error creating calendar file: {e}")
        return None


def display_itinerary(itinerary):
    st.header("Your Personalized Itinerary")

    if 'itinerary' in itinerary:
        total_cost = 0
        variable_costs = False
        unknown_costs = False
        for day_info in itinerary.get('itinerary', []):
            st.subheader(day_info.get('day', 'Unknown Day'))
            for activity in day_info.get('activities', []):
                st.markdown(f"**{activity.get('title', 'No Title')}**")
                st.markdown(f"_{activity.get('timing', 'No Timing')}_ at {
                            activity.get('location', 'No Location')}")
                st.markdown(activity.get('description', 'No Description'))
                cost = activity.get('cost', 'Not Provided')

                parsed_cost = parse_cost(cost)
                if parsed_cost == 'Variable':
                    variable_costs = True
                    st.markdown(f"Cost: Variable")
                elif parsed_cost == 'Unknown':
                    unknown_costs = True
                    st.markdown(f"Cost: Unknown")
                elif parsed_cost is None:
                    st.markdown("Cost: Unknown")
                else:
                    total_cost += parsed_cost
                    st.markdown(f"Cost: {parsed_cost} {CURRENCY}")

                st.markdown("---")
        st.subheader(f"Estimated Total Cost: ${total_cost:.2f}")
        if variable_costs:
            st.warning(
                "Some activities have variable costs, which are not included in the total cost estimate.")
        if unknown_costs:
            st.warning(
                "Some activities have unknown costs, which are not included in the total cost estimate.")
    else:
        st.warning("No itinerary data available to display.")

st.title("Personalized Travel Itinerary Generator")

city = st.text_input("City")
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")
budget = st.number_input(f"Budget ({CURRENCY})", min_value=0, value=100)
interests = st.text_area("Interests (e.g., art, museums, outdoor activities)")
duration = st.number_input("Trip Duration (days)", min_value=1, value=1)

if st.button("Generate Itinerary"):
    if city and start_date and end_date:
        itinerary = generate_itinerary(
            city, start_date, end_date, budget, interests, duration)

        if itinerary:
            display_itinerary(itinerary)
            events = []
            for day in itinerary.get('itinerary', []):
                for activity in day.get('activities', []):
                    event = {
                        "title": activity.get('title', 'No Title'),
                        "start_time": f"{start_date}T10:00:00",
                        "end_time": f"{start_date}T12:00:00",
                        "description": activity.get('description', 'No Description'),
                        "location": activity.get('location', 'No Location')
                    }
                    events.append(event)

            ical_buffer = create_icalendar(events)
            if ical_buffer:
                st.download_button(
                    label="Download Itinerary (.ics)",
                    data=ical_buffer.getvalue(),
                    file_name='itinerary.ics',
                    mime='text/calendar'
                )
                st.success("Itinerary generated and ready for download.")
        else:
            st.error("Could not generate itinerary. Please try again.")
    else:
        st.error("Please fill in all fields.")
