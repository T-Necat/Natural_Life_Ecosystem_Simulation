import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import time
import random
import os
from PIL import Image, ImageDraw
from living_class import Living, distances, file_path

st.set_page_config(layout="wide")
st.title("📊 Natural Life Ecosystem Simulation")

@st.cache_data(show_spinner=False, ttl=1)
def load_data(force_reload=False):
    try:
        if force_reload:
            st.cache_data.clear()
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        return pd.DataFrame(columns=['id', 'species', 'gender', 'location', 'movement_distance', 'hunting_distance', 'huntable_creatures'])
    except Exception as e:
        st.error(f"Data loading error: {e}")
        return pd.DataFrame(columns=['id', 'species', 'gender', 'location', 'movement_distance', 'hunting_distance', 'huntable_creatures'])

st.sidebar.title("Simulation Controls")

if st.sidebar.button("🔄 Start New Simulation"):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        pd.DataFrame(columns=['id', 'species', 'gender', 'location', 'movement_distance', 
                            'hunting_distance', 'huntable_creatures']).to_csv(file_path, index=False)
        st.sidebar.success("Simulation reset!")
    except Exception as e:
        st.sidebar.error(f"Error resetting simulation: {e}")

st.sidebar.header("Add Creatures")
creature_counts = {}
for species in distances.keys():
    creature_counts[species] = st.sidebar.slider(f"{species.capitalize()} count", 0, 30, 5)

if st.sidebar.button("➕ Add Creatures"):
    try:
        if not os.path.exists(file_path):
            pd.DataFrame(columns=['id', 'species', 'gender', 'location', 'movement_distance', 
                                'hunting_distance', 'huntable_creatures']).to_csv(file_path, index=False)
        
        progress_bar = st.sidebar.progress(0)
        total_creatures = sum(creature_counts.values())
        current_progress = 0
        
        new_creatures = []
        
        for species, count in creature_counts.items():
            if count > 0:
                if species == "predator":
                    for _ in range(count):
                        creature = Living(species, " ")
                        new_creatures.append(creature.__dict__)
                elif species in ["chicken"]:
                    for _ in range(count):
                        creature = Living(species, "female")
                        new_creatures.append(creature.__dict__)
                elif species in ["rooster"]:
                    for _ in range(count):
                        creature = Living(species, "male")
                        new_creatures.append(creature.__dict__)
                else:
                    male_count = count // 2
                    female_count = count - male_count
                    for _ in range(male_count):
                        creature = Living(species, "male")
                        new_creatures.append(creature.__dict__)
                    for _ in range(female_count):
                        creature = Living(species, "female")
                        new_creatures.append(creature.__dict__)
                
                current_progress += count
                progress_bar.progress(current_progress / total_creatures)
        
        pd.DataFrame(new_creatures).to_csv(file_path, index=False)
        progress_bar.empty()
        st.sidebar.success(f"Total {total_creatures} creatures added!")
    except Exception as e:
        st.sidebar.error(f"Error adding creatures: {e}")

step_count = st.sidebar.slider("Simulation step count", 10, 1000, 100)

simulation_speed = st.sidebar.slider("Simulation speed", 0.1, 2.0, 0.5)

tab1, tab2, tab3 = st.tabs(["📈 Creature Map", "📊 Statistics", "📋 Detailed Data"])

def location_to_int(creature_location):
    if isinstance(creature_location, str):
        creature_location = creature_location.strip('[]()')
        location_list = creature_location.split(',')
        x = int(location_list[0].strip())
        y = int(location_list[1].strip())
        return x, y
    else:
        return creature_location[0], creature_location[1]

def scan_coordinates(range_distance, df, creature_id):
    suitable_creatures = []
    center_creature = df.loc[df['id'] == creature_id].iloc[0]
    center_x, center_y = location_to_int(center_creature['location'])

    for index, other_creature in df.iterrows():
        other_creature_x, other_creature_y = location_to_int(other_creature['location'])
        if abs(other_creature_x - center_x) <= range_distance and abs(other_creature_y - center_y) <= range_distance:
            if other_creature['id'] != creature_id:
                suitable_creatures.append(other_creature)
    return suitable_creatures

def check_mating_for_creature(df, creature_id):
    born_list = []
    try:
        creature = df.loc[df['id'] == creature_id].iloc[0]
        suitable_creatures = scan_coordinates(3, df, creature['id'])

        if suitable_creatures:
            matches = []
            for other_creature in suitable_creatures:
                if other_creature['species'] == creature['species'] and other_creature['gender'] != creature['gender']:
                    matches.append(other_creature['id'])
            if matches:
                new_creature = Living(creature['species'], random.choice(['male', 'female']))
                born_list.append(new_creature)
                return f"ID: {creature['id']} mated with {matches[0]}. New ID: {new_creature.id}", born_list
    except Exception as e:
        pass
    return "", born_list

def check_hunting_for_creature(df, creature_id):
    hunted_list = []
    try:
        creature = df.loc[df['id'] == creature_id].iloc[0]
        hunting_distance = creature['hunting_distance']

        if hunting_distance == 0:
            return f"Creature ID {creature_id} cannot hunt.", hunted_list, df

        else:
            suitable_creatures_hunting = scan_coordinates(hunting_distance, df, creature['id'])

            if suitable_creatures_hunting:
                matches = []
                for other_creature in suitable_creatures_hunting:
                    huntable_creature_list = creature['huntable_creatures']
                    if isinstance(huntable_creature_list, str):
                        if '[' in huntable_creature_list:
                            huntable_creature_list = eval(huntable_creature_list)
                        else:
                            huntable_creature_list = [x.strip() for x in huntable_creature_list.split(',')]
                    
                    if other_creature['species'] in huntable_creature_list:
                        matches.append(other_creature)

                if matches:
                    selected_prey = random.choice(matches)
                    message = f"Hunting Creature ID {creature_id} ({creature['species']}), Hunted Creature ID {selected_prey['id']} ({selected_prey['species']})"
                    
                    df = df[df['id'] != selected_prey['id']]
                    
                    new_creature = Living(creature['species'], random.choice(['male', 'female']))
                    hunted_list.append(new_creature)
                    
                    df.to_csv(file_path, index=False)
                    
                    return message, hunted_list, df
    except Exception as e:
        pass
    
    return "", hunted_list, df

def move_creature(df, creature_id):
    try:
        creature = df.loc[df['id'] == creature_id].iloc[0]
        movement_distance = distances.get(creature['species'], [1])[0]
        
        x, y = location_to_int(creature['location'])
        move_x = random.randint(-movement_distance, movement_distance)
        move_y = random.randint(-movement_distance, movement_distance)
        
        while abs(move_x) + abs(move_y) > movement_distance:
            move_x = random.randint(-movement_distance, movement_distance)
            move_y = random.randint(-movement_distance, movement_distance)
        
        new_x = max(0, min(499, x + move_x))
        new_y = max(0, min(499, y + move_y))
        
        df.loc[df['id'] == creature_id, 'location'] = f"[{new_x}, {new_y}]"
        return f"Creature ID {creature_id} moved to new location: [{new_x}, {new_y}]"
    except Exception as e:
        return f"Error: {e}"

def simulation_step(df, id_list):
    creature_status = []
    hunted_list = []
    born_list = []
    
    if not id_list:
        return "Error: Cannot proceed because id_list is empty.", df, hunted_list, born_list
    
    for creature_id in id_list:
        try:
            creature = df[df['id'] == creature_id].iloc[0]
            
            mating_message, new_born = check_mating_for_creature(df, creature_id)
            if mating_message:
                creature_status.append(mating_message)
                born_list.extend(new_born)
                df = load_data(force_reload=True)
            
            hunting_message, new_hunted, df = check_hunting_for_creature(df, creature_id)
            if hunting_message:
                creature_status.append(hunting_message)
                hunted_list.extend(new_hunted)
            
            move_message = move_creature(df, creature_id)
            creature_status.append(move_message)
            
        except Exception as e:
            creature_status.append(f"Error {creature_id}: {e}")
    
    df.to_csv(file_path, index=False)
    return "\n".join(creature_status), df, hunted_list, born_list

def show_map(df):
    if df.empty:
        st.warning("There are no creatures in the simulation. Please add creatures first.")
        return

    species_colors = {
        'sheep': '#FFFFFF',
        'wolf': '#808080',
        'cow': '#8B4513',
        'chicken': '#FFD700',
        'rooster': '#FF6347',
        'lion': '#FFA500',
        'hunter': '#FF0000'
    }

    species_icons = {
        'sheep': '🐑',
        'wolf': '🐺',
        'cow': '🐄',
        'chicken': '🐔',
        'rooster': '🐓',
        'lion': '🦁',
        'hunter': '🏹'
    }

    df['x'] = 0
    df['y'] = 0
    
    for idx, row in df.iterrows():
        try:
            x, y = location_to_int(row['location'])
            df.at[idx, 'x'] = x
            df.at[idx, 'y'] = y
        except:
            st.error(f"Location conversion error: {row['location']}")

    fig = px.scatter(
        df,
        x='x',
        y='y',
        color='species',
        color_discrete_map=species_colors,
        hover_data=['id', 'species', 'gender'],
        title='Ecosystem Map'
    )

    fig.update_layout(
        width=800,
        height=800,
        xaxis_range=[0, 500],
        yaxis_range=[0, 500]
    )

    with tab1:
        st.plotly_chart(fig)

        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                species_distribution = df['species'].value_counts()
                st.subheader("Species Distribution")
                fig_species = px.pie(values=species_distribution.values, names=species_distribution.index)
                st.plotly_chart(fig_species)

            with col2:
                gender_distribution = df['gender'].value_counts()
                st.subheader("Gender Distribution")
                fig_gender = px.pie(values=gender_distribution.values, names=gender_distribution.index)
                st.plotly_chart(fig_gender)

        with tab3:
            st.dataframe(df)

st.sidebar.header("Steps to Display")
steps_to_display = st.sidebar.multiselect(
    "Which steps do you want to display?",
    options=list(range(0, 101, 10)),
    default=[0, 50, 100]
)

if 'step_data' not in st.session_state:
    st.session_state.step_data = {}

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Start Simulation"):
        try:
            df = load_data(force_reload=True)
            st.session_state.step_data = {}
            
            if df.empty:
                st.warning("There are no creatures in the simulation. Please add creatures first.")
            else:
                with st.spinner('Simulation running...'):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    current_df = df.copy()
                    
                    for i in range(101):
                        id_list = current_df['id'].tolist()
                        status_message, current_df, hunted_list, born_list = simulation_step(current_df, id_list)
                        
                        progress = (i + 1) / 101
                        progress_bar.progress(progress)
                        
                        if i in steps_to_display:
                            st.session_state.step_data[i] = current_df.copy()
                        
                        status_text.text(f"Step {i}/100")
                    
                    st.success("Simulation completed!")
        except Exception as e:
            st.error(f"Simulation error: {e}")

with col2:
    if st.button("⏹️ Stop Simulation"):
        st.warning("Simulation stopped!")

with col3:
    if st.session_state.step_data:
        selected_step = st.selectbox(
            "Step to display",
            options=sorted(st.session_state.step_data.keys())
        )
        
        if selected_step is not None:
            selected_df = st.session_state.step_data[selected_step]
            
            show_map(selected_df)
            
            with tab2:
                col1, col2 = st.columns(2)
                
                with col1:
                    species_distribution = selected_df['species'].value_counts()
                    st.subheader(f"Species Distribution (Step {selected_step})")
                    fig_species = px.pie(values=species_distribution.values, names=species_distribution.index)
                    st.plotly_chart(fig_species)

                with col2:
                    gender_distribution = selected_df['gender'].value_counts()
                    st.subheader(f"Gender Distribution (Step {selected_step})")
                    fig_gender = px.pie(values=gender_distribution.values, names=gender_distribution.index)
                    st.plotly_chart(fig_gender)

            with tab3:
                st.dataframe(selected_df)