"""
PONS AUTO - Web Dashboard
Mobile-responsive web app for managing vehicle inventory and publishing
Works on iOS, Android browsers, and desktop
"""

import streamlit as st
import requests
from datetime import datetime
from PIL import Image
from io import BytesIO
import base64
import os

# Import AI modules
from photo_manager import show_photo_manager
from ai_description import show_ai_description_generator, show_description_library

# Configuration - works locally and in Streamlit Cloud
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001/api/v1")

# Page config - mobile optimized
st.set_page_config(
    page_title="PONS AUTO",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",  # Better for mobile
    menu_items={
        'Get Help': 'https://ponsauto.com/help',
        'Report a bug': 'https://ponsauto.com/bug',
        'About': 'PONS AUTO - Multi-Channel Vehicle Publishing'
    }
)

# Mobile-responsive CSS
st.markdown("""
<style>
    /* Mobile-first responsive design */
    .main {
        padding: 1rem;
    }
    
    /* Large tap targets for mobile */
    .stButton>button {
        width: 100%;
        height: 3rem;
        font-size: 1.1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    
    /* Input fields optimized for mobile */
    .stTextInput>div>div>input {
        font-size: 16px; /* Prevents iOS zoom on focus */
        height: 3rem;
    }
    
    /* Cards with shadows */
    .vehicle-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Success message */
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Mobile header */
    .mobile-header {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #1f2937;
    }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-success { background: #d1fae5; color: #065f46; }
    .badge-warning { background: #fed7aa; color: #92400e; }
    .badge-info { background: #dbeafe; color: #1e40af; }
    
    /* Hide Streamlit branding on mobile */
    @media (max-width: 768px) {
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Deep linking support - check query params
    query_params = st.experimental_get_query_params()
if 'vin' in query_params and not st.session_state.logged_in:
    # Auto-login to demo mode if VIN is in URL
    st.session_state.logged_in = True
    st.session_state.user_email = "demo@ponsauto.com"
    st.session_state.demo_mode = True
if 'view' in query_params:
    st.session_state.active_view = query_params['view']
if 'preview' in query_params:
    # Auto-open preview modal for specific VIN
    st.session_state.preview_vin = query_params['preview']
    if not st.session_state.logged_in:
        st.session_state.logged_in = True
        st.session_state.user_email = "demo@ponsauto.com"
        st.session_state.demo_mode = True
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'feed_connected' not in st.session_state:
    st.session_state.feed_connected = False


def api_request(endpoint, method="GET", data=None, params=None):
    """Make API request with error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    
    if st.session_state.api_key:
        headers["X-API-Key"] = st.session_state.api_key
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None


def login_page():
    """Login/signup page"""
    st.markdown('<div class="mobile-header">🚗 PONS AUTO</div>', unsafe_allow_html=True)
    st.markdown("### Publish Vehicles to Facebook Marketplace")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with tab1:
        st.subheader("Welcome Back")
        email = st.text_input("Email", key="login_email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("🔐 Sign In", use_container_width=True):
            if email and password:
                # For demo, use email as API key (in production, call auth endpoint)
                st.session_state.logged_in = True
                st.session_state.api_key = f"demo-key-{email}"
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Please enter email and password")
    
    with tab2:
        st.subheader("Get Started Free")
        new_email = st.text_input("Email", key="signup_email", placeholder="your@email.com")
        new_password = st.text_input("Password", type="password", key="signup_password")
        dealer_name = st.text_input("Dealership Name", key="dealer_name", 
                                    placeholder="ABC Motors")
        
        if st.button("🚀 Create Account", use_container_width=True):
            if new_email and new_password and dealer_name:
                # Create account
                st.session_state.logged_in = True
                st.session_state.api_key = f"demo-key-{new_email}"
                st.session_state.user_email = new_email
                st.success("✓ Account created! Setting up your dashboard...")
                st.rerun()
            else:
                st.error("Please fill all fields")
    
    # Demo mode
    st.markdown("---")
    if st.button("👀 Try Demo (No signup required)", use_container_width=True):
        st.session_state.logged_in = True
        st.session_state.api_key = "demo-key"
        st.session_state.user_email = "demo@ponsauto.com"
        st.rerun()


def connect_feed_page():
    """Connect inventory feed - mobile friendly"""
    st.markdown('<div class="mobile-header">📡 Connect Your Inventory</div>', 
                unsafe_allow_html=True)
    
    st.info("Connect your dealership website or 3rd party inventory provider")
    
    # Method selection
    method = st.radio(
        "How do you want to connect?",
        ["Paste Feed URL", "Upload File", "Connect to Provider"],
        horizontal=False  # Better for mobile
    )
    
    if method == "Paste Feed URL":
        st.subheader("Enter your inventory feed URL")
        feed_url = st.text_input(
            "Feed URL",
            placeholder="https://yourdealer.com/inventory.xml",
            help="URL to your XML, CSV, or JSON inventory feed"
        )
        
        feed_format = st.selectbox(
            "Format",
            ["Auto-detect", "XML", "CSV", "JSON"]
        )
        
        sync_schedule = st.selectbox(
            "Auto-sync frequency",
            ["Every 4 hours", "Every 6 hours", "Every 12 hours", "Daily", "Manual only"]
        )
        
        if st.button("✓ Connect Feed", use_container_width=True):
            if feed_url:
                with st.spinner("Testing connection..."):
                    # Register feed with API
                    result = api_request("/feeds/register", method="POST", data={
                        "name": f"Feed from {feed_url.split('/')[2]}",
                        "url": feed_url,
                        "format": feed_format.lower(),
                        "schedule": "0 */4 * * *"  # Every 4 hours
                    })
                    
                    if result:
                        st.session_state.feed_connected = True
                        st.success("✓ Feed connected! Syncing vehicles...")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Could not connect to feed. Check URL and try again.")
            else:
                st.warning("Please enter a feed URL")
    
    elif method == "Upload File":
        st.subheader("Upload your inventory file")
        uploaded_file = st.file_uploader(
            "Choose file",
            type=['xml', 'csv', 'json'],
            help="Upload your inventory file (XML, CSV, or JSON)"
        )
        
        if uploaded_file:
            if st.button("📤 Upload & Import", use_container_width=True):
                with st.spinner("Importing vehicles..."):
                    # In production, send file to API
                    st.session_state.feed_connected = True
                    st.success(f"✓ Imported {uploaded_file.name}!")
                    st.rerun()
    
    else:  # Connect to Provider
        st.subheader("Connect to popular providers")
        
        providers = {
            "vAuto": "https://vauto.com",
            "DealerSocket": "https://dealersocket.com",
            "CDK Global": "https://cdkglobal.com",
            "Reynolds & Reynolds": "https://reyrey.com",
            "Dealer.com": "https://dealer.com"
        }
        
        selected_provider = st.selectbox("Select Provider", list(providers.keys()))
        
        provider_username = st.text_input("Provider Username/Account ID")
        provider_api_key = st.text_input("Provider API Key", type="password")
        
        if st.button(f"Connect to {selected_provider}", use_container_width=True):
            if provider_username and provider_api_key:
                with st.spinner(f"Connecting to {selected_provider}..."):
                    st.session_state.feed_connected = True
                    st.success(f"✓ Connected to {selected_provider}!")
                    st.rerun()
            else:
                st.warning("Please enter credentials")
    
    # Skip option
    st.markdown("---")
    if st.button("⏭️ Skip for now (Use demo data)", use_container_width=True):
        st.session_state.feed_connected = True
        st.rerun()


def inventory_dashboard():
    """Main dashboard - mobile responsive"""
    
    # Header with user info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="mobile-header">🚗 My Inventory</div>', 
                    unsafe_allow_html=True)
    with col2:
        if st.button("🚪", help="Logout"):
            st.session_state.clear()
            st.rerun()
    
    st.markdown(f"*Logged in as: {st.session_state.user_email}*")
    st.markdown("---")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Vehicles", "47", delta="+3")
    with col2:
        st.metric("Published", "32", delta="+5")
    with col3:
        st.metric("Pending", "15")
    
    st.markdown("---")
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Vehicles", 
        "🚀 Publish", 
        "� Photos",
        "🤖 AI Descriptions",
        "�📡 Feeds",
        "⚙️ Settings"
    ])
    
    with tab1:
        show_vehicles_tab()
    
    with tab2:
        show_publish_tab()
    
    with tab3:
        show_photo_management_tab()
    
    with tab4:
        show_ai_description_tab()
    
    with tab5:
        show_feeds_tab()
    
    with tab6:
        show_settings_tab()


def show_vehicles_tab():
    """Vehicle list with search and filters"""
    
    # Check for deep link to specific vehicle
    query_params = st.experimental_get_query_params()
    selected_vin = query_params.get('vin', None)
    
    # Check for preview modal trigger
    if 'preview_vin' in st.session_state and st.session_state.preview_vin:
        show_preview_modal(st.session_state.preview_vin)
        # Clear after showing
        st.session_state.preview_vin = None
        if st.button("← Back to Inventory"):
            st.query_params.clear()
            st.rerun()
        return
    
    if selected_vin:
        # Show vehicle detail view
        show_vehicle_detail(selected_vin)
        if st.button("← Back to Inventory"):
            # Clear VIN param
            st.query_params.clear()
            st.rerun()
        return
    
    st.subheader("Vehicle Inventory")
    
    # Search and filters
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("🔍 Search", placeholder="Search by VIN, make, model...")
    with col2:
        filter_status = st.selectbox("Filter", ["All", "Published", "Unpublished"])
    
    # Get vehicles from API
    vehicles_response = api_request("/inventory/vehicles")
    
    # Demo data if API not available
    if not vehicles_response:
        vehicles = [
            {"vin": "1HGCM82633A123456", "year": 2023, "make": "Honda", 
             "model": "Accord", "price": 28500, "mileage": 15000, 
             "published_channels": ["facebook"]},
            {"vin": "5YFBURHE5HP123789", "year": 2022, "make": "Toyota", 
             "model": "Camry", "price": 25900, "mileage": 22000, 
             "published_channels": []},
            {"vin": "1FTFW1ET5EFA12345", "year": 2021, "make": "Ford", 
             "model": "F-150", "price": 35900, "mileage": 18000, 
             "published_channels": ["facebook", "autotrader"]},
        ]
    else:
        vehicles = vehicles_response.get("vehicles", [])
    
    # Display vehicles as mobile-friendly cards
    for vehicle in vehicles:
        with st.container():
            st.markdown(f"""
            <div class="vehicle-card">
                <h3>{vehicle['year']} {vehicle['make']} {vehicle['model']}</h3>
                <p><strong>VIN:</strong> {vehicle['vin']}</p>
                <p><strong>Price:</strong> ${vehicle['price']:,} | 
                   <strong>Mileage:</strong> {vehicle['mileage']:,} mi</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("📱 Publish", key=f"pub_{vehicle['vin']}", 
                           use_container_width=True):
                    st.session_state.selected_vehicle = vehicle
                    st.info(f"Ready to publish {vehicle['year']} {vehicle['make']} {vehicle['model']}")
            with col2:
                st.button("✏️ Edit", key=f"edit_{vehicle['vin']}", 
                         use_container_width=True)
            with col3:
                if st.button("👁️ View", key=f"view_{vehicle['vin']}", 
                         use_container_width=True):
                    # Deep link to vehicle detail
                    st.query_params["vin"] = vehicle['vin']
                    st.rerun()
            with col4:
                # Share button - copies deep link
                share_url = f"{st.get_option('browser.serverAddress')}:{st.get_option('browser.serverPort')}/?vin={vehicle['vin']}"
                if st.button("🔗 Share", key=f"share_{vehicle['vin']}", 
                           use_container_width=True, help="Copy direct link"):
                    st.info(f"📋 Share this link: {share_url}")
            
            # Show published channels
            if vehicle.get('published_channels'):
                badges = " ".join([
                    f'<span class="badge badge-success">✓ {ch.title()}</span>'
                    for ch in vehicle['published_channels']
                ])
                st.markdown(badges, unsafe_allow_html=True)
            
            st.markdown("---")


def show_publish_tab():
    """Publish vehicles to Facebook Marketplace and other channels"""
    st.subheader("🚀 Publish to Channels")
    
    st.info("Select vehicles and channels to publish")
    
    # Get vehicles
    vehicles_response = api_request("/inventory/vehicles")
    
    # Demo data
    vehicles = [
        {"vin": "1HGCM82633A123456", "year": 2023, "make": "Honda", "model": "Accord"},
        {"vin": "5YFBURHE5HP123789", "year": 2022, "make": "Toyota", "model": "Camry"},
        {"vin": "1FTFW1ET5EFA12345", "year": 2021, "make": "Ford", "model": "F-150"},
    ]
    
    # Select vehicles
    st.markdown("### Select Vehicles")
    selected_vehicles = []
    for vehicle in vehicles:
        if st.checkbox(
            f"{vehicle['year']} {vehicle['make']} {vehicle['model']} - {vehicle['vin']}",
            key=f"select_{vehicle['vin']}"
        ):
            selected_vehicles.append(vehicle)
    
    st.markdown("---")
    
    # Select channels
    st.markdown("### Select Publishing Channels")
    
    col1, col2 = st.columns(2)
    with col1:
        publish_facebook = st.checkbox("🔵 Facebook Marketplace", value=True)
        publish_autotrader = st.checkbox("🚗 AutoTrader")
    with col2:
        publish_carscom = st.checkbox("🚙 Cars.com")
        publish_cargurus = st.checkbox("📊 CarGurus")
    
    # Publish button
    st.markdown("---")
    if st.button("🚀 Publish Selected Vehicles", use_container_width=True, 
                 type="primary"):
        if not selected_vehicles:
            st.warning("Please select at least one vehicle")
        elif not any([publish_facebook, publish_autotrader, publish_carscom, publish_cargurus]):
            st.warning("Please select at least one channel")
        else:
            channels = []
            if publish_facebook: channels.append("facebook")
            if publish_autotrader: channels.append("autotrader")
            if publish_carscom: channels.append("cars_com")
            if publish_cargurus: channels.append("cargurus")
            
            with st.spinner("Publishing vehicles..."):
                for vehicle in selected_vehicles:
                    # Call publishing API
                    result = api_request("/publishing/jobs", method="POST", data={
                        "vin": vehicle['vin'],
                        "channels": channels
                    })
                    
                    if result:
                        job_id = result.get('id')
                        # Execute job
                        api_request(f"/publishing/jobs/{job_id}/execute", method="POST")
                
                st.success(f"✅ Published {len(selected_vehicles)} vehicles to {len(channels)} channels!")
                st.balloons()
                
                # Show results
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown("**Published Successfully:**")
                for vehicle in selected_vehicles:
                    st.markdown(f"- {vehicle['year']} {vehicle['make']} {vehicle['model']}")
                st.markdown("</div>", unsafe_allow_html=True)


def show_feeds_tab():
    """Manage connected feeds"""
    st.subheader("📡 Connected Feeds")
    
    # Connected feeds
    feeds = [
        {"name": "Dealership Website", "url": "https://dealer.com/inventory.xml", 
         "status": "Active", "last_sync": "2 hours ago"},
        {"name": "vAuto Export", "url": "https://vauto.com/export.csv", 
         "status": "Active", "last_sync": "4 hours ago"},
    ]
    
    for idx, feed in enumerate(feeds):
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{feed['name']}**")
                st.caption(f"🔗 {feed['url']}")
                st.caption(f"Last synced: {feed['last_sync']}")
            with col2:
                st.markdown(f'<span class="badge badge-success">{feed["status"]}</span>', 
                           unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.button("🔄 Sync Now", key=f"sync_feed_{idx}", 
                         use_container_width=True)
            with col2:
                st.button("⚙️ Edit", key=f"edit_feed_{idx}", 
                         use_container_width=True)
            
            st.markdown("---")
    
    # Add new feed
    if st.button("➕ Add New Feed", use_container_width=True):
        st.session_state.feed_connected = False
        st.rerun()


def show_preview_modal(vin):
    """Show preview modal with desktop and mobile side-by-side views"""
    st.markdown(f'<div class="mobile-header">🔍 Listing Preview</div>', unsafe_allow_html=True)
    st.info(f"Preview for VIN: {vin}")
    
    # Channel selector
    channel = st.selectbox(
        "Select Channel",
        ["Facebook Marketplace", "AutoTrader", "Cars.com", "CarGurus"],
        key="preview_modal_channel"
    )
    
    if st.button("🔍 Generate Preview", use_container_width=True, type="primary"):
        with st.spinner("Generating desktop & mobile previews..."):
            try:
                channel_map = {
                    "Facebook Marketplace": "facebook",
                    "AutoTrader": "autotrader",
                    "Cars.com": "cars_com",
                    "CarGurus": "cargurus"
                }
                
                # Call preview API (mock for now)
                preview_data = {
                    "channel": channel,
                    "listing_title": f"2022 Toyota Camry SE",
                    "price_display": "$28,995",
                    "desktop_view": {
                        "layout": "Wide 2-column",
                        "photo_size": "1200x800px",
                        "description_lines": 10,
                        "visible_features": "All"
                    },
                    "mobile_view": {
                        "layout": "Single column",
                        "photo_size": "800x600px (swipeable)",
                        "description_lines": 5,
                        "visible_features": "Collapsed (tap to expand)"
                    }
                }
                
                st.success(f"✅ Preview generated for {channel}")
                
                # Side-by-side comparison
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🖥️ Desktop View")
                    st.markdown(f"**{preview_data['listing_title']}**")
                    st.markdown(f"## {preview_data['price_display']}")
                    for key, value in preview_data['desktop_view'].items():
                        st.text(f"{key}: {value}")
                
                with col2:
                    st.markdown("### 📱 Mobile View")
                    st.markdown(f"**{preview_data['listing_title']}**")
                    st.markdown(f"## {preview_data['price_display']}")
                    for key, value in preview_data['mobile_view'].items():
                        st.text(f"{key}: {value}")
                
                st.markdown("---")
                st.warning("💡 **Tip:** Mobile users see condensed version, desktop users see full details!")
                
                if st.button(f"🚀 Publish to {channel} Now", use_container_width=True):
                    st.success(f"✅ Published to {channel}!")
                    st.balloons()
                    
            except Exception as e:
                st.error(f"Error generating preview: {str(e)}")


def show_vehicle_detail(vin):
    """Show detailed view for a specific vehicle with publish preview"""
    st.markdown(f'<div class="mobile-header">🚗 Vehicle Details</div>', unsafe_allow_html=True)
    
    # Fetch vehicle data (in production, call API)
    # For demo, use mock data
    vehicle = {
        "vin": vin,
        "year": 2022,
        "make": "Toyota",
        "model": "Camry",
        "trim": "SE",
        "price": 28995,
        "mileage": 25000,
        "stock_number": "TC12345",
        "exterior_color": "Silver",
        "interior_color": "Black",
        "transmission": "Automatic",
        "fuel_type": "Gasoline",
        "body_type": "Sedan",
        "description": "Excellent condition, one owner, clean CarFax",
        "images": [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg"
        ]
    }
    
    # Vehicle info
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Year", vehicle["year"])
        st.metric("Make", vehicle["make"])
        st.metric("Price", f"${vehicle['price']:,}")
    with col2:
        st.metric("Model", vehicle["model"])
        st.metric("Mileage", f"{vehicle['mileage']:,} mi")
        st.metric("Stock #", vehicle["stock_number"])
    
    st.markdown("---")
    
    # Preview section
    st.subheader("📱 Listing Preview")
    st.info("See exactly how this vehicle will appear on each platform before publishing.")
    
    channel = st.selectbox(
        "Select Channel",
        ["Facebook Marketplace", "AutoTrader", "Cars.com", "CarGurus"],
        key="preview_channel"
    )
    
    if st.button("🔍 Generate Preview", use_container_width=True, type="primary"):
        with st.spinner("Generating preview..."):
            # Call preview API endpoint
            channel_map = {
                "Facebook Marketplace": "facebook",
                "AutoTrader": "autotrader",
                "Cars.com": "cars_com",
                "CarGurus": "cargurus"
            }
            
            try:
                # In production: call /api/v1/publishing/preview
                preview_data = {
                    "channel": channel,
                    "listing_title": f"{vehicle['year']} {vehicle['make']} {vehicle['model']}",
                    "listing_description": vehicle["description"],
                    "price_display": f"${vehicle['price']:,}",
                    "photo_count": len(vehicle["images"]),
                    "photos": vehicle["images"],
                    "vehicle_details": {
                        "VIN": vehicle["vin"],
                        "Year": vehicle["year"],
                        "Make": vehicle["make"],
                        "Model": vehicle["model"],
                        "Trim": vehicle.get("trim", "N/A"),
                        "Mileage": f"{vehicle['mileage']:,} miles",
                        "Exterior Color": vehicle.get("exterior_color", "N/A"),
                        "Interior Color": vehicle.get("interior_color", "N/A"),
                    }
                }
                
                # Display preview
                st.success(f"✅ Preview generated for {channel}")
                
                st.markdown("### Listing Title")
                st.markdown(f"**{preview_data['listing_title']}**")
                
                st.markdown("### Price Display")
                st.markdown(f"## {preview_data['price_display']}")
                
                st.markdown("### Description")
                st.markdown(preview_data['listing_description'])
                
                st.markdown("### Photos")
                st.info(f"📸 {preview_data['photo_count']} photos will be displayed in this order:")
                for idx, img_url in enumerate(preview_data['photos'], 1):
                    st.text(f"{idx}. {img_url}")
                
                st.markdown("### Vehicle Details")
                for key, value in preview_data['vehicle_details'].items():
                    st.text(f"{key}: {value}")
                
                st.markdown("---")
                st.warning("💡 **Tip:** This is exactly how dealership customers will see your listing!")
                
                # Quick publish button
                if st.button(f"🚀 Publish to {channel} Now", use_container_width=True):
                    st.success(f"✅ Published to {channel}!")
                    st.balloons()
                    
            except Exception as e:
                st.error(f"Error generating preview: {str(e)}")


def show_photo_management_tab():
    """Photo management with AI features."""
    st.subheader("📸 Photo Management")
    
    # VIN selector
    vin = st.text_input(
        "Vehicle VIN",
        placeholder="Enter VIN to manage photos",
        help="VIN of the vehicle you want to add/edit photos for"
    )
    
    if vin:
        show_photo_manager(vin)
    else:
        st.info("👆 Enter a VIN above to start managing photos")
        
        # Quick tips
        with st.expander("💡 Photo Management Features"):
            st.markdown("""
            **Mobile-Optimized Photo Tools:**
            
            📤 **Upload & Crop**
            - Take photos with your phone camera
            - Choose aspect ratios (16:9, 4:3, 1:1)
            - Adjust JPEG quality
            
            ✨ **AI Background Replacement**
            - Replace backgrounds with AI (GPT-4 + DALL-E 3)
            - Choose from 6 professional styles
            - Process single photos or batch (Select All)
            
            🖼️ **Gallery Management**
            - View all photos in grid
            - Reorder photos
            - Delete unwanted shots
            - See AI-enhanced versions
            
            🎯 **Best Practices:**
            - Upload 8-12 photos per vehicle
            - Include exterior, interior, engine, wheels
            - Use landscape mode for best results
            - AI backgrounds take 10-30 seconds per photo
            """)


def show_ai_description_tab():
    """AI description generator with SEO optimization."""
    st.subheader("🤖 AI Description Generator")
    
    # Tab navigation
    desc_tab1, desc_tab2 = st.tabs(["✨ Generate New", "📚 Saved Descriptions"])
    
    with desc_tab1:
        st.markdown("### Create SEO-Optimized Description")
        
        # Vehicle selector
        col1, col2 = st.columns(2)
        with col1:
            vin_input = st.text_input("Vehicle VIN", placeholder="1HGCM82633A123456")
        with col2:
            if st.button("🔍 Load Vehicle Data", use_container_width=True):
                if vin_input:
                    st.info("Loading vehicle data...")
        
        if vin_input:
            # Demo vehicle data (in production, fetch from API)
            demo_vehicle = {
                "vin": vin_input,
                "year": 2023,
                "make": "Honda",
                "model": "Accord",
                "trim": "Sport",
                "mileage": 15000,
                "price": 28500,
                "condition": "Excellent",
                "features": [
                    "Sunroof",
                    "Leather Seats",
                    "Navigation System",
                    "Backup Camera",
                    "Bluetooth"
                ]
            }
            
            show_ai_description_generator(demo_vehicle)
        else:
            st.info("👆 Enter a VIN to generate AI description")
            
            # Feature overview
            with st.expander("🚀 AI Description Features"):
                st.markdown("""
                **Powered by GPT-4 - Set & Forget AI Copywriting:**
                
                ✍️ **Auto-Generated Content**
                - Compelling titles (60 chars)
                - 300-500 word descriptions
                - Natural keyword integration
                - Call-to-action included
                
                🔑 **SEO Optimization**
                - 10-15 targeted keywords
                - Keywords appear naturally in text
                - Meta algorithm optimization
                - SEO score calculation
                
                #️⃣ **Social Media Ready**
                - 8-12 relevant hashtags
                - Platform-specific optimization
                - Copy/paste ready format
                
                ⌨️ **"Typed Out" for Meta**
                - Character-by-character rendering
                - Ensures Facebook counts all keywords
                - Improves search ranking
                - Better ad performance
                
                📊 **Performance Tracking**
                - SEO score out of 100
                - Keyword density analysis
                - Character count
                - Readability metrics
                """)
    
    with desc_tab2:
        show_description_library()


def show_settings_tab():
    """App settings"""
    st.subheader("⚙️ Settings")
    
    st.markdown("### Account")
    st.text_input("Email", value=st.session_state.user_email, disabled=True)
    st.text_input("Dealership Name", value="ABC Motors")
    
    st.markdown("### Notifications")
    st.checkbox("Email notifications", value=True)
    st.checkbox("Push notifications", value=True)
    
    st.markdown("### AI Configuration")
    openai_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Required for AI descriptions and background replacement"
    )
    if openai_key:
        st.success("✅ AI features enabled")
    else:
        st.warning("⚠️ Enter API key to enable AI features")
    
    st.markdown("### Facebook Integration")
    if st.button("🔵 Connect Facebook Business Account", use_container_width=True):
        st.info("Opening Facebook OAuth...")
    
    st.markdown("### API Access")
    st.code(st.session_state.api_key, language="text")
    
    st.markdown("---")
    if st.button("💾 Save Settings", use_container_width=True, type="primary"):
        st.success("✓ Settings saved!")


# Main app logic
def main():
    if not st.session_state.logged_in:
        login_page()
    elif not st.session_state.feed_connected:
        connect_feed_page()
    else:
        inventory_dashboard()


if __name__ == "__main__":
    main()
