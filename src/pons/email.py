"""Email notification service."""

import os
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Dict, List, Optional
from jinja2 import Template


class EmailService:
    """Send email notifications."""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("EMAIL_FROM", self.smtp_user)
    
    async def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        html: bool = False
    ) -> bool:
        """
        Send an email.
        
        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body (plain text or HTML)
            html: Whether body is HTML
            
        Returns:
            True if sent successfully
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to)
            msg['Subject'] = subject
            
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Email send failed: {e}")
            return False
    
    async def send_vehicle_published_notification(
        self,
        to: List[str],
        vehicle_data: Dict[str, Any],
        channels: List[str]
    ) -> bool:
        """Send notification when vehicle is published."""
        template = Template("""
        <html>
        <body>
            <h2>Vehicle Published Successfully</h2>
            <p>The following vehicle has been published to {{ channels|join(', ') }}:</p>
            
            <table style="border-collapse: collapse; margin: 20px 0;">
                <tr>
                    <td style="padding: 8px; font-weight: bold;">VIN:</td>
                    <td style="padding: 8px;">{{ vehicle.vin }}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Vehicle:</td>
                    <td style="padding: 8px;">{{ vehicle.year }} {{ vehicle.make }} {{ vehicle.model }}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Price:</td>
                    <td style="padding: 8px;">${{ vehicle.price }}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Mileage:</td>
                    <td style="padding: 8px;">{{ vehicle.mileage }} miles</td>
                </tr>
            </table>
            
            <p>View in dashboard: <a href="https://shiftly.auto/vehicles/{{ vehicle.vin }}">Click here</a></p>
        </body>
        </html>
        """)
        
        html_body = template.render(vehicle=vehicle_data, channels=channels)
        
        return await self.send_email(
            to=to,
            subject=f"Vehicle Published: {vehicle_data['year']} {vehicle_data['make']} {vehicle_data['model']}",
            body=html_body,
            html=True
        )
    
    async def send_feed_import_notification(
        self,
        to: List[str],
        feed_name: str,
        vehicles_imported: int,
        errors: Optional[List[str]] = None
    ) -> bool:
        """Send notification after feed import."""
        template = Template("""
        <html>
        <body>
            <h2>Feed Import Complete</h2>
            <p><strong>Feed:</strong> {{ feed_name }}</p>
            <p><strong>Vehicles Imported:</strong> {{ vehicles_imported }}</p>
            
            {% if errors %}
            <h3>Errors</h3>
            <ul>
            {% for error in errors %}
                <li>{{ error }}</li>
            {% endfor %}
            </ul>
            {% else %}
            <p style="color: green;">✓ No errors</p>
            {% endif %}
        </body>
        </html>
        """)
        
        html_body = template.render(
            feed_name=feed_name,
            vehicles_imported=vehicles_imported,
            errors=errors
        )
        
        return await self.send_email(
            to=to,
            subject=f"Feed Import: {feed_name} - {vehicles_imported} vehicles",
            body=html_body,
            html=True
        )
    
    async def send_alert_notification(
        self,
        to: List[str],
        severity: str,
        message: str,
        source: str
    ) -> bool:
        """Send system alert notification."""
        colors = {
            "critical": "#ff0000",
            "high": "#ff6600",
            "medium": "#ffcc00",
            "low": "#0099ff"
        }
        
        template = Template("""
        <html>
        <body>
            <div style="border-left: 4px solid {{ color }}; padding-left: 12px;">
                <h2 style="color: {{ color }};">{{ severity|upper }} Alert</h2>
                <p><strong>Source:</strong> {{ source }}</p>
                <p><strong>Message:</strong> {{ message }}</p>
                <p><strong>Time:</strong> {{ timestamp }}</p>
            </div>
        </body>
        </html>
        """)
        
        html_body = template.render(
            severity=severity,
            message=message,
            source=source,
            color=colors.get(severity.lower(), "#666666"),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return await self.send_email(
            to=to,
            subject=f"[{severity.upper()}] Shiftly Auto Alert",
            body=html_body,
            html=True
        )


# Service instance
email_service = EmailService()
