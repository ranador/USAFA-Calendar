import streamlit as st
from datetime import datetime, timedelta
import requests
from icalendar import Calendar, Event, vText

st.set_page_config(
    page_title="Class Schedule Generator",  # Tab/window title
    page_icon="📆",  # You can use an emoji or a URL to an icon
)

def add_class():

    new_class = {
        'name': '',
        'location': '',
        'start_time': "08:00",
        'end_time': "09:00",
        'day': ''
    }

    st.session_state.classes.append(new_class)
    st.session_state.new_calendar = None

def remove_class(index):
    st.session_state.classes.pop(index)
    st.session_state.new_calendar = None

def start_session():
    if 'classes' not in st.session_state:
        st.session_state.classes = []

    if 'url' not in st.session_state:
        st.session_state.url = 'https://outlook.office365.com/owa/calendar/d8fbe643dd404faa85cfa326d86d43b6@afacademy.af.edu/785d8eab2f1c490da906c78b2c0946374871920484251035494/calendar.ics'
    
    if 'url_label' not in st.session_state:
        st.session_state.url_label = 'Enter the URL of the master schedule'
    
    if 'url_valid' not in st.session_state:
        st.session_state.url_valid = False

    if 'start_date' not in st.session_state:
        st.session_state.start_date = datetime.now()

    if 'end_date' not in st.session_state:
        st.session_state.end_date = datetime.now()

    if 'time_slots' not in st.session_state:
        st.session_state.time_slots = generate_time_slots()

    if 'new_calendar' not in st.session_state:
        st.session_state.new_calendar = None

def generate_time_slots(interval_minutes=15):
    time_slots = []
    start_time = datetime.strptime('07:00', '%H:%M')
    end_time = datetime.strptime('19:00', '%H:%M')

    current_time = start_time

    while current_time <= end_time:
        time_slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=interval_minutes)

    return time_slots

def generate_schedule():
    response = requests.get(st.session_state.url)
    cal = Calendar.from_ical(response.text)

    new_cal = Calendar()
    new_cal.add('X-WR-CALNAME', 'My Class Schedule')

    start_date = st.session_state.start_date
    end_date = st.session_state.end_date

    classes = st.session_state.classes

    # Loop through each event in the calendar
    for event in cal.walk('vevent'):

        # Get event start and end dates
        event_start = event.get('dtstart').dt
        event_end = event.get('dtend').dt

        # If the event falls within the date range, print it
        if start_date <= event_start <= end_date:
            # You can access properties of the event like this:
            summary = event.get('summary')
            summary_day = summary[0]

            if len(summary) <= 3:
                for class_info in classes:
                    if class_info['day'] == summary_day:
                        start_time_obj = datetime.strptime(class_info['start_time'], "%H:%M").time()
                        end_time_obj = datetime.strptime(class_info['end_time'], "%H:%M").time()
                        start_datetime = datetime.combine(event_start, start_time_obj)
                        end_datetime = datetime.combine(event_start, end_time_obj)

                        new_event = Event()
                        new_event.add('Summary', class_info['name'])
                        new_event.add('dtstart',start_datetime)
                        new_event.add('dtend', end_datetime)
                        new_event.add('location', class_info['location'])
                        new_event.add('categories', vText('Teaching'))

                        new_cal.add_component(new_event)

    st.session_state.new_calendar = new_cal.to_ical()

def main():
    start_session()

    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.markdown(f'<p style="font-size: 48px; font-weight: 600;">Class Schedule Generator</p>', unsafe_allow_html=True)
    
    with st.container(border=True):
        st.session_state.url = st.text_input(st.session_state.url_label, st.session_state.url) 

    with st.container(border=True):
        # st.markdown(f'<p style="font-size: 20px; font-weight: 600;">Semester Information</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.start_date = st.date_input('Semester Start Date', value=st.session_state.start_date)
        with col2:
            st.session_state.end_date = st.date_input('Semester End Date', value=st.session_state.end_date)

    st.button('Add Class', on_click=add_class)

    for i, class_info in enumerate(st.session_state.classes):
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f'<p style="font-size: 20px; font-weight: 600;">Class {i+1}</p>', unsafe_allow_html=True)
            with col2:
                st.button('Remove', key=f'remove_{i}', on_click=remove_class, args=(i,))
            col1, col2 = st.columns(2)

            with col1:
                class_info['name'] = st.text_input('Class Name', key=f'class_name_{i}', value=class_info['name'], help='Enter the name of the class')
                class_info['location'] = st.text_input('Location', key=f'location_{i}', value=class_info['location'])
            with col2:
                class_info['start_time'] = st.selectbox('Start Time', key=f'start_time_{i}', options=st.session_state.time_slots, index=st.session_state.time_slots.index(class_info['start_time']))
                class_info['end_time'] = st.selectbox('End Time', key=f'end_time_{i}', options=st.session_state.time_slots, index=st.session_state.time_slots.index(class_info['end_time']))
                class_info['day'] = st.selectbox('Day', key=f'day_{i}', options=['M', 'T'])

    if len(st.session_state.classes) > 0:
        st.button('Generate Schedule', on_click=generate_schedule)

    if st.session_state.new_calendar:
        st.download_button(label='📆 Download Schedule', data=st.session_state.new_calendar, file_name='teaching_calendar.ics', mime='text/calendar')


if __name__ == '__main__':
    main()