import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta, date
import json
import base64
from abc import ABC, abstractmethod
import re

st.set_page_config(
    page_title="🥗 Advanced Nutrition Tracker",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #2E8B57;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
        margin: 1rem 0;
    }
    
    .warning-message {
        padding: 1rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        color: #856404;
        margin: 1rem 0;
    }
    
    .sidebar-info {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class FoodItem(ABC):
    def __init__(self, name, calories_per_100g, protein, carbs, fat, fiber=0, sugar=0):
        self.name = name
        self.calories_per_100g = calories_per_100g
        self.protein = protein
        self.carbs = carbs
        self.fat = fat
        self.fiber = fiber
        self.sugar = sugar
    
    @abstractmethod
    def get_category(self):
        pass
    
    def calculate_nutrition(self, serving_size_g):
        multiplier = serving_size_g / 100
        return {
            'calories': self.calories_per_100g * multiplier,
            'protein': self.protein * multiplier,
            'carbs': self.carbs * multiplier,
            'fat': self.fat * multiplier,
            'fiber': self.fiber * multiplier,
            'sugar': self.sugar * multiplier
        }

class Fruit(FoodItem):
    def __init__(self, name, calories_per_100g, protein, carbs, fat, fiber=0, sugar=0, vitamin_c=0):
        super().__init__(name, calories_per_100g, protein, carbs, fat, fiber, sugar)
        self.vitamin_c = vitamin_c
    
    def get_category(self):
        return "🍎 Fruits"

class Vegetable(FoodItem):
    def __init__(self, name, calories_per_100g, protein, carbs, fat, fiber=0, sugar=0, iron=0):
        super().__init__(name, calories_per_100g, protein, carbs, fat, fiber, sugar)
        self.iron = iron
    
    def get_category(self):
        return "🥬 Vegetables"

class Protein(FoodItem):
    def __init__(self, name, calories_per_100g, protein, carbs, fat, fiber=0, sugar=0, is_lean=True):
        super().__init__(name, calories_per_100g, protein, carbs, fat, fiber, sugar)
        self.is_lean = is_lean
    
    def get_category(self):
        return "🍗 Proteins"

class Grain(FoodItem):
    def __init__(self, name, calories_per_100g, protein, carbs, fat, fiber=0, sugar=0, is_whole_grain=False):
        super().__init__(name, calories_per_100g, protein, carbs, fat, fiber, sugar)
        self.is_whole_grain = is_whole_grain
    
    def get_category(self):
        return "🌾 Grains"

class Dairy(FoodItem):
    def __init__(self, name, calories_per_100g, protein, carbs, fat, fiber=0, sugar=0, calcium=0):
        super().__init__(name, calories_per_100g, protein, carbs, fat, fiber, sugar)
        self.calcium = calcium
    
    def get_category(self):
        return "🥛 Dairy"

class NutritionError(Exception):
    pass

class InvalidServingSizeError(NutritionError):
    pass

class InvalidGoalError(NutritionError):
    pass

def initialize_session_state():
    if 'food_database' not in st.session_state:
        st.session_state.food_database = create_food_database()
    
    if 'daily_entries' not in st.session_state:
        st.session_state.daily_entries = {}
    
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'name': 'User',
            'age': 25,
            'weight': 70,
            'height': 170,
            'activity_level': 'Moderate',
            'goal': 'Maintain Weight',
            'daily_calories': 2000,
            'daily_protein': 150,
            'daily_carbs': 250,
            'daily_fat': 67
        }
    
    if 'weekly_goals' not in st.session_state:
        st.session_state.weekly_goals = {
            'water_glasses': 8,
            'exercise_minutes': 150,
            'sleep_hours': 8
        }

def create_food_database():
    foods = {}
    
    fruits_data = [
        ("Apple", 52, 0.3, 14, 0.2, 2.4, 10.4, 4.6),
        ("Banana", 89, 1.1, 23, 0.3, 2.6, 12.2, 8.7),
        ("Orange", 47, 0.9, 12, 0.1, 2.4, 9.4, 53.2),
        ("Strawberry", 32, 0.7, 8, 0.3, 2.0, 4.9, 58.8),
        ("Mango", 60, 0.8, 15, 0.4, 1.6, 13.7, 36.4),
        ("Grapes", 62, 0.6, 16, 0.2, 0.9, 16.0, 3.2)
    ]
    
    for name, cal, prot, carb, fat, fib, sug, vit_c in fruits_data:
        foods[name] = Fruit(name, cal, prot, carb, fat, fib, sug, vit_c)
    
    vegetables_data = [
        ("Broccoli", 34, 2.8, 7, 0.4, 2.6, 1.5, 1.8),
        ("Spinach", 23, 2.9, 3.6, 0.4, 2.2, 0.4, 2.7),
        ("Carrot", 41, 0.9, 10, 0.2, 2.8, 4.7, 0.9),
        ("Bell Pepper", 31, 1.0, 7, 0.3, 2.5, 4.2, 0.4),
        ("Tomato", 18, 0.9, 3.9, 0.2, 1.2, 2.6, 1.2),
        ("Cucumber", 16, 0.7, 4, 0.1, 0.5, 1.7, 0.2)
    ]
    
    for name, cal, prot, carb, fat, fib, sug, iron in vegetables_data:
        foods[name] = Vegetable(name, cal, prot, carb, fat, fib, sug, iron)
    
    proteins_data = [
        ("Chicken Breast", 165, 31, 0, 3.6, 0, 0, True),
        ("Salmon", 208, 20, 0, 13, 0, 0, True),
        ("Eggs", 155, 13, 1.1, 11, 0, 0.7, True),
        ("Tofu", 76, 8, 1.9, 4.8, 0.3, 0.6, True),
        ("Ground Beef", 250, 26, 0, 15, 0, 0, False),
        ("Tuna", 144, 30, 0, 1, 0, 0, True)
    ]
    
    for name, cal, prot, carb, fat, fib, sug, lean in proteins_data:
        foods[name] = Protein(name, cal, prot, carb, fat, fib, sug, lean)
    
    grains_data = [
        ("Brown Rice", 111, 2.6, 23, 0.9, 1.8, 0.4, True),
        ("White Rice", 130, 2.7, 28, 0.3, 0.4, 0.1, False),
        ("Quinoa", 120, 4.4, 22, 1.9, 2.8, 0.9, True),
        ("Oats", 389, 17, 66, 7, 11, 0.99, True),
        ("Whole Wheat Bread", 247, 13, 41, 4.2, 7, 6.8, True),
        ("White Bread", 265, 9, 49, 3.2, 2.7, 5.7, False)
    ]
    
    for name, cal, prot, carb, fat, fib, sug, whole in grains_data:
        foods[name] = Grain(name, cal, prot, carb, fat, fib, sug, whole)
    
    dairy_data = [
        ("Milk (2%)", 50, 3.4, 5, 2, 0, 5, 120),
        ("Greek Yogurt", 59, 10, 3.6, 0.4, 0, 3.6, 110),
        ("Cheddar Cheese", 402, 25, 1.3, 33, 0, 0.5, 721),
        ("Cottage Cheese", 98, 11, 3.4, 4.3, 0, 2.7, 83),
        ("Almond Milk", 17, 0.6, 0.6, 1.5, 0.5, 0, 184)
    ]
    
    for name, cal, prot, carb, fat, fib, sug, calcium in dairy_data:
        foods[name] = Dairy(name, cal, prot, carb, fat, fib, sug, calcium)
    
    return foods

def calculate_bmr(weight, height, age, gender):
    if gender == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return bmr

def calculate_daily_calories(bmr, activity_level):
    activity_multipliers = {
        "Sedentary": 1.2,
        "Light": 1.375,
        "Moderate": 1.55,
        "Active": 1.725,
        "Very Active": 1.9
    }
    return int(bmr * activity_multipliers.get(activity_level, 1.55))

def validate_serving_size(serving_size):
    try:
        size = float(serving_size)
        if size <= 0 or size > 10000:
            raise InvalidServingSizeError("Serving size must be between 0 and 10000 grams")
        return size
    except ValueError:
        raise InvalidServingSizeError("Please enter a valid number for serving size")

def create_nutrition_pie_chart(nutrition_data):
    macros = ['Protein', 'Carbs', 'Fat']
    values = [nutrition_data['protein'] * 4, nutrition_data['carbs'] * 4, nutrition_data['fat'] * 9]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    fig = go.Figure(data=[go.Pie(
        labels=macros,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textfont_size=12,
        hovertemplate='<b>%{label}</b><br>Calories: %{value:.0f}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title="Daily Macronutrient Distribution (Calories)",
        font=dict(size=14),
        showlegend=True,
        height=400
    )
    
    return fig

def create_progress_bars(current, target, label):
    percentage = min((current / target * 100) if target > 0 else 0, 100)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = current,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"{label}"},
        delta = {'reference': target},
        gauge = {
            'axis': {'range': [None, target * 1.2]},
            'bar': {'color': "#1f77b4"},
            'steps': [
                {'range': [0, target * 0.8], 'color': "lightgray"},
                {'range': [target * 0.8, target], 'color': "yellow"},
                {'range': [target, target * 1.2], 'color': "red"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': target}}))
    
    fig.update_layout(height=250)
    return fig

def create_weekly_trend_chart(daily_entries):
    if not daily_entries:
        return None
    
    dates = []
    calories = []
    
    for i in range(6, -1, -1):
        date_key = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        dates.append(date_key)
        
        if date_key in daily_entries:
            daily_cal = sum(entry['nutrition']['calories'] for entry in daily_entries[date_key])
            calories.append(daily_cal)
        else:
            calories.append(0)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=calories,
        mode='lines+markers',
        name='Daily Calories',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_hline(
        y=st.session_state.user_profile['daily_calories'], 
        line_dash="dash", 
        line_color="green",
        annotation_text="Target Calories"
    )
    
    fig.update_layout(
        title="Weekly Calorie Intake Trend",
        xaxis_title="Date",
        yaxis_title="Calories",
        height=400,
        showlegend=True
    )
    
    return fig

def main():
    initialize_session_state()
    
    st.markdown('<h1 class="main-header">🥗 Advanced Nutrition Tracker</h1>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("🏠 Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["📊 Dashboard", "🍽️ Food Entry", "👤 Profile", "📈 Analytics", "🎯 Goals", "⚙️ Settings"]
        )
        
        st.markdown("---")
        
        st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
        st.subheader("📋 Quick Stats")
        
        today = datetime.now().strftime("%Y-%m-%d")
        if today in st.session_state.daily_entries:
            today_entries = st.session_state.daily_entries[today]
            total_calories = sum(entry['nutrition']['calories'] for entry in today_entries)
            st.metric("Today's Calories", f"{total_calories:.0f}")
            st.metric("Target Calories", f"{st.session_state.user_profile['daily_calories']}")
            
            if total_calories > 0:
                progress = (total_calories / st.session_state.user_profile['daily_calories']) * 100
                st.progress(min(progress / 100, 1.0))
        else:
            st.info("No entries for today yet!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🍽️ Food Entry":
        show_food_entry()
    elif page == "👤 Profile":
        show_profile()
    elif page == "📈 Analytics":
        show_analytics()
    elif page == "🎯 Goals":
        show_goals()
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard():
    st.header("📊 Nutrition Dashboard")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    col1, col2, col3, col4 = st.columns(4)
    
    if today in st.session_state.daily_entries:
        today_entries = st.session_state.daily_entries[today]
        
        total_nutrition = {
            'calories': sum(entry['nutrition']['calories'] for entry in today_entries),
            'protein': sum(entry['nutrition']['protein'] for entry in today_entries),
            'carbs': sum(entry['nutrition']['carbs'] for entry in today_entries),
            'fat': sum(entry['nutrition']['fat'] for entry in today_entries),
            'fiber': sum(entry['nutrition']['fiber'] for entry in today_entries)
        }
        
        with col1:
            st.metric(
                "🔥 Calories", 
                f"{total_nutrition['calories']:.0f}",
                f"{total_nutrition['calories'] - st.session_state.user_profile['daily_calories']:.0f}"
            )
        
        with col2:
            st.metric(
                "🥩 Protein", 
                f"{total_nutrition['protein']:.1f}g",
                f"{total_nutrition['protein'] - st.session_state.user_profile['daily_protein']:.1f}g"
            )
        
        with col3:
            st.metric(
                "🍞 Carbs", 
                f"{total_nutrition['carbs']:.1f}g",
                f"{total_nutrition['carbs'] - st.session_state.user_profile['daily_carbs']:.1f}g"
            )
        
        with col4:
            st.metric(
                "🥑 Fat", 
                f"{total_nutrition['fat']:.1f}g",
                f"{total_nutrition['fat'] - st.session_state.user_profile['daily_fat']:.1f}g"
            )
        
        st.subheader("📈 Daily Progress")
        
        progress_col1, progress_col2 = st.columns(2)
        
        with progress_col1:
            if total_nutrition['calories'] > 0:
                fig_pie = create_nutrition_pie_chart(total_nutrition)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Add some food entries to see the macronutrient breakdown!")
        
        with progress_col2:
            st.subheader("🎯 Target Progress")
            
            calorie_progress = (total_nutrition['calories'] / st.session_state.user_profile['daily_calories']) * 100
            st.progress(min(calorie_progress / 100, 1.0))
            st.caption(f"Calories: {calorie_progress:.1f}% of target")
            
            protein_progress = (total_nutrition['protein'] / st.session_state.user_profile['daily_protein']) * 100
            st.progress(min(protein_progress / 100, 1.0))
            st.caption(f"Protein: {protein_progress:.1f}% of target")
            
            carbs_progress = (total_nutrition['carbs'] / st.session_state.user_profile['daily_carbs']) * 100
            st.progress(min(carbs_progress / 100, 1.0))
            st.caption(f"Carbs: {carbs_progress:.1f}% of target")
            
            fat_progress = (total_nutrition['fat'] / st.session_state.user_profile['daily_fat']) * 100
            st.progress(min(fat_progress / 100, 1.0))
            st.caption(f"Fat: {fat_progress:.1f}% of target")
        
        st.subheader("🍽️ Today's Food Log")
        
        if today_entries:
            food_df = pd.DataFrame([
                {
                    'Time': entry['time'],
                    'Food': entry['food_name'],
                    'Serving (g)': entry['serving_size'],
                    'Calories': f"{entry['nutrition']['calories']:.0f}",
                    'Protein (g)': f"{entry['nutrition']['protein']:.1f}",
                    'Carbs (g)': f"{entry['nutrition']['carbs']:.1f}",
                    'Fat (g)': f"{entry['nutrition']['fat']:.1f}"
                }
                for entry in today_entries
            ])
            
            st.dataframe(food_df, use_container_width=True)
            
            if st.checkbox("🗑️ Enable entry removal"):
                entry_to_remove = st.selectbox(
                    "Select entry to remove:",
                    range(len(today_entries)),
                    format_func=lambda i: f"{today_entries[i]['time']} - {today_entries[i]['food_name']}"
                )
                
                if st.button("Remove Entry", type="secondary"):
                    del st.session_state.daily_entries[today][entry_to_remove]
                    st.rerun()
        
    else:
        st.info("🌅 No food entries for today yet! Start by adding your first meal.")
        with col1:
            st.metric("🔥 Calories", "0", "0")
        with col2:
            st.metric("🥩 Protein", "0g", "0g")
        with col3:
            st.metric("🍞 Carbs", "0g", "0g")
        with col4:
            st.metric("🥑 Fat", "0g", "0g")
    
    st.subheader("📅 Weekly Calorie Trend")
    weekly_chart = create_weekly_trend_chart(st.session_state.daily_entries)
    if weekly_chart:
        st.plotly_chart(weekly_chart, use_container_width=True)
    else:
        st.info("Start logging food to see your weekly trends!")

def show_food_entry():
    st.header("🍽️ Food Entry")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔍 Search Food Database")
        
        search_term = st.text_input("Search for food:", placeholder="Type food name...")
        
        categories = list(set(food.get_category() for food in st.session_state.food_database.values()))
        selected_category = st.selectbox("Filter by category:", ["All"] + categories)
        
        filtered_foods = {}
        for name, food in st.session_state.food_database.items():
            if search_term.lower() in name.lower() or not search_term:
                if selected_category == "All" or food.get_category() == selected_category:
                    filtered_foods[name] = food
        
        if filtered_foods:
            selected_food_name = st.selectbox("Select food:", list(filtered_foods.keys()))
            selected_food = filtered_foods[selected_food_name]
        else:
            st.warning("No foods found matching your criteria.")
            selected_food = None
    
    with col2:
        if selected_food:
            st.subheader("📋 Food Information")
            st.write(f"**Category:** {selected_food.get_category()}")
            st.write(f"**Calories per 100g:** {selected_food.calories_per_100g}")
            st.write(f"**Protein:** {selected_food.protein}g")
            st.write(f"**Carbs:** {selected_food.carbs}g")
            st.write(f"**Fat:** {selected_food.fat}g")
            st.write(f"**Fiber:** {selected_food.fiber}g")
    
    if selected_food:
        st.markdown("---")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("⚖️ Serving Information")
            
            serving_size = st.number_input(
                "Serving size (grams):",
                min_value=0.1,
                max_value=10000.0,
                value=100.0,
                step=1.0,
                help="Enter the weight of your serving in grams"
            )
            
            meal_time = st.selectbox(
                "Meal time:",
                ["Breakfast", "Lunch", "Dinner", "Snack"],
                help="Select which meal this food belongs to"
            )
            
            custom_time = st.time_input("Time:", value=datetime.now().time())
        
        with col2:
            st.subheader("🧮 Nutrition Calculation")
            
            try:
                nutrition = selected_food.calculate_nutrition(serving_size)
                
                nutrition_col1, nutrition_col2 = st.columns(2)
                
                with nutrition_col1:
                    st.metric("🔥 Calories", f"{nutrition['calories']:.0f}")
                    st.metric("🥩 Protein", f"{nutrition['protein']:.1f}g")
                    st.metric("🍞 Carbohydrates", f"{nutrition['carbs']:.1f}g")
                
                with nutrition_col2:
                    st.metric("🥑 Fat", f"{nutrition['fat']:.1f}g")
                    st.metric("🌾 Fiber", f"{nutrition['fiber']:.1f}g")
                    st.metric("🍯 Sugar", f"{nutrition['sugar']:.1f}g")
                
                if nutrition['calories'] > 0:
                    fig = go.Figure(data=[go.Pie(
                        labels=['Protein (cal)', 'Carbs (cal)', 'Fat (cal)'],
                        values=[nutrition['protein']*4, nutrition['carbs']*4, nutrition['fat']*9],
                        hole=0.3,
                        marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1']
                    )])
                    
                    fig.update_layout(
                        title=f"Macronutrient Breakdown ({nutrition['calories']:.0f} total calories)",
                        height=300,
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error calculating nutrition: {str(e)}")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("➕ Add to Food Log", type="primary"):
                try:
                    validate_serving_size(serving_size)
                    
                    today = datetime.now().strftime("%Y-%m-%d")
                    
                    if today not in st.session_state.daily_entries:
                        st.session_state.daily_entries[today] = []
                    
                    entry = {
                        'time': custom_time.strftime("%H:%M"),
                        'meal': meal_time,
                        'food_name': selected_food_name,
                        'serving_size': serving_size,
                        'nutrition': nutrition
                    }
                    
                    st.session_state.daily_entries[today].append(entry)
                    
                    st.success(f"✅ Added {selected_food_name} to your food log!")
                    
                except InvalidServingSizeError as e:
                    st.error(f"❌ {str(e)}")
                
                except Exception as e:
                    st.error(f"❌ Error adding food: {str(e)}")
        
        with col2:
            if st.button("🔄 Reset Form"):
                st.rerun()

def show_profile():
    st.header("👤 User Profile")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Personal Information")
        
        name = st.text_input("Name:", value=st.session_state.user_profile['name'])
        age = st.number_input("Age:", min_value=1, max_value=120, value=st.session_state.user_profile['age'])
        weight = st.number_input("Weight (kg):", min_value=1.0, max_value=500.0, value=float(st.session_state.user_profile['weight']))
        height = st.number_input("Height (cm):", min_value=50.0, max_value=250.0, value=float(st.session_state.user_profile['height']))
        
        gender = st.selectbox("Gender:", ["Male", "Female"], 
                             index=0 if st.session_state.user_profile.get('gender', 'Male') == 'Male' else 1)
        
        activity_level = st.selectbox(
            "Activity Level:",
            ["Sedentary", "Light", "Moderate", "Active", "Very Active"],
            index=["Sedentary", "Light", "Moderate", "Active", "Very Active"].index(st.session_state.user_profile['activity_level'])
        )
        
        goal = st.selectbox(
            "Goal:",
            ["Lose Weight", "Maintain Weight", "Gain Weight"],
            index=["Lose Weight", "Maintain Weight", "Gain Weight"].index(st.session_state.user_profile['goal'])
        )
    
    with col2:
        st.subheader("🎯 Calculated Targets")
        
        bmr = calculate_bmr(weight, height, age, gender)
        daily_calories = calculate_daily_calories(bmr, activity_level)
        
        if goal == "Lose Weight":
            daily_calories = int(daily_calories * 0.8)
        elif goal == "Gain Weight":
            daily_calories = int(daily_calories * 1.2)
        
        daily_protein = weight * 2.2
        daily_fat = daily_calories * 0.25 / 9
        daily_carbs = (daily_calories - (daily_protein * 4) - (daily_fat * 9)) / 4
        
        st.metric("🔥 BMR", f"{bmr:.0f} calories")
        st.metric("📊 Daily Calories", f"{daily_calories} calories")
        st.metric("🥩 Protein Target", f"{daily_protein:.0f}g")
        st.metric("🍞 Carbs Target", f"{daily_carbs:.0f}g")
        st.metric("🥑 Fat Target", f"{daily_fat:.0f}g")
        
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        
        st.markdown("---")
        st.subheader("📏 Body Mass Index")
        st.metric("BMI", f"{bmi:.1f}")
        
        if bmi < 18.5:
            st.warning("⚠️ Underweight")
        elif 18.5 <= bmi < 25:
            st.success("✅ Normal weight")
        elif 25 <= bmi < 30:
            st.warning("⚠️ Overweight")
        else:
            st.error("🚨 Obese")
    
    if st.button("💾 Save Profile", type="primary"):
        st.session_state.user_profile.update({
            'name': name,
            'age': age,
            'weight': weight,
            'height': height,
            'gender': gender,
            'activity_level': activity_level,
            'goal': goal,
            'daily_calories': daily_calories,
            'daily_protein': daily_protein,
            'daily_carbs': daily_carbs,
            'daily_fat': daily_fat
        })
        st.success("✅ Profile saved successfully!")

def show_analytics():
    st.header("📈 Nutrition Analytics")
    
    if not st.session_state.daily_entries:
        st.info("📊 No data available yet. Start logging food to see analytics!")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date:", 
                                  value=datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date:", 
                                value=datetime.now())
    
    filtered_entries = {}
    for date_str, entries in st.session_state.daily_entries.items():
        entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if start_date <= entry_date <= end_date:
            filtered_entries[date_str] = entries
    
    if not filtered_entries:
        st.warning("No data found for the selected date range.")
        return
    
    daily_totals = {}
    for date_str, entries in filtered_entries.items():
        daily_totals[date_str] = {
            'calories': sum(entry['nutrition']['calories'] for entry in entries),
            'protein': sum(entry['nutrition']['protein'] for entry in entries),
            'carbs': sum(entry['nutrition']['carbs'] for entry in entries),
            'fat': sum(entry['nutrition']['fat'] for entry in entries),
            'fiber': sum(entry['nutrition']['fiber'] for entry in entries)
        }
    
    st.subheader("📊 Daily Trends")
    
    dates = list(daily_totals.keys())
    dates.sort()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Calories', 'Protein (g)', 'Carbohydrates (g)', 'Fat (g)'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig.add_trace(
        go.Scatter(x=dates, 
                  y=[daily_totals[d]['calories'] for d in dates],
                  name='Calories',
                  line=dict(color='#FF6B6B', width=2)),
        row=1, col=1
    )
    fig.add_hline(y=st.session_state.user_profile['daily_calories'], 
                  line_dash="dash", line_color="red", row=1, col=1)
    
    fig.add_trace(
        go.Scatter(x=dates, 
                  y=[daily_totals[d]['protein'] for d in dates],
                  name='Protein',
                  line=dict(color='#4ECDC4', width=2)),
        row=1, col=2
    )
    fig.add_hline(y=st.session_state.user_profile['daily_protein'], 
                  line_dash="dash", line_color="green", row=1, col=2)
    
    fig.add_trace(
        go.Scatter(x=dates, 
                  y=[daily_totals[d]['carbs'] for d in dates],
                  name='Carbs',
                  line=dict(color='#45B7D1', width=2)),
        row=2, col=1
    )
    fig.add_hline(y=st.session_state.user_profile['daily_carbs'], 
                  line_dash="dash", line_color="blue", row=2, col=1)
    
    fig.add_trace(
        go.Scatter(x=dates, 
                  y=[daily_totals[d]['fat'] for d in dates],
                  name='Fat',
                  line=dict(color='#96CEB4', width=2)),
        row=2, col=2
    )
    fig.add_hline(y=st.session_state.user_profile['daily_fat'], 
                  line_dash="dash", line_color="orange", row=2, col=2)
    
    fig.update_layout(height=600, showlegend=False, title_text="Nutrition Trends Over Time")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 Period Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    avg_calories = np.mean([daily_totals[d]['calories'] for d in dates])
    avg_protein = np.mean([daily_totals[d]['protein'] for d in dates])
    avg_carbs = np.mean([daily_totals[d]['carbs'] for d in dates])
    avg_fat = np.mean([daily_totals[d]['fat'] for d in dates])
    
    with col1:
        st.metric("📊 Avg Calories", f"{avg_calories:.0f}",
                 f"{avg_calories - st.session_state.user_profile['daily_calories']:.0f}")
    with col2:
        st.metric("🥩 Avg Protein", f"{avg_protein:.1f}g",
                 f"{avg_protein - st.session_state.user_profile['daily_protein']:.1f}g")
    with col3:
        st.metric("🍞 Avg Carbs", f"{avg_carbs:.1f}g",
                 f"{avg_carbs - st.session_state.user_profile['daily_carbs']:.1f}g")
    with col4:
        st.metric("🥑 Avg Fat", f"{avg_fat:.1f}g",
                 f"{avg_fat - st.session_state.user_profile['daily_fat']:.1f}g")
    
    st.subheader("🍎 Food Category Analysis")
    
    category_totals = {}
    for entries in filtered_entries.values():
        for entry in entries:
            food_name = entry['food_name']
            if food_name in st.session_state.food_database:
                category = st.session_state.food_database[food_name].get_category()
                if category not in category_totals:
                    category_totals[category] = {'calories': 0, 'count': 0}
                category_totals[category]['calories'] += entry['nutrition']['calories']
                category_totals[category]['count'] += 1
    
    if category_totals:
        fig_cat = go.Figure(data=[go.Pie(
            labels=list(category_totals.keys()),
            values=[data['calories'] for data in category_totals.values()],
            textinfo='label+percent+value',
            texttemplate='%{label}<br>%{value:.0f} cal<br>%{percent}',
            hovertemplate='<b>%{label}</b><br>Calories: %{value:.0f}<br>Percentage: %{percent}<br>Frequency: %{customdata}<extra></extra>',
            customdata=[data['count'] for data in category_totals.values()]
        )])
        
        fig_cat.update_layout(
            title="Calories by Food Category",
            height=500
        )
        
        st.plotly_chart(fig_cat, use_container_width=True)

def show_goals():
    st.header("🎯 Goals & Achievements")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Achievement Tracking")
        
        today = datetime.now().date()
        streak = 0
        
        for i in range(30):
            check_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            if check_date in st.session_state.daily_entries:
                entries = st.session_state.daily_entries[check_date]
                daily_calories = sum(entry['nutrition']['calories'] for entry in entries)
                target_calories = st.session_state.user_profile['daily_calories']
                
                if 0.9 * target_calories <= daily_calories <= 1.1 * target_calories:
                    streak += 1
                else:
                    break
            else:
                break
        
        st.metric("🔥 Current Streak", f"{streak} days")
        
        st.subheader("📅 Weekly Goals")
        
        water_goal = st.session_state.weekly_goals['water_glasses']
        water_current = st.number_input("Water glasses today:", min_value=0, max_value=20, value=0)
        water_progress = min(water_current / water_goal, 1.0)
        
        st.progress(water_progress)
        st.caption(f"💧 Water: {water_current}/{water_goal} glasses ({water_progress*100:.0f}%)")
        
        exercise_goal = st.session_state.weekly_goals['exercise_minutes']
        exercise_current = st.number_input("Exercise minutes this week:", min_value=0, max_value=1000, value=0)
        exercise_progress = min(exercise_current / exercise_goal, 1.0)
        
        st.progress(exercise_progress)
        st.caption(f"💪 Exercise: {exercise_current}/{exercise_goal} minutes ({exercise_progress*100:.0f}%)")
        
        sleep_goal = st.session_state.weekly_goals['sleep_hours']
        sleep_current = st.number_input("Sleep hours last night:", min_value=0.0, max_value=12.0, value=8.0, step=0.5)
        sleep_progress = min(sleep_current / sleep_goal, 1.0)
        
        st.progress(sleep_progress)
        st.caption(f"😴 Sleep: {sleep_current}/{sleep_goal} hours ({sleep_progress*100:.0f}%)")
    
    with col2:
        st.subheader("🎖️ Badges & Milestones")
        
        badges = []
        
        if streak >= 7:
            badges.append("🏆 Week Warrior")
        if streak >= 30:
            badges.append("🔥 Month Master")
        if streak >= 100:
            badges.append("💎 Century Champion")
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        if today_str in st.session_state.daily_entries:
            today_entries = st.session_state.daily_entries[today_str]
            total_protein = sum(entry['nutrition']['protein'] for entry in today_entries)
            target_protein = st.session_state.user_profile['daily_protein']
            
            if total_protein >= target_protein:
                badges.append("🥩 Protein Power")
            
            total_fiber = sum(entry['nutrition']['fiber'] for entry in today_entries)
            if total_fiber >= 25:
                badges.append("🌾 Fiber Champion")
        
        if badges:
            for badge in badges:
                st.success(badge)
        else:
            st.info("Keep logging food to earn badges! 🏆")
        
        st.subheader("⚙️ Set New Goals")
        
        with st.expander("🎯 Customize Weekly Goals"):
            new_water = st.slider("Daily water glasses:", 1, 15, water_goal)
            new_exercise = st.slider("Weekly exercise minutes:", 30, 500, exercise_goal)
            new_sleep = st.slider("Daily sleep hours:", 6, 12, sleep_goal)
            
            if st.button("💾 Save Goals"):
                st.session_state.weekly_goals.update({
                    'water_glasses': new_water,
                    'exercise_minutes': new_exercise,
                    'sleep_hours': new_sleep
                })
                st.success("Goals updated! 🎉")
        
        st.subheader("💡 Insights")
        
        if len(st.session_state.daily_entries) >= 7:
            recent_days = []
            for i in range(7):
                date_key = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                if date_key in st.session_state.daily_entries:
                    daily_cal = sum(entry['nutrition']['calories'] for entry in st.session_state.daily_entries[date_key])
                    recent_days.append(daily_cal)
            
            if recent_days:
                avg_weekly = np.mean(recent_days)
                target = st.session_state.user_profile['daily_calories']
                
                if avg_weekly < target * 0.9:
                    st.info("💡 You've been eating below your calorie target. Consider adding healthy snacks!")
                elif avg_weekly > target * 1.1:
                    st.warning("💡 You've been exceeding your calorie target. Try smaller portions or lighter meals.")
                else:
                    st.success("💡 Great job staying within your calorie targets! 🎉")

def show_settings():
    st.header("⚙️ Settings & Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Data Export/Import")
        
        if st.button("📤 Export All Data"):
            export_data = {
                'user_profile': st.session_state.user_profile,
                'daily_entries': st.session_state.daily_entries,
                'weekly_goals': st.session_state.weekly_goals,
                'export_timestamp': datetime.now().isoformat()
            }
            
            json_string = json.dumps(export_data, indent=2, default=str)
            b64 = base64.b64encode(json_string.encode()).decode()
            
            st.download_button(
                label="💾 Download JSON File",
                data=json_string,
                file_name=f"nutrition_data_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
            
            st.success("✅ Data prepared for download!")
        
        st.markdown("---")
        uploaded_file = st.file_uploader("📤 Import Data", type=['json'])
        
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                
                if st.button("⚠️ Import Data (This will overwrite current data)"):
                    if 'user_profile' in data:
                        st.session_state.user_profile = data['user_profile']
                    if 'daily_entries' in data:
                        st.session_state.daily_entries = data['daily_entries']
                    if 'weekly_goals' in data:
                        st.session_state.weekly_goals = data['weekly_goals']
                    
                    st.success("✅ Data imported successfully!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error importing data: {str(e)}")
        
        st.subheader("🗑️ Data Management")
        
        if st.checkbox("Enable data clearing (⚠️ Dangerous)"):
            if st.button("🗑️ Clear All Food Entries", type="secondary"):
                st.session_state.daily_entries = {}
                st.success("✅ Food entries cleared!")
                st.rerun()
            
            if st.button("🔄 Reset Profile to Defaults", type="secondary"):
                st.session_state.user_profile = {
                    'name': 'User',
                    'age': 25,
                    'weight': 70,
                    'height': 170,
                    'activity_level': 'Moderate',
                    'goal': 'Maintain Weight',
                    'daily_calories': 2000,
                    'daily_protein': 150,
                    'daily_carbs': 250,
                    'daily_fat': 67
                }
                st.success("✅ Profile reset to defaults!")
                st.rerun()
    
    with col2:
        st.subheader("🍎 Food Database Management")
        
        with st.expander("➕ Add Custom Food"):
            food_name = st.text_input("Food Name:")
            food_category = st.selectbox("Category:", 
                                       ["🍎 Fruits", "🥬 Vegetables", "🍗 Proteins", 
                                        "🌾 Grains", "🥛 Dairy"])
            
            col_a, col_b = st.columns(2)
            with col_a:
                calories = st.number_input("Calories per 100g:", min_value=0.0, value=100.0)
                protein = st.number_input("Protein (g):", min_value=0.0, value=0.0)
                carbs = st.number_input("Carbs (g):", min_value=0.0, value=0.0)
            
            with col_b:
                fat = st.number_input("Fat (g):", min_value=0.0, value=0.0)
                fiber = st.number_input("Fiber (g):", min_value=0.0, value=0.0)
                sugar = st.number_input("Sugar (g):", min_value=0.0, value=0.0)
            
            if st.button("➕ Add Custom Food"):
                if food_name and food_name not in st.session_state.food_database:
                    if food_category == "🍎 Fruits":
                        new_food = Fruit(food_name, calories, protein, carbs, fat, fiber, sugar)
                    elif food_category == "🥬 Vegetables":
                        new_food = Vegetable(food_name, calories, protein, carbs, fat, fiber, sugar)
                    elif food_category == "🍗 Proteins":
                        new_food = Protein(food_name, calories, protein, carbs, fat, fiber, sugar)
                    elif food_category == "🌾 Grains":
                        new_food = Grain(food_name, calories, protein, carbs, fat, fiber, sugar)
                    else:
                        new_food = Dairy(food_name, calories, protein, carbs, fat, fiber, sugar)
                    
                    st.session_state.food_database[food_name] = new_food
                    st.success(f"✅ Added {food_name} to database!")
                else:
                    st.error("❌ Food name is required and must be unique!")
        
        st.subheader("📈 Database Statistics")
        
        category_counts = {}
        for food in st.session_state.food_database.values():
            category = food.get_category()
            category_counts[category] = category_counts.get(category, 0) + 1
        
        for category, count in category_counts.items():
            st.metric(category, count)
        
        st.info(f"📊 Total foods in database: {len(st.session_state.food_database)}")
        
        st.subheader("ℹ️ About This App")
        st.info("""
        🥗 **Advanced Nutrition Tracker v2.0**
        
        **Features:**
        • Comprehensive food database with 30+ foods
        • Object-oriented design with inheritance
        • Dynamic visualizations with Plotly
        • Goal tracking and achievements
        • Data export/import functionality
        • Real-time nutrition calculations
        • BMI and calorie target calculations
        
        **Built with:**
        • Streamlit for web interface
        • Plotly for interactive charts
        • Pandas for data management
        • Object-oriented Python design
        """)

if __name__ == "__main__":
    main()
