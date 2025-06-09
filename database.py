import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
import psycopg2
import re
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


# Set page configuration
st.set_page_config(page_title="Zomato Restaurant orders Analytics Dashboard", page_icon="🍽", layout="wide")

# Inject CSS to change cursor to pointer in multiselect dropdowns
st.markdown("""
    <style>
            background-color: white;
        .stMultiSelect > div, .stMultiSelect div[data-baseweb="popover"] {
            cursor: pointer !important;
        }
        .stSelectbox > div {
            cursor: pointer !important;
        }
    </style>
""", unsafe_allow_html=True)

# Page title
st.markdown("""<div style="background-color: #FF4C4C; padding: 1.5rem; border-radius: 10px; color: white; text-align: center;">
    <p style="font-size: 32px;">📈 Zomato Restaurant Orders Analytics Dashboard</p>
    </div>""", unsafe_allow_html=True)

st.markdown("This dashboard provides insights into restaurant orders, including key metrics, top items, and revenue analysis📈💰📊")

# PostgreSQL connection
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    user="postgres",
    password="123456",  # Replace with your actual PostgreSQL password
    database="Sql_project"  # Replace with your actual database name
)
c = conn.cursor()

# Fetch data from PostgreSQL
def view_all_data():
    c.execute('SELECT * FROM zomato_orders')
    data = c.fetchall()
    return data

result = view_all_data()
df = pd.DataFrame(result, columns=[
    "order_id", "order_date", "order_time", "customer_id", "menu_item_id", "quantity", "price",
    "item_name", "cuisine_type", "price_2", "restaurant_id", "restaurant_name", "rating",
    "city_id", "city_name", "state_name", "region", "fullname", "age", "gender"
])
st.markdown(
    """
    <style>
    body {
        background-color: green;
    }
    .stApp {
        background-color: green;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Convert 'order_date' to datetime format
df["order_date"] = pd.to_datetime(df["order_date"])

# Sidebar UI
st.sidebar.image("data/Logo 1.png", caption="Zomato Restaurant Orders Analytics", use_container_width=True)
st.sidebar.header("Please Select Filter")

# Date range selector
min_date = df["order_date"].min()
max_date = df["order_date"].max()
start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

Region = st.sidebar.multiselect(
    "Select Region",
    options=df["region"].unique(),
    default=list(df["region"].unique())
)
city = st.sidebar.multiselect(
    "Select City",
    options=df["city_name"].unique(),
    default=list(df["city_name"].unique())
)
state = st.sidebar.multiselect(
    
    "Select State",
    options=df["state_name"].unique(),
    default=list(df["state_name"].unique())
)
restaurant = st.sidebar.multiselect(
    "Select Restaurant",
    options=df["restaurant_name"].unique(),
    default=list(df["restaurant_name"].unique())
)
menu = st.sidebar.multiselect(
    "Select Item Name",
    options=df["item_name"].unique(),
    default=list(df["item_name"].unique())
)
cuisine = st.sidebar.multiselect(
    "Select Cuisine Type",
    options=df["cuisine_type"].unique(),
    default=list(df["cuisine_type"].unique())
)

# Filter the data based on all selected filters
df_selection = df.query(
    "region == @Region & city_name == @city & state_name == @state & restaurant_name == @restaurant & item_name == @menu & cuisine_type == @cuisine"
)

# Filter by date range
df_selection = df_selection[
    (df_selection["order_date"] >= pd.to_datetime(start_date)) &
    (df_selection["order_date"] <= pd.to_datetime(end_date))
]
def Home():
    with st.expander("Click Here to View Data"):
        show_data = st.multiselect("Filter", df_selection.columns, default=[])
        if show_data:
            st.write(df_selection[show_data])
        else:
            st.write(df_selection)

    # Corrected KPI Calculations
    total_income = df_selection["price"].sum()
    total_orders = df_selection["order_id"].nunique()
    total_items_sold = df_selection["quantity"].sum()
    average_rating = df_selection["rating"].mean()

# KPI Display with Red Background Cards
    tot1, tot2, tot3, tot4 = st.columns(4, gap='large')

    with tot1:
        st.markdown(f"""
            <div style="background-color: #FF4C4C; padding: 1.5rem; border-radius: 10px; color: white; text-align: center;">
                <div style="font-size: 2rem;">💵</div>
                <h4>Total Income</h4>
                <p style="font-size: 1.8rem; font-weight: bold;">₹{total_income * total_items_sold:,.0f}</p>
            </div>
        """, unsafe_allow_html=True)

    with tot2:
        st.markdown(f"""
            <div style="background-color: #FF4C4C; padding: 1.5rem; border-radius: 10px; color: white; text-align: center;">
                <div style="font-size: 2rem;">📦</div>
                <h4>Total Orders</h4>
                <p style="font-size: 1.8rem; font-weight: bold;">{total_orders}</p>
            </div>
        """, unsafe_allow_html=True)

    with tot3:
        st.markdown(f"""
            <div style="background-color: #FF4C4C; padding: 1.5rem; border-radius: 10px; color: white; text-align: center;">
                <div style="font-size: 2rem;">🍽️</div>
                <h4>Total Items Sold</h4>
                <p style="font-size: 1.8rem; font-weight: bold;">{total_items_sold}</p>
            </div>
        """, unsafe_allow_html=True)

    with tot4:
        st.markdown(f"""
            <div style="background-color: #FF4C4C; padding: 1.5rem; border-radius: 10px; color: white; text-align: center;">
                <div style="font-size: 2rem;">⭐</div>
                <h4>Average Rating</h4>
                <p style="font-size: 1.8rem; font-weight: bold;">{average_rating:.2f}</p>
            </div>
        """, unsafe_allow_html=True)



def graphs():
    st.markdown("""
        <div style= "text-align: center; margin: 3rem 0 2rem 0;">
                <h1 style="color:white; font-size: 2.5rem; font-weight: 700; text-shadow: 2px 2px 8px grba(0,0,0,0.3); margin-bottom: 1rem;">
                    📊 Advanced Analytics & Visualizations
                </h1>
                <p style="color: blue; font-size:1.1rem;">
                    This Charts Shows The Total Analysis Of The Zomatos Restaurant's Orders
                </p>
        </div>
""", unsafe_allow_html=True)
    def create_chart_container(chart_func, delay="0s"):
        st.markdown(f"""
            <div class="plot-container fade-in" style ="animation-delay: {delay};">
        """, unsafe_allow_html=True)
        chart_func()
        st.markdown("</div", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        def revenue_chart():

            daily_revenue =  df_selection.groupby('order_date')['price'].sum().reset_index()
            daily_revenue = daily_revenue.sort_values('order_date')

            fig_revenue = px.line(
                daily_revenue,
                x = 'order_date',
                y = 'price',
                title='📈 Daily Revenue Trend',
                labels={'price': 'Revenue (₹)', 'order_date': 'Date'},
                color_discrete_sequence=['#FF6B6B']
            )
            fig_revenue.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family='Poppins'),
                title_font_size=20,
                title_x=0.5,
                title_font_color='white',
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            fig_revenue.update_traces(line_width=4, hovertemplate='<b>Date:</b> %{x}<br><b>Revenue:</b> ₹%{y:,.0f}<extra></extra>')
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        create_chart_container(revenue_chart, "0.09s")
    with col2:
        def items_chart():
            # Top 10 Items by Revenue
            top_items = df_selection.groupby('item_name')['price'].sum().reset_index()
            top_items = top_items.sort_values('price', ascending=False).head(10)
            
            fig_items = px.bar(
                top_items, 
                x='price', 
                y='item_name',
                orientation='h',
                title='🍽️ Top 10 Items by Revenue',
                labels={'price': 'Revenue (₹)', 'item_name': 'Menu Item'},
                color='price',
                color_continuous_scale='viridis'
            )
            fig_items.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family='Poppins'),
                title_font_size=20,
                title_x=0.5,
                title_font_color='white',
                yaxis={'categoryorder':'total ascending'},
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis2=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            fig_items.update_traces(hovertemplate='<b>Item:</b> %{y}<br><b>Revenue:</b> ₹%{x:,.0f}<extra></extra>')
            st.plotly_chart(fig_items, use_container_width=True)
        
        create_chart_container(items_chart, "0.2s")
    col3, col4 = st.columns(2, gap="large")

    col3, col4 = st.columns(2, gap="large")
    
    with col3:
        def restaurant_chart():
            # Restaurant Performance (Revenue vs Rating)
            restaurant_stats = df_selection.groupby('restaurant_name').agg({
                'price': 'sum',
                'rating': 'mean',
                'order_id': 'nunique'
            }).reset_index()
            
            fig_restaurant = px.scatter(
                restaurant_stats,
                x='rating',
                y='price',
                size='order_id',
                hover_name='restaurant_name',
                title='🏪 Restaurant Performance: Revenue vs Rating',
                labels={'price': 'Total Revenue (₹)', 'rating': 'Average Rating', 'order_id': 'Orders Count'},
                color='price',
                color_continuous_scale='plasma',
                size_max=60
            )
            fig_restaurant.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family='Poppins'),
                title_font_size=20,
                title_x=0.5,
                title_font_color='white',
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            fig_restaurant.update_traces(
                hovertemplate='<b>Restaurant:</b> %{hovertext}<br><b>Rating:</b> %{x:.2f}<br><b>Revenue:</b> ₹%{y:,.0f}<br><b>Orders:</b> %{marker.size}<extra></extra>'
            )
            st.plotly_chart(fig_restaurant, use_container_width=True)
        
        create_chart_container(restaurant_chart, "0.3s")
    
    with col4:
        def cuisine_chart():
            # Cuisine Type Distribution
            cuisine_revenue = df_selection.groupby('cuisine_type')['price'].sum().reset_index()
            
            fig_cuisine = px.pie(
                cuisine_revenue,
                values='price',
                names='cuisine_type',
                title='🌍 Revenue Distribution by Cuisine Type',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_cuisine.update_layout(
                font=dict(color='white', family='Poppins'),
                title_font_size=20,
                title_x=0.5,
                title_font_color='white',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            fig_cuisine.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>Cuisine:</b> %{label}<br><b>Revenue:</b> ₹%{value:,.0f}<br><b>Percentage:</b> %{percent}<extra></extra>',
                textfont_color='white'
            )
            st.plotly_chart(fig_cuisine, use_container_width=True)
        
        create_chart_container(cuisine_chart, "0.4s")
def graphs():
    """
    Function to display outstanding visualizations with live connections to data
    """
    st.markdown("## 📊 Analytics & Visualizations")
    
    # Add button to show/hide all graphs
    show_all_graphs = st.button("📈 Show All Graphs Analytics", type="primary", use_container_width=True)
    
    # Add button for individual graph analysis
    st.markdown("---")
    
    # Use session state to maintain the individual analysis state
    if 'show_individual_analysis' not in st.session_state:
        st.session_state.show_individual_analysis = False
    
    # Toggle button for individual analysis
    if st.button("🔍 Click Here for Individual Graph Analysis", type="secondary", use_container_width=True):
        st.session_state.show_individual_analysis = not st.session_state.show_individual_analysis
    
    # Individual graph selection - show when button is toggled ON
    if st.session_state.show_individual_analysis:
        st.markdown("### 📊 Select Individual Graph for Detailed Analysis")
        
        # Graph options
        graph_options = {
            "📈 Daily Revenue Trend": "revenue_trend",
            "🍽️ Top 10 Items by Revenue": "top_items",
            "🏪 Restaurant Performance: Revenue vs Rating": "restaurant_performance",
            "🌍 Revenue Distribution by Cuisine Type": "cuisine_distribution",
            "👥 Revenue by Age Group & Gender": "age_gender",
            "🗺️ Regional Performance: Revenue & Rating": "regional_performance",
            "🕐 Orders Distribution by Hour": "hourly_orders",
            "📅 Monthly Revenue & Orders Trend": "monthly_trend",
            "💰 Price Distribution": "price_distribution",
            "⭐ Rating Distribution": "rating_distribution"
        }
        
        # Add a close button for individual analysis
        col_close, col_select = st.columns([1, 4])
        with col_close:
            if st.button("❌ Close", help="Close individual analysis"):
                st.session_state.show_individual_analysis = False
                st.rerun()
        
        with col_select:
            selected_graph = st.selectbox(
                "Choose a graph to analyze:",
                options=list(graph_options.keys()),
                index=0,
                help="Select a specific graph to view with detailed insights",
                key="graph_selector"
            )
        
        # Display selected graph with analysis
        if selected_graph:
            col_graph, col_insights = st.columns([2, 1])
            
            with col_graph:
                st.markdown(f"### {selected_graph}")
                
                # Generate the selected graph
                if graph_options[selected_graph] == "revenue_trend":
                    daily_revenue = df_selection.groupby('order_date')['price'].sum().reset_index()
                    daily_revenue = daily_revenue.sort_values('order_date')
                    
                    fig_revenue = px.line(
                        daily_revenue, 
                        x='order_date', 
                        y='price',
                        title='📈 Daily Revenue Trend',
                        labels={'price': 'Revenue (₹)', 'order_date': 'Date'},
                        color_discrete_sequence=['#FF6B6B']
                    )
                    fig_revenue.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#2E86AB'),
                        title_font_size=18,
                        title_x=0.5
                    )
                    fig_revenue.update_traces(line_width=3)
                    st.plotly_chart(fig_revenue, use_container_width=True)
                
                elif graph_options[selected_graph] == "top_items":
                    top_items = df_selection.groupby('item_name')['price'].sum().reset_index()
                    top_items = top_items.sort_values('price', ascending=False).head(10)
                    
                    fig_items = px.bar(
                        top_items, 
                        x='price', 
                        y='item_name',
                        orientation='h',
                        title='🍽️ Top 10 Items by Revenue',
                        labels={'price': 'Revenue (₹)', 'item_name': 'Menu Item'},
                        color='price',
                        color_continuous_scale='viridis'
                    )
                    fig_items.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#2E86AB'),
                        title_font_size=18,
                        title_x=0.5,
                        yaxis={'categoryorder':'total ascending'}
                    )
                    fig_items.update_traces(line_width=3)
                    st.plotly_chart(fig_items, use_container_width=True)
                
                elif graph_options[selected_graph] == "restaurant_performance":
                    restaurant_stats = df_selection.groupby('restaurant_name').agg({
                        'price': 'sum',
                        'rating': 'mean',
                        'order_id': 'nunique'
                    }).reset_index()
                    
                    fig_restaurant = px.scatter(
                        restaurant_stats,
                        x='rating',
                        y='price',
                        size='order_id',
                        hover_name='restaurant_name',
                        title='🏪 Restaurant Performance: Revenue vs Rating',
                        labels={'price': 'Total Revenue (₹)', 'rating': 'Average Rating', 'order_id': 'Orders Count'},
                        color='price',
                        color_continuous_scale='plasma',
                        size_max=60
                    )
                    fig_restaurant.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#2E86AB'),
                        title_font_size=18,
                        title_x=0.5
                    )
                    st.plotly_chart(fig_restaurant, use_container_width=True)
                
                elif graph_options[selected_graph] == "cuisine_distribution":
                    cuisine_revenue = df_selection.groupby('cuisine_type')['price'].sum().reset_index()
                    
                    fig_cuisine = px.pie(
                        cuisine_revenue,
                        values='price',
                        names='cuisine_type',
                        title='🌍 Revenue Distribution by Cuisine Type',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_cuisine.update_layout(
                        font=dict(color='#2E86AB'),
                        title_font_size=18,
                        title_x=0.5
                    )
                    fig_cuisine.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                    )
                    st.plotly_chart(fig_cuisine, use_container_width=True)
                
                elif graph_options[selected_graph] == "age_gender":
                    df_selection['age_group'] = pd.cut(df_selection['age'], 
                                                     bins=[0, 25, 35, 45, 55, 100], 
                                                     labels=['18-25', '26-35', '36-45', '46-55', '55+'])
                    age_analysis = df_selection.groupby(['age_group', 'gender'])['price'].sum().reset_index()
                    
                    fig_age = px.bar(
                        age_analysis,
                        x='age_group',
                        y='price',
                        color='gender',
                        title='👥 Revenue by Age Group & Gender',
                        labels={'price': 'Revenue (₹)', 'age_group': 'Age Group'},
                        color_discrete_sequence=['#E74C3C', '#3498DB'],
                        barmode='group'
                    )
                    fig_age.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#2E86AB'),
                        title_font_size=18,
                        title_x=0.5
                    )
                    st.plotly_chart(fig_age, use_container_width=True)
                
                elif graph_options[selected_graph] == "regional_performance":
                    region_stats = df_selection.groupby('region').agg({
                        'price': 'sum',
                        'order_id': 'nunique',
                        'rating': 'mean'
                    }).reset_index()
                    
                    fig_region = go.Figure()
                    
                    fig_region.add_trace(go.Bar(
                        name='Revenue',
                        x=region_stats['region'],
                        y=region_stats['price'],
                        yaxis='y',
                        offsetgroup=1,
                        marker_color='#FF9F43'
                    ))
                    
                    fig_region.add_trace(go.Scatter(
                        name='Avg Rating',
                        x=region_stats['region'],
                        y=region_stats['rating'],
                        yaxis='y2',
                        mode='lines+markers',
                        line_color='#E74C3C',
                        marker_size=8
                    ))
                    
                    fig_region.update_layout(
                        title='🗺️ Regional Performance: Revenue & Rating',
                        xaxis_title='Region',
                        yaxis=dict(title='Revenue (₹)', side='left'),
                        yaxis2=dict(title='Average Rating', side='right', overlaying='y'),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#2E86AB'),
                        title_font_size=18,
                        title_x=0.5,
                        legend=dict(x=0.02, y=0.98)
                    )
                    st.plotly_chart(fig_region, use_container_width=True)
                
                elif graph_options[selected_graph] == "hourly_orders":
                    df_selection['hour'] = pd.to_datetime(df_selection['order_time'], format='%H:%M:%S').dt.hour
                    hourly_orders = df_selection.groupby('hour')['order_id'].nunique().reset_index()
                    
                    fig_hourly = px.bar(
                        hourly_orders,
                        x='hour',
                        y='order_id',
                        title='🕐 Orders Distribution by Hour',
                        labels={'order_id': 'Number of Orders', 'hour': 'Hour of Day'},
                        color='order_id',
                        color_continuous_scale='blues'
                    )
                    fig_hourly.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#2E86AB'),
                        title_font_size=18,
                        title_x=0.5
                    )
                    st.plotly_chart(fig_hourly, use_container_width=True)
                
                elif graph_options[selected_graph] == "monthly_trend":
                    df_selection['order_date'] = pd.to_datetime(df_selection['order_date'], errors='coerce')
                    df_selection['month'] = df_selection['order_date'].dt.month_name()
                    monthly_trend = df_selection.groupby('month').agg({
                        'price': 'sum',
                        'order_id': 'nunique'
                    }).reset_index()
                    
                    fig_monthly = make_subplots(specs=[[{"secondary_y": True}]])
                    
                    fig_monthly.add_trace(
                        go.Bar(name='Revenue', x=monthly_trend['month'], y=monthly_trend['price'], 
                              marker_color='#9B59B6', opacity=0.8),
                        secondary_y=False,
                    )
                    
                    fig_monthly.add_trace(
                        go.Scatter(name='Orders', x=monthly_trend['month'], y=monthly_trend['order_id'],
                                  mode='lines+markers', line_color='#E67E22', marker_size=8),
                        secondary_y=True,
                    )
                    
                    fig_monthly.update_xaxes(title_text="Month")
                    fig_monthly.update_yaxes(title_text="Revenue (₹)", secondary_y=False)
                    fig_monthly.update_yaxes(title_text="Number of Orders", secondary_y=True)
                    
                    fig_monthly.update_layout(
                        title_text="📅 Monthly Revenue & Orders Trend",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#2E86AB'),
                        title_font_size=18,
                        title_x=0.5
                    )
                    st.plotly_chart(fig_monthly, use_container_width=True)
                
                elif graph_options[selected_graph] == "price_distribution":
                    fig_price_dist = px.histogram(
                        df_selection,
                        x='price',
                        nbins=30,
                        title='💰 Price Distribution',
                        labels={'price': 'Price (₹)', 'count': 'Frequency'},
                        color_discrete_sequence=['#1ABC9C']
                    )
                    fig_price_dist.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#2E86AB'),
                        title_font_size=18,
                        title_x=0.5
                    )
                    st.plotly_chart(fig_price_dist, use_container_width=True)
                
                elif graph_options[selected_graph] == "rating_distribution":
                    rating_dist = df_selection['rating'].value_counts().sort_index().reset_index()
                    rating_dist.columns = ['rating', 'count']
                    
                    fig_rating_dist = px.bar(
                        rating_dist,
                        x='rating',
                        y='count',
                        title='⭐ Rating Distribution',
                        labels={'count': 'Number of Orders', 'rating': 'Rating'},
                        color='rating',
                        color_continuous_scale='RdYlGn'
                    )
                    fig_rating_dist.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#2E86AB'),
                        title_font_size=18,
                        title_x=0.5
                    )
                    st.plotly_chart(fig_rating_dist, use_container_width=True)
            
            with col_insights:
                st.markdown("### 💡 Insights & Recommendations")
                
                # Generate insights based on selected graph
                if graph_options[selected_graph] == "rating_distribution":
                    # Best rating analysis
                    best_rating_data = df_selection[df_selection['rating'] == df_selection['rating'].max()]
                    best_restaurant = best_rating_data.groupby('restaurant_name')['order_id'].count().idxmax()
                    best_item = best_rating_data.groupby('item_name')['order_id'].count().idxmax()
                    best_city = best_rating_data.groupby('city_name')['order_id'].count().idxmax()
                    best_region = best_rating_data.groupby('region')['order_id'].count().idxmax()
                    
                    st.success("🏆 **Best Rating Analysis**")
                    st.write(f"**🏪 Top Restaurant:** {best_restaurant}")
                    st.write(f"**🍽️ Popular Item:** {best_item}")
                    st.write(f"**🌆 City:** {best_city}")
                    st.write(f"**🗺️ Region:** {best_region}")
                    
                    avg_rating = df_selection['rating'].mean()
                    st.info(f"📊 **Average Rating:** {avg_rating:.2f}/5.0")
                    
                    high_rating_percent = (df_selection['rating'] >= 4.0).mean() * 100
                    st.info(f"⭐ **High Ratings (4+):** {high_rating_percent:.1f}%")
                
                elif graph_options[selected_graph] == "top_items":
                    top_item_data = df_selection.groupby('item_name')['price'].sum().reset_index()
                    top_item = top_item_data.loc[top_item_data['price'].idxmax()]
                    
                    # Find restaurants and locations for top item
                    top_item_locations = df_selection[df_selection['item_name'] == top_item['item_name']]
                    popular_restaurant = top_item_locations.groupby('restaurant_name')['order_id'].count().idxmax()
                    popular_city = top_item_locations.groupby('city_name')['order_id'].count().idxmax()
                    popular_region = top_item_locations.groupby('region')['order_id'].count().idxmax()
                    
                    st.success("🍽️ **Top Revenue Item Analysis**")
                    st.write(f"**🥇 Best Item:** {top_item['item_name']}")
                    st.write(f"**💰 Revenue:** ₹{top_item['price']:,.0f}")
                    st.write(f"**🏪 Popular At:** {popular_restaurant}")
                    st.write(f"**🌆 City:** {popular_city}")
                    st.write(f"**🗺️ Region:** {popular_region}")
                
                elif graph_options[selected_graph] == "restaurant_performance":
                    restaurant_stats = df_selection.groupby('restaurant_name').agg({
                        'price': 'sum',
                        'rating': 'mean',
                        'order_id': 'nunique'
                    }).reset_index()
                    
                    best_performer = restaurant_stats.loc[restaurant_stats['price'].idxmax()]
                    highest_rated = restaurant_stats.loc[restaurant_stats['rating'].idxmax()]
                    
                    # Get location info
                    best_location = df_selection[df_selection['restaurant_name'] == best_performer['restaurant_name']]
                    city = best_location['city_name'].iloc[0]
                    region = best_location['region'].iloc[0]
                    
                    st.success("🏪 **Restaurant Performance Analysis**")
                    st.write(f"**💰 Highest Revenue:** {best_performer['restaurant_name']}")
                    st.write(f"**⭐ Highest Rated:** {highest_rated['restaurant_name']} ({highest_rated['rating']:.2f}/5)")
                    st.write(f"**📍 Location:** {city}, {region}")
                    st.write(f"**📊 Total Orders:** {best_performer['order_id']}")
                
                elif graph_options[selected_graph] == "cuisine_distribution":
                    cuisine_revenue = df_selection.groupby('cuisine_type')['price'].sum().reset_index()
                    top_cuisine = cuisine_revenue.loc[cuisine_revenue['price'].idxmax()]
                    
                    # Find best locations for top cuisine
                    cuisine_locations = df_selection[df_selection['cuisine_type'] == top_cuisine['cuisine_type']]
                    top_city = cuisine_locations.groupby('city_name')['price'].sum().idxmax()
                    top_region = cuisine_locations.groupby('region')['price'].sum().idxmax()
                    top_restaurant = cuisine_locations.groupby('restaurant_name')['price'].sum().idxmax()
                    
                    st.success("🌍 **Cuisine Analysis**")
                    st.write(f"**🥇 Top Cuisine:** {top_cuisine['cuisine_type']}")
                    st.write(f"**💰 Revenue:** ₹{top_cuisine['price']:,.0f}")
                    st.write(f"**🏪 Best Restaurant:** {top_restaurant}")
                    st.write(f"**🌆 Top City:** {top_city}")
                    st.write(f"**🗺️ Top Region:** {top_region}")
                
                elif graph_options[selected_graph] == "regional_performance":
                    region_stats = df_selection.groupby('region').agg({
                        'price': 'sum',
                        'rating': 'mean',
                        'order_id': 'nunique'
                    }).reset_index()
                    
                    top_revenue_region = region_stats.loc[region_stats['price'].idxmax()]
                    top_rated_region = region_stats.loc[region_stats['rating'].idxmax()]
                    
                    st.success("🗺️ **Regional Performance Analysis**")
                    st.write(f"**💰 Highest Revenue Region:** {top_revenue_region['region']}")
                    st.write(f"**⭐ Highest Rated Region:** {top_rated_region['region']} ({top_rated_region['rating']:.2f}/5)")
                    st.write(f"**📊 Total Orders:** {top_revenue_region['order_id']}")
                
                elif graph_options[selected_graph] == "hourly_orders":
                    df_selection['hour'] = pd.to_datetime(df_selection['order_time'], format='%H:%M:%S').dt.hour
                    hourly_stats = df_selection.groupby('hour').agg({
                        'order_id': 'nunique',
                        'price': 'sum'
                    }).reset_index()
                    
                    peak_hour = hourly_stats.loc[hourly_stats['order_id'].idxmax()]
                    revenue_hour = hourly_stats.loc[hourly_stats['price'].idxmax()]
                    
                    st.success("🕐 **Time Analysis**")
                    st.write(f"**📈 Peak Order Hour:** {peak_hour['hour']}:00 ({peak_hour['order_id']} orders)")
                    st.write(f"**💰 Peak Revenue Hour:** {revenue_hour['hour']}:00 (₹{revenue_hour['price']:,.0f})")
                    
                    if peak_hour['hour'] < 12:
                        time_period = "Morning"
                    elif peak_hour['hour'] < 17:
                        time_period = "Afternoon"
                    else:
                        time_period = "Evening"
                    
                    st.info(f"🌅 **Peak Period:** {time_period}")
                
                elif graph_options[selected_graph] == "monthly_trend":
                    df_selection['order_date'] = pd.to_datetime(df_selection['order_date'], errors='coerce')
                    df_selection['month'] = df_selection['order_date'].dt.month_name()
                    monthly_stats = df_selection.groupby('month').agg({
                        'price': 'sum',
                        'order_id': 'nunique'
                    }).reset_index()
                    
                    best_month = monthly_stats.loc[monthly_stats['price'].idxmax()]
                    
                    st.success("📅 **Monthly Performance**")
                    st.write(f"**🏆 Best Month:** {best_month['month']}")
                    st.write(f"**💰 Revenue:** ₹{best_month['price']:,.0f}")
                    st.write(f"**📊 Orders:** {best_month['order_id']}")
                
                elif graph_options[selected_graph] == "price_distribution":
                    avg_price = df_selection['price'].mean()
                    median_price = df_selection['price'].median()
                    expensive_items = df_selection[df_selection['price'] > avg_price * 1.5]
                    
                    st.success("💰 **Price Analysis**")
                    st.write(f"**📊 Average Price:** ₹{avg_price:.0f}")
                    st.write(f"**📊 Median Price:** ₹{median_price:.0f}")
                    
                    if len(expensive_items) > 0:
                        premium_item = expensive_items.groupby('item_name')['order_id'].count().idxmax()
                        premium_restaurant = expensive_items.groupby('restaurant_name')['order_id'].count().idxmax()
                        st.write(f"**💎 Premium Item:** {premium_item}")
                        st.write(f"**🏪 Premium Restaurant:** {premium_restaurant}")
                
                elif graph_options[selected_graph] == "age_gender":
                    df_selection['age_group'] = pd.cut(df_selection['age'], 
                                                     bins=[0, 25, 35, 45, 55, 100], 
                                                     labels=['18-25', '26-35', '36-45', '46-55', '55+'])
                    age_gender_stats = df_selection.groupby(['age_group', 'gender'])['price'].sum().reset_index()
                    top_segment = age_gender_stats.loc[age_gender_stats['price'].idxmax()]
                    
                    st.success("👥 **Demographic Analysis**")
                    st.write(f"**🎯 Top Segment:** {top_segment['age_group']} {top_segment['gender']}")
                    st.write(f"**💰 Revenue:** ₹{top_segment['price']:,.0f}")
                    
                    # Additional insights
                    gender_revenue = df_selection.groupby('gender')['price'].sum()
                    dominant_gender = gender_revenue.idxmax()
                    st.write(f"**👤 Dominant Gender:** {dominant_gender}")
                
                elif graph_options[selected_graph] == "revenue_trend":
                    daily_revenue = df_selection.groupby('order_date')['price'].sum().reset_index()
                    best_day = daily_revenue.loc[daily_revenue['price'].idxmax()]
                    
                    st.success("📈 **Revenue Trend Analysis**")
                    st.write(f"**🏆 Best Day:** {best_day['order_date']}")
                    st.write(f"**💰 Revenue:** ₹{best_day['price']:,.0f}")
                    
                    avg_daily_revenue = daily_revenue['price'].mean()
                    st.info(f"📊 **Average Daily Revenue:** ₹{avg_daily_revenue:,.0f}")
    
    # Only display all graphs if button is clicked
    elif show_all_graphs:
        # Row 1: Revenue and Orders Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily Revenue Trend
            daily_revenue = df_selection.groupby('order_date')['price'].sum().reset_index()
            daily_revenue = daily_revenue.sort_values('order_date')
            
            fig_revenue = px.line(
                daily_revenue, 
                x='order_date', 
                y='price',
                title='📈 Daily Revenue Trend',
                labels={'price': 'Revenue (₹)', 'order_date': 'Date'},
                color_discrete_sequence=['#FF6B6B']
            )
            fig_revenue.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#2E86AB'),
                title_font_size=18,
                title_x=0.5
            )
            fig_revenue.update_traces(line_width=3, hovertemplate='<b>Date:</b> %{x}<br><b>Revenue:</b> ₹%{y:,.0f}<extra></extra>')
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        with col2:
            # Top 10 Items by Revenue
            top_items = df_selection.groupby('item_name')['price'].sum().reset_index()
            top_items = top_items.sort_values('price', ascending=False).head(10)
            
            fig_items = px.bar(
                top_items, 
                x='price', 
                y='item_name',
                orientation='h',
                title='🍽️ Top 10 Items by Revenue',
                labels={'price': 'Revenue (₹)', 'item_name': 'Menu Item'},
                color='price',
                color_continuous_scale='viridis'
            )
            fig_items.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#2E86AB'),
                title_font_size=18,
                title_x=0.5,
                yaxis={'categoryorder':'total ascending'}
            )
            fig_items.update_traces(hovertemplate='<b>Item:</b> %{y}<br><b>Revenue:</b> ₹%{x:,.0f}<extra></extra>')
            st.plotly_chart(fig_items, use_container_width=True)
        
        # Row 2: Restaurant and Cuisine Analysis
        col3, col4 = st.columns(2)

        with col3:
            # Restaurant Performance (Revenue vs Rating)
            restaurant_stats = df_selection.groupby('restaurant_name').agg({
                'price': 'sum',
                'rating': 'mean',
                'order_id': 'nunique'
            }).reset_index()
            
            fig_restaurant = px.scatter(
                restaurant_stats,
                x='rating',
                y='price',
                size='order_id',
                hover_name='restaurant_name',
                title='🏪 Restaurant Performance: Revenue vs Rating',
                labels={'price': 'Total Revenue (₹)', 'rating': 'Average Rating', 'order_id': 'Orders Count'},
                color='price',
                color_continuous_scale='plasma',
                size_max=60
            )
            fig_restaurant.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#2E86AB'),
                title_font_size=18,
                title_x=0.5
            )
            fig_restaurant.update_traces(
                hovertemplate='<b>Restaurant:</b> %{hovertext}<br><b>Rating:</b> %{x:.2f}<br><b>Revenue:</b> ₹%{y:,.0f}<br><b>Orders:</b> %{marker.size}<extra></extra>'
            )
            st.plotly_chart(fig_restaurant, use_container_width=True)

        with col4:
            # Cuisine Type Distribution
            cuisine_revenue = df_selection.groupby('cuisine_type')['price'].sum().reset_index()
            
            fig_cuisine = px.pie(
                cuisine_revenue,
                values='price',
                names='cuisine_type',
                title='🌍 Revenue Distribution by Cuisine Type',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_cuisine.update_layout(
                font=dict(color='#2E86AB'),
                title_font_size=18,
                title_x=0.5
            )
            fig_cuisine.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>Cuisine:</b> %{label}<br><b>Revenue:</b> ₹%{value:,.0f}<br><b>Percentage:</b> %{percent}<extra></extra>'
            )
            st.plotly_chart(fig_cuisine, use_container_width=True)

        # Row 3: Customer Demographics and Geographic Analysis
        col5, col6 = st.columns(2)

        with col5:
            # Age Group Analysis
            df_selection['age_group'] = pd.cut(df_selection['age'], 
                                            bins=[0, 25, 35, 45, 55, 100], 
                                            labels=['18-25', '26-35', '36-45', '46-55', '55+'])
            age_analysis = df_selection.groupby(['age_group', 'gender'])['price'].sum().reset_index()
            
            fig_age = px.bar(
                age_analysis,
                x='age_group',
                y='price',
                color='gender',
                title='👥 Revenue by Age Group & Gender',
                labels={'price': 'Revenue (₹)', 'age_group': 'Age Group'},
                color_discrete_sequence=['#E74C3C', '#3498DB'],
                barmode='group'
            )
            fig_age.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#2E86AB'),
                title_font_size=18,
                title_x=0.5
            )
            fig_age.update_traces(hovertemplate='<b>Age Group:</b> %{x}<br><b>Gender:</b> %{legendgroup}<br><b>Revenue:</b> ₹%{y:,.0f}<extra></extra>')
            st.plotly_chart(fig_age, use_container_width=True)

        with col6:
            # Regional Performance
            region_stats = df_selection.groupby('region').agg({
                'price': 'sum',
                'order_id': 'nunique',
                'rating': 'mean'
            }).reset_index()
            
            fig_region = go.Figure()
            
            fig_region.add_trace(go.Bar(
                name='Revenue',
                x=region_stats['region'],
                y=region_stats['price'],
                yaxis='y',
                offsetgroup=1,
                marker_color='#FF9F43',
                hovertemplate='<b>Region:</b> %{x}<br><b>Revenue:</b> ₹%{y:,.0f}<extra></extra>'
            ))
            
            fig_region.add_trace(go.Scatter(
                name='Avg Rating',
                x=region_stats['region'],
                y=region_stats['rating'],
                yaxis='y2',
                mode='lines+markers',
                line_color='#E74C3C',
                marker_size=8,
                hovertemplate='<b>Region:</b> %{x}<br><b>Avg Rating:</b> %{y:.2f}<extra></extra>'
            ))
            
            fig_region.update_layout(
                title='🗺️ Regional Performance: Revenue & Rating',
                xaxis_title='Region',
                yaxis=dict(title='Revenue (₹)', side='left'),
                yaxis2=dict(title='Average Rating', side='right', overlaying='y'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#2E86AB'),
                title_font_size=18,
                title_x=0.5,
                legend=dict(x=0.02, y=0.98)
            )
            
            st.plotly_chart(fig_region, use_container_width=True)

        # Row 4: Time-based Analysis
        col7, col8 = st.columns(2)

        with col7:
            # Orders by Hour
            df_selection['hour'] = pd.to_datetime(df_selection['order_time'], format='%H:%M:%S').dt.hour
            hourly_orders = df_selection.groupby('hour')['order_id'].nunique().reset_index()
            
            fig_hourly = px.bar(
                hourly_orders,
                x='hour',
                y='order_id',
                title='🕐 Orders Distribution by Hour',
                labels={'order_id': 'Number of Orders', 'hour': 'Hour of Day'},
                color='order_id',
                color_continuous_scale='blues'
            )
            fig_hourly.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#2E86AB'),
                title_font_size=18,
                title_x=0.5
            )
            fig_hourly.update_traces(
                hovertemplate='<b>Hour:</b> %{x}<br><b>Orders:</b> %{y}<extra></extra>'
            )
            st.plotly_chart(fig_hourly, use_container_width=True)

        with col8:
            # Orders by Day of Week
            df_selection['weekday'] = pd.to_datetime(df_selection['order_date']).dt.day_name()
            weekday_orders = df_selection.groupby('weekday')['order_id'].nunique().reindex([
                'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
            ]).reset_index()
            
            fig_weekday = px.bar(
                weekday_orders,
                x='weekday',
                y='order_id',
                title='📆 Orders by Day of the Week',
                labels={'order_id': 'Number of Orders', 'weekday': 'Day'},
                color='order_id',
                color_continuous_scale='greens'
            )
            fig_weekday.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#2E86AB'),
                title_font_size=18,
                title_x=0.5
            )
            fig_weekday.update_traces(
                hovertemplate='<b>Day:</b> %{x}<br><b>Orders:</b> %{y}<extra></extra>'
            )
            st.plotly_chart(fig_weekday, use_container_width=True)

        # Row 5: Customer Loyalty and Spending Patterns
        col9, col10 = st.columns(2)

        with col9:
            # Repeat Customers
            repeat_customers = df_selection.groupby('customer_id')['order_id'].nunique().reset_index()
            repeat_customers['is_repeat'] = repeat_customers['order_id'] > 1
            repeat_stats = repeat_customers['is_repeat'].value_counts().reset_index()
            repeat_stats.columns = ['Repeat Customer', 'Count']
            repeat_stats['Repeat Customer'] = repeat_stats['Repeat Customer'].map({True: 'Yes', False: 'No'})
            
            fig_repeat = px.pie(
                repeat_stats,
                names='Repeat Customer',
                values='Count',
                title='🔁 Repeat Customers Distribution',
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig_repeat.update_traces(
                textinfo='percent+label',
                hovertemplate='<b>Repeat:</b> %{label}<br><b>Count:</b> %{value}<br><b>Percentage:</b> %{percent}<extra></extra>'
            )
            st.plotly_chart(fig_repeat, use_container_width=True)

        with col10:
            # High-Spending Customers
            top_customers = df_selection.groupby('customer_id')['price'].sum().reset_index()
            top_customers = top_customers.sort_values('price', ascending=False).head(10)
            
            fig_customers = px.bar(
                top_customers,
                x='price',
                y='customer_id',
                orientation='h',
                title='💸 Top 10 High-Spending Customers',
                labels={'price': 'Total Spend (₹)', 'customer_id': 'Customer ID'},
                color='price',
                color_continuous_scale='magma'
            )
            fig_customers.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#2E86AB'),
                title_font_size=18,
                title_x=0.5,
                yaxis={'categoryorder':'total ascending'}
            )
            fig_customers.update_traces(
                hovertemplate='<b>Customer ID:</b> %{y}<br><b>Total Spend:</b> ₹%{x:,.0f}<extra></extra>'
            )
            st.plotly_chart(fig_customers, use_container_width=True)

# Main execution
Home()
st.markdown("---")
graphs()