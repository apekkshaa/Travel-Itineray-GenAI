# Personalized Travel Itinerary Generator

## Overview

The Personalized Travel Itinerary Generator is a web application designed to create customized travel itineraries based on user preferences. Users can input their budget, interests, trip duration, and destination to receive a detailed, dynamic itinerary. The app also offers functionality to export the itinerary as an iCalendar file for easy integration with calendar applications.

## Features

- **Personalized Itinerary Generation:** Generate customized itineraries based on user input.
- **Cost Parsing:** Handles various cost formats and provides clear cost information.
- **iCalendar Export:** Download the itinerary in `.ics` format for calendar applications.
- **Dynamic Display:** Shows itinerary details with organized activities and cost estimates.

## Tech Stack

- **Backend:** Python, Google PaLM API
- **Frontend:** Streamlit
- **Additional Libraries:** `ics` for calendar functionality, `json` for data handling, `re` for regex operations

## Getting Started

### Prerequisites

- Python 3.7 or later
- `pip` (Python package installer)
- Google PaLM API key

### Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/personalized-travel-itinerary-generator.git
    cd personalized-travel-itinerary-generator
    ```

2. **Set Up Virtual Environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure API Key:**

    Create a `.streamlit/secrets.toml` file in the project root and add your Google PaLM API key:

    ```toml
    [general]
    PALM_API_KEY = "your_api_key_here"
    ```

5. **Run the Application:**

    ```bash
    streamlit run app.py
    ```


## Code Explanation

### `app.py`

This script contains the core functionality of the application:

- **`generate_itinerary(city, start_date, end_date, budget, interests, duration)`**: Communicates with Google PaLM API to generate a travel itinerary.
- **`parse_cost(cost_str)`**: Parses cost information from the API response.
- **`create_icalendar(events)`**: Converts itinerary data into iCalendar format.
- **`display_itinerary(itinerary)`**: Displays the generated itinerary in the Streamlit app.

Lists the Python dependencies required for the application:
    ```
    streamlit==1.10.0
    ```
    ```
    google-generativeai==0.1.0
    ```
    ```
    ics==0.8.0
    ```

  
## Usage

1. Open the application in your browser.
2. Enter your city, start date, end date, budget, interests, and trip duration.
3. Click "Generate Itinerary" to create a personalized travel plan.
4. Download the `.ics` file to integrate the itinerary with your calendar.


## Contributing

Feel free to fork the repository and submit pull requests. For any issues or suggestions, please open an issue on GitHub.


