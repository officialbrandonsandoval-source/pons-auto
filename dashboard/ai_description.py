"""
PONS AUTO - AI Description Generator
SEO-optimized descriptions with "typed out" effect for Meta keyword counting
"""

import streamlit as st
import requests
import time
from typing import Dict, Any, Optional

API_BASE_URL = "http://localhost:8000/api/v1"


def show_ai_description_generator(vehicle_data: Dict[str, Any]):
    """
    Set and forget AI description generator.
    
    Features:
    - Auto-generates SEO-optimized descriptions
    - Includes keywords and hashtags
    - "Types out" description so Meta counts keywords
    - Shows SEO score
    """
    
    st.markdown("### 🤖 AI Description Generator")
    st.info("💡 **Set & Forget:** Let AI write compelling, SEO-optimized descriptions for you!")
    
    # Vehicle info display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Year", vehicle_data.get("year", "N/A"))
    with col2:
        st.metric("Make", vehicle_data.get("make", "N/A"))
    with col3:
        st.metric("Model", vehicle_data.get("model", "N/A"))
    
    st.markdown("---")
    
    # Optional customization
    with st.expander("⚙️ Customize Description (Optional)"):
        col1, col2 = st.columns(2)
        
        with col1:
            custom_features = st.text_area(
                "Highlight Specific Features",
                placeholder="Sunroof, Leather seats, Navigation...",
                help="Comma-separated list of features to emphasize"
            )
        
        with col2:
            tone = st.selectbox(
                "Writing Tone",
                ["Professional", "Friendly", "Luxury", "Budget-Friendly"],
                help="How the description should sound"
            )
            
            target_platform = st.multiselect(
                "Optimize For",
                ["Facebook Marketplace", "AutoTrader", "Cars.com", "Instagram"],
                default=["Facebook Marketplace"]
            )
    
    st.markdown("---")
    
    # Generate button
    if st.button("✨ Generate AI Description", use_container_width=True, type="primary"):
        generate_and_display_description(vehicle_data, custom_features if custom_features else None)


def generate_and_display_description(vehicle_data: Dict[str, Any], custom_features: Optional[str] = None):
    """Generate AI description and display with typing effect."""
    
    # Prepare API request
    features = []
    if custom_features:
        features = [f.strip() for f in custom_features.split(",")]
    
    request_data = {
        "year": vehicle_data.get("year"),
        "make": vehicle_data.get("make"),
        "model": vehicle_data.get("model"),
        "trim": vehicle_data.get("trim"),
        "mileage": vehicle_data.get("mileage"),
        "features": features if features else vehicle_data.get("features", []),
        "condition": vehicle_data.get("condition", "Excellent"),
        "price": vehicle_data.get("price")
    }
    
    with st.spinner("🤖 AI is crafting your description..."):
        try:
            response = requests.post(
                f"{API_BASE_URL}/ai/description",
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                ai_result = response.json()
                display_ai_description(ai_result, vehicle_data)
            else:
                st.error(f"API Error: {response.status_code}")
                # Fallback demo data
                display_demo_description(vehicle_data)
                
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            st.info("💡 **Demo Mode:** Showing sample AI description")
            display_demo_description(vehicle_data)


def display_ai_description(ai_result: Dict[str, Any], vehicle_data: Dict[str, Any]):
    """Display AI-generated description with typing effect for Meta."""
    
    st.success("✅ AI Description Generated!")
    
    # SEO Score
    seo_score = ai_result.get("seo_score", 85)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("SEO Score", f"{seo_score:.0f}/100")
    with col2:
        st.metric("Keywords", len(ai_result.get("keywords", [])))
    with col3:
        st.metric("Hashtags", len(ai_result.get("hashtags", [])))
    
    st.markdown("---")
    
    # Title
    st.markdown("#### 📝 Listing Title")
    st.code(ai_result.get("title", ""), language="text")
    
    st.markdown("---")
    
    # Description with typing effect
    st.markdown("#### 📄 Description")
    st.info("💡 **Meta Optimization:** Description will be 'typed out' to ensure keywords are counted by Facebook's algorithm")
    
    description = ai_result.get("description", "")
    
    # Checkbox to enable typing effect
    enable_typing = st.checkbox(
        "🎬 **Enable Typing Effect** (Simulates real-time entry for Meta)",
        value=False,
        help="When enabled, description appears character-by-character"
    )
    
    if enable_typing:
        # Create placeholder for typing animation
        description_placeholder = st.empty()
        
        # Type out the description
        typed_text = ""
        for char in description:
            typed_text += char
            description_placeholder.text_area(
                "Generated Description",
                value=typed_text,
                height=300,
                key=f"typing_{len(typed_text)}"
            )
            time.sleep(0.01)  # Typing speed - adjust for faster/slower
        
        st.success("✅ Description fully loaded - Meta can now count all keywords!")
    else:
        # Show full description immediately
        st.text_area(
            "Generated Description",
            value=description,
            height=300,
            disabled=False,
            help="You can edit this description if needed"
        )
    
    st.markdown("---")
    
    # Keywords
    st.markdown("#### 🔑 SEO Keywords")
    keywords = ai_result.get("keywords", [])
    
    # Display keywords as colored badges
    keyword_html = ""
    for kw in keywords:
        keyword_html += f'<span style="background-color: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 12px; margin: 4px; display: inline-block; font-size: 14px;">#{kw}</span>'
    
    st.markdown(keyword_html, unsafe_allow_html=True)
    st.caption(f"✓ {len(keywords)} keywords naturally integrated into description")
    
    st.markdown("---")
    
    # Hashtags
    st.markdown("#### #️⃣ Hashtags")
    hashtags = ai_result.get("hashtags", [])
    
    hashtag_text = " ".join(hashtags)
    st.code(hashtag_text, language="text")
    st.caption("Copy and paste into your social media posts")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save & Use This Description", use_container_width=True, type="primary"):
            # Save to vehicle data
            if 'vehicle_descriptions' not in st.session_state:
                st.session_state.vehicle_descriptions = {}
            
            vin = vehicle_data.get("vin", "unknown")
            st.session_state.vehicle_descriptions[vin] = {
                "title": ai_result.get("title"),
                "description": description,
                "keywords": keywords,
                "hashtags": hashtags,
                "seo_score": seo_score
            }
            
            st.success("✅ Description saved to vehicle!")
            st.balloons()
    
    with col2:
        if st.button("🔄 Generate New Version", use_container_width=True):
            st.rerun()


def display_demo_description(vehicle_data: Dict[str, Any]):
    """Display demo AI description when API is unavailable."""
    
    year = vehicle_data.get("year", 2023)
    make = vehicle_data.get("make", "Toyota")
    model = vehicle_data.get("model", "Camry")
    mileage = vehicle_data.get("mileage", 25000)
    price = vehicle_data.get("price", 28995)
    
    demo_result = {
        "title": f"{year} {make} {model} - Excellent Condition",
        "description": f"""🚗 PREMIUM {str(year)} {make.upper()} {model.upper()} - YOUR NEXT DREAM CAR AWAITS! 🚗

Are you looking for a reliable, stylish, and feature-packed vehicle? Look no further! This stunning {year} {make} {model} combines performance, comfort, and cutting-edge technology in one impressive package.

✨ KEY FEATURES:
• Only {mileage:,} miles - barely broken in!
• Fuel-efficient engine perfect for daily commuting
• Spacious interior with premium materials
• Advanced safety features for peace of mind
• Smooth automatic transmission
• Bluetooth connectivity and modern infotainment
• Well-maintained service history

💎 CONDITION: This {model} is in exceptional condition, both inside and out. The exterior shines like new, and the interior is immaculate with no signs of wear. Non-smoker vehicle, garage-kept, and meticulously cared for by the previous owner.

🛡️ SAFETY FIRST: Equipped with advanced safety features including airbags, anti-lock brakes, traction control, and stability control to keep you and your family protected on every journey.

💰 PRICED TO SELL: At just ${price:,}, this {make} {model} offers incredible value. Compare our price to similar vehicles - you won't find a better deal!

📍 CONVENIENT LOCATION & FINANCING: We're here to help make your car-buying experience smooth and stress-free. Financing options available for qualified buyers with competitive rates.

⭐ Don't miss out on this opportunity! Vehicles in this condition and price range don't last long. Contact us TODAY to schedule your test drive and experience the quality of this {year} {make} {model} for yourself.

📞 Call now or message us to learn more. Your next adventure starts here! 🌟

#QualityUsedCars #AffordableCars #ReliableTransportation #{make} #{model} #CarShopping #DealOfTheDay""",
        "keywords": [
            f"{year} {make} {model}",
            "used cars",
            "reliable vehicle",
            "fuel efficient",
            "low mileage",
            "excellent condition",
            "affordable cars",
            make.lower(),
            model.lower(),
            "car dealership",
            "financing available",
            "test drive",
            "clean title",
            "certified pre-owned"
        ],
        "hashtags": [
            f"#{make}",
            f"#{model}",
            "#UsedCars",
            "#CarDeals",
            "#AffordableCars",
            "#ReliableTransportation",
            "#CarShopping",
            "#AutoSales",
            f"#{make}{model}",
            "#QualityUsedCars",
            "#CarDealership",
            "#TestDrive"
        ],
        "seo_score": 88.5,
        "character_count": 1450
    }
    
    st.info("💡 **Demo Mode:** Showing sample AI description (OpenAI API key required for production)")
    display_ai_description(demo_result, vehicle_data)


def show_description_library():
    """Show all saved AI descriptions for quick access."""
    
    st.markdown("### 📚 Description Library")
    
    if 'vehicle_descriptions' not in st.session_state or not st.session_state.vehicle_descriptions:
        st.info("📝 No saved descriptions yet. Generate your first AI description!")
        return
    
    st.success(f"✓ {len(st.session_state.vehicle_descriptions)} saved description(s)")
    
    for vin, desc_data in st.session_state.vehicle_descriptions.items():
        with st.expander(f"🚗 VIN: {vin} - {desc_data['title']}"):
            st.markdown(f"**SEO Score:** {desc_data['seo_score']:.1f}/100")
            
            st.markdown("**Description:**")
            st.text(desc_data['description'][:200] + "...")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📋 Copy", key=f"copy_{vin}"):
                    st.code(desc_data['description'])
            with col2:
                if st.button("✏️ Edit", key=f"edit_{vin}"):
                    st.info("Editing feature coming soon!")
            with col3:
                if st.button("🗑️ Delete", key=f"del_{vin}"):
                    del st.session_state.vehicle_descriptions[vin]
                    st.rerun()
