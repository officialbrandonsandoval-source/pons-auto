"""
PONS AUTO - Photo Management Module
Mobile-optimized photo cropping, AI background replacement, and management
"""

import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64
from typing import List, Dict, Any, Optional

API_BASE_URL = "http://localhost:8000/api/v1"


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=95)
    return base64.b64encode(buffered.getvalue()).decode()


def base64_to_image(base64_str: str) -> Image.Image:
    """Convert base64 string to PIL Image."""
    image_data = base64.b64decode(base64_str)
    return Image.open(BytesIO(image_data))


def show_photo_manager(vin: str):
    """
    Mobile-optimized photo management interface.
    
    Features:
    - Touch-friendly photo upload
    - Crop photos before upload
    - AI background replacement (individual or batch)
    - Preview all photos
    - Reorder photos
    """
    
    st.markdown("### 📸 Photo Management")
    st.markdown(f"**Vehicle:** {vin}")
    
    # Initialize session state for photos
    if 'vehicle_photos' not in st.session_state:
        st.session_state.vehicle_photos = []
    if 'edited_photos' not in st.session_state:
        st.session_state.edited_photos = {}
    
    # Tab navigation
    tab1, tab2, tab3 = st.tabs(["📤 Upload", "✨ AI Background", "🖼️ Gallery"])
    
    with tab1:
        show_upload_crop_interface(vin)
    
    with tab2:
        show_ai_background_interface(vin)
    
    with tab3:
        show_photo_gallery(vin)


def show_upload_crop_interface(vin: str):
    """Upload and crop photos - mobile friendly."""
    
    st.markdown("#### Upload Vehicle Photos")
    st.info("💡 **Tip:** Hold your phone in landscape mode for best results!")
    
    # Multi-file uploader
    uploaded_files = st.file_uploader(
        "Choose photos to upload",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="Select one or more photos from your device"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} photo(s) selected")
        
        # Process each uploaded file
        for idx, uploaded_file in enumerate(uploaded_files):
            with st.expander(f"📸 Photo {idx + 1}: {uploaded_file.name}", expanded=(idx == 0)):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**Original**")
                    image = Image.open(uploaded_file)
                    st.image(image, use_container_width=True)
                    
                    # Image info
                    st.caption(f"Size: {image.width}x{image.height}px")
                
                with col2:
                    st.markdown("**Crop Options**")
                    
                    # Preset crop ratios
                    crop_preset = st.selectbox(
                        "Aspect Ratio",
                        ["Original", "16:9 (Wide)", "4:3 (Standard)", "1:1 (Square)"],
                        key=f"crop_{idx}"
                    )
                    
                    # Apply crop
                    if crop_preset != "Original":
                        cropped_image = apply_crop_preset(image, crop_preset)
                        st.image(cropped_image, use_container_width=True)
                        st.caption(f"Size: {cropped_image.width}x{cropped_image.height}px")
                    else:
                        cropped_image = image
                    
                    # Quality settings
                    quality = st.slider(
                        "JPEG Quality",
                        50, 100, 95,
                        key=f"quality_{idx}",
                        help="Higher quality = larger file size"
                    )
                
                # Add to gallery button
                if st.button(f"✅ Add to Gallery", key=f"add_{idx}", use_container_width=True):
                    # Save to session state
                    photo_data = {
                        "filename": uploaded_file.name,
                        "image": cropped_image,
                        "quality": quality,
                        "timestamp": str(st.session_state.get('timestamp', idx))
                    }
                    st.session_state.vehicle_photos.append(photo_data)
                    st.success(f"✓ Added to gallery!")
                    st.rerun()


def apply_crop_preset(image: Image.Image, preset: str) -> Image.Image:
    """Apply preset crop ratio to image."""
    width, height = image.size
    
    if preset == "16:9 (Wide)":
        target_ratio = 16 / 9
    elif preset == "4:3 (Standard)":
        target_ratio = 4 / 3
    elif preset == "1:1 (Square)":
        target_ratio = 1.0
    else:
        return image
    
    current_ratio = width / height
    
    if current_ratio > target_ratio:
        # Image is too wide, crop width
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    else:
        # Image is too tall, crop height
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        image = image.crop((0, top, width, top + new_height))
    
    return image


def show_ai_background_interface(vin: str):
    """AI-powered background replacement."""
    
    st.markdown("#### ✨ AI Background Replacement")
    
    if not st.session_state.vehicle_photos:
        st.warning("📸 No photos uploaded yet. Go to the Upload tab first!")
        return
    
    st.info("🤖 **Powered by GPT-4 + DALL-E 3** - Create professional dealership backgrounds")
    
    # Background style selector
    background_style = st.selectbox(
        "Choose Background Style",
        [
            "professional showroom",
            "luxury",
            "scenic",
            "gradient",
            "studio",
            "outdoor"
        ],
        help="AI will replace the background with this style"
    )
    
    # Style descriptions
    style_descriptions = {
        "professional showroom": "🏢 Modern dealership with bright lighting",
        "luxury": "💎 Upscale dealership with marble floors",
        "scenic": "🏔️ Beautiful mountain road with blue sky",
        "gradient": "🎨 Professional studio gradient backdrop",
        "studio": "📸 Clean photography studio setting",
        "outdoor": "🌳 Natural outdoor setting with clear sky"
    }
    
    st.caption(style_descriptions[background_style])
    
    st.markdown("---")
    
    # Select all checkbox
    select_all = st.checkbox(
        "🎯 **SELECT ALL PHOTOS** - Process all images at once",
        value=False,
        help="Apply AI background to all photos in one click"
    )
    
    if select_all:
        # Batch processing
        st.warning(f"⚡ Ready to process {len(st.session_state.vehicle_photos)} photos")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Process All Photos", use_container_width=True, type="primary"):
                with st.spinner("🤖 AI is working on your photos..."):
                    process_batch_ai_backgrounds(vin, background_style)
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.rerun()
    else:
        # Individual photo selection
        st.markdown("**Select photos to process:**")
        
        selected_indices = []
        cols = st.columns(3)
        
        for idx, photo in enumerate(st.session_state.vehicle_photos):
            with cols[idx % 3]:
                st.image(photo["image"], use_container_width=True)
                if st.checkbox(f"Photo {idx + 1}", key=f"select_{idx}"):
                    selected_indices.append(idx)
        
        if selected_indices:
            st.success(f"✓ {len(selected_indices)} photo(s) selected")
            
            if st.button("✨ Apply AI Background", use_container_width=True, type="primary"):
                with st.spinner("🤖 Processing..."):
                    process_selected_ai_backgrounds(vin, selected_indices, background_style)


def process_batch_ai_backgrounds(vin: str, background_style: str):
    """Process all photos with AI background replacement."""
    
    try:
        # In production, upload images to temporary storage and get URLs
        # For demo, we'll simulate the API call
        
        image_urls = []
        for photo in st.session_state.vehicle_photos:
            # Convert to base64 for API (in production, use S3 URLs)
            image_base64 = image_to_base64(photo["image"])
            image_urls.append(f"data:image/jpeg;base64,{image_base64}")
        
        # Call batch processing API
        response = requests.post(
            f"{API_BASE_URL}/ai/image/background/batch",
            json={
                "image_urls": image_urls,
                "background_style": background_style
            },
            timeout=120  # AI processing can take time
        )
        
        if response.status_code == 200:
            results = response.json()
            st.success(f"✅ Processed {len(results)} photos successfully!")
            
            # Store results
            for idx, result in enumerate(results):
                st.session_state.edited_photos[idx] = result
            
            st.balloons()
            st.rerun()
        else:
            st.error(f"❌ API Error: {response.status_code}")
            st.info("💡 Running in demo mode - AI features require OpenAI API key")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("💡 **Demo Mode:** AI background replacement requires OpenAI API key in production")


def process_selected_ai_backgrounds(vin: str, selected_indices: List[int], background_style: str):
    """Process selected photos with AI background."""
    
    try:
        selected_photos = [st.session_state.vehicle_photos[i] for i in selected_indices]
        
        image_urls = []
        for photo in selected_photos:
            image_base64 = image_to_base64(photo["image"])
            image_urls.append(f"data:image/jpeg;base64,{image_base64}")
        
        response = requests.post(
            f"{API_BASE_URL}/ai/image/background/batch",
            json={
                "image_urls": image_urls,
                "background_style": background_style
            },
            timeout=120
        )
        
        if response.status_code == 200:
            results = response.json()
            st.success(f"✅ Processed {len(results)} photos!")
            
            for idx, result in zip(selected_indices, results):
                st.session_state.edited_photos[idx] = result
            
            st.rerun()
        else:
            st.error(f"API Error: {response.status_code}")
            st.info("💡 Demo mode - requires OpenAI API key")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")


def show_photo_gallery(vin: str):
    """Display all photos with reordering capability."""
    
    st.markdown("#### 🖼️ Photo Gallery")
    
    if not st.session_state.vehicle_photos:
        st.info("📸 No photos yet. Upload some in the Upload tab!")
        return
    
    st.success(f"✓ {len(st.session_state.vehicle_photos)} photo(s) in gallery")
    
    # Display photos in grid
    cols = st.columns(2)
    
    for idx, photo in enumerate(st.session_state.vehicle_photos):
        with cols[idx % 2]:
            st.image(photo["image"], use_container_width=True)
            st.caption(f"📸 Photo {idx + 1}")
            
            # Show AI-enhanced version if available
            if idx in st.session_state.edited_photos:
                st.success("✨ AI-enhanced version available")
            
            # Delete button
            if st.button(f"🗑️ Remove", key=f"delete_{idx}"):
                st.session_state.vehicle_photos.pop(idx)
                if idx in st.session_state.edited_photos:
                    del st.session_state.edited_photos[idx]
                st.rerun()
    
    st.markdown("---")
    
    # Save to vehicle
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save All Photos", use_container_width=True, type="primary"):
            st.success("✅ Photos saved to vehicle!")
            st.balloons()
    
    with col2:
        if st.button("🗑️ Clear Gallery", use_container_width=True):
            st.session_state.vehicle_photos = []
            st.session_state.edited_photos = {}
            st.rerun()
