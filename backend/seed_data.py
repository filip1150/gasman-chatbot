"""
Seed the Gas Man Ottawa knowledge base into Pinecone and SQLite.
Run once: python seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from database import init_db, SessionLocal
from knowledge_base import create_entry

SEED_DATA = [
    # Company Info
    ("Company Info", "Company Overview",
     "Gas Man Ottawa Inc. Founded in 2004 by Jeff. Located at 6770 Breanna Cardill St, Greely, ON K4P 0C3. Phone: (613) 880-3888. Email: jeff@gasmanottawa.com. Website: gasmanottawa.com. Service in English and French. TSSA Licensed, Fully Insured."),
    ("Company Info", "Guarantees and Warranties",
     "Gas Man provides a 1-year installation guarantee on parts and labour. Lifetime warranty on installation errors. Gas Man is an authorized repair contractor — if equipment is covered under manufacturer warranty, Gas Man bills the manufacturer, not the customer. All work built to code."),
    ("Company Info", "How Quoting Works",
     "Gas Man uses Jobber for digital quotations. Customers receive professional quotes electronically and can approve, reject, or modify them. All estimates are FREE and no obligation — a technician visits your home to assess needs and provide an accurate quote."),

    # Service Areas
    ("Service Areas", "Service Areas",
     "Gas Man services all of Ottawa including: Orleans, Kanata, Barrhaven, Nepean, Gloucester, Manotick, Rockland, Cumberland, Limoges, Embrun, Vanier, South Keys, Pineview, Innes Road, Blackburn Hamlet, Beacon Hill, Stittsville, Bells Corners, Hunt Club Road, Greely, March Road, Bridlewood. Also serves rural areas — inquire about out-of-town and special rural service."),

    # Furnaces
    ("Furnaces", "Furnace Brands",
     "Gas Man supplies and installs furnaces from all major brands: Rheem, Trane, Carrier, Goodman, Amana, Bryant, York, and more. We favour furnaces that offer exceptional value and quality. If we wouldn't put it in our home, we won't put it in yours."),
    ("Furnaces", "Furnace Types and Pricing",
     "Three types of furnaces available. Single-stage 95% AFUE: $3,500-$5,000 installed — basic, reliable, full blast or off. Two-stage 96% AFUE: $4,500-$6,500 installed — quieter, more even temperature, best value for most Ottawa homes, approximately $100/year gas savings over single-stage. Modulating 98% AFUE: $5,500-$7,500+ installed — whisper quiet, most consistent temperature, premium option. Labour ($500-$1,500) is typically included in these prices. Canada mandates minimum 95% AFUE so all new furnaces are high-efficiency."),
    ("Furnaces", "Furnace Installation Details",
     "Furnace installation takes 4-8 hours, usually completed in one day. Time varies based on furnace location, accessibility, and old furnace removal. Ottawa homes typically need 60,000-120,000 BTU depending on square footage and insulation quality. High-efficiency furnaces use PVC sidewall venting instead of metal chimney — conversion cost $200-$500 one-time. Manufacturer warranty covers 10-year parts. Gas Man adds 1-year installation guarantee on top."),
    ("Furnaces", "Furnace Features",
     "Modern furnaces offer features like ECM blower motors (50-75% less electricity than old PSC motors), two-stage heating for better comfort, smart AI-controlled functionality, WiFi connectivity and app control for temperature monitoring. Exact Comfort models add extra temperature sensors around the home. Some models offer one-button warranty service through the furnace app."),
    ("Furnaces", "Furnace Rebates",
     "Check with Enbridge and Natural Resources Canada for current rebate programs on energy-efficient furnace upgrades. Enbridge offers $250 for ECM blower motors when paired with qualifying furnace. Ask during free estimate about any currently running government programs."),
    ("Furnaces", "Furnace Recommendation",
     "For most Ottawa homes, a two-stage 96% AFUE furnace is the sweet spot. It costs $1,000-$1,500 more than single-stage but delivers noticeably better comfort, quieter operation, and approximately $100 per year in gas savings. The modulating 98% model costs an additional $1,000-$2,000 on top for only marginal improvements — the price difference is better invested in ductwork, a smart thermostat, or whole-home humidifier."),

    # Air Conditioning
    ("Air Conditioning", "AC Types and Pricing",
     "Three main cooling options for Ottawa homes. Central AC: $3,800-$7,500+ installed — cools entire home through existing ductwork, 15-20 year lifespan. Ductless Mini-Split: $3,000-$5,000 per zone — no ductwork required, wall-mounted units cool individual rooms, multi-zone systems cool up to 5 rooms from one outdoor unit. Heat Pump: $5,500-$12,000+ installed — cools in summer AND heats in winter, highest efficiency, qualifies for largest rebates."),
    ("Air Conditioning", "AC Brands and Recommendations",
     "Gas Man installs trusted manufacturers including Rheem, Goodman, and other high-quality brands. We are authorized installers so manufacturer warranty is fully backed by factory support. For most Ottawa homes with existing ductwork, a central air conditioner in the two-stage range (16-17 SEER) delivers the best balance of upfront cost, efficiency, and comfort. Homes without ductwork should consider a ductless mini-split or heat pump."),
    ("Air Conditioning", "AC Rebates",
     "Direct rebates for standalone AC units are limited. Enbridge offers $75 for smart thermostat and $250 for ECM blower motors when paired with qualifying furnace. Heat pumps qualify for much larger rebates — up to $5,000-$7,500 from federal and provincial programs. Consider a heat pump if maximizing rebates is a priority."),

    # Heat Pumps
    ("Heat Pumps", "Heat Pump Overview",
     "Heat pumps heat your home in winter and cool it in summer at a fraction of the energy cost of traditional furnace-and-AC combinations. Modern cold-climate heat pumps work down to -25°C to -30°C, fully viable for Ottawa winters. Brands: Mitsubishi Hyper-Heat, Daikin Fit, Bosch IDS. Pricing: $5,500-$12,000+ installed. Rebates: Up to $7,500+ from federal and provincial programs."),
    ("Heat Pumps", "Heat Pump Savings",
     "Most Ottawa homeowners report 30-50% heating cost savings in shoulder seasons (fall and spring) and 20-40% savings during peak winter when heat pump shares load with furnace. Total annual energy savings of $500-$1,200 realistic depending on home size and insulation. Dual-fuel setup (heat pump + gas furnace backup) is the most popular option for Ottawa."),
    ("Heat Pumps", "Heat Pump Installation",
     "Ducted heat pump replacing existing AC unit takes 6-10 hours, typically one day. Ductless single-zone installation takes 4-6 hours. Multi-zone ductless systems may require 1-2 days. Modern cold-climate models are quiet — 55-65 dB outdoor unit (normal conversation level), 20-30 dB indoor ductless heads (nearly silent)."),

    # Water Heaters
    ("Water Heaters", "Tankless Water Heater Overview",
     "Tankless (on-demand) water heaters provide unlimited hot water, are wall-mounted to save space, and are energy efficient. Only heats water when you use it. Perfect for both high-demand families who need constant hot water and low-demand homes who only pay for what they use. Features available: condensing models (highest efficiency), WiFi connectivity, indoor/outdoor mounting options, easy to winterize."),
    ("Water Heaters", "Tankless Water Heater Sizing",
     "Tankless water heater sizing based on demand. Low demand: 130,000 BTU. Medium demand: 180,000 BTU. High demand: 350,000 BTU. Sizing depends on total GPM required for simultaneous fixtures (showers, dishwashers) and temperature rise needed to heat incoming groundwater to desired temperature."),
    ("Water Heaters", "Water Heater Maintenance and Repairs",
     "Regular maintenance recommended for tankless water heaters. Ottawa water has high calcium and magnesium that can build up inside restricting water flow. Common issues: mineral build-up, water demand too high (system overload), error codes, ignition and pilot light problems. Gas Man is authorized to diagnose and repair all makes and models using genuine replacement parts. Priority same-day or next-day emergency repair available."),

    # Gas Piping
    ("Gas Piping", "Gas Piping Services",
     "Gas Man uses ONLY schedule 40 black steel pipes and fittings — the safest and most durable option. We do NOT use copper or flexible stainless steel pipes which can be damaged during home renovations. Applications: BBQ hookup, pool heaters, gas fireplaces, gas appliances, outdoor kitchens, landscaping features, gas stoves. All trucks equipped with commercial-grade pipe cutting and threading machines for custom fabrication on site."),
    ("Gas Piping", "BBQ Gas Line Installation",
     "Connecting your barbecue to natural gas provides unlimited, clean, and affordable fuel. Installation takes just a few hours. Gas technicians cut custom-length gas piping and professionally install it connecting your barbecue to your gas meter. Gas line piping cost: $200-$600 depending on distance and complexity."),

    # Gas Fireplaces
    ("Gas Fireplaces", "Gas Fireplace Services",
     "Gas Man installs and services all major gas fireplace brands: Napoleon, Majestic, Kingsman, Continental, Regency, Heatilator, and more. Types: direct vent inserts, vent-free (strict Ontario regulations), log sets. Pricing: $2,500-$6,000+ installed. Gas fireplaces are best for zone heating — they heat the room effectively but are not a replacement for central furnace. Annual professional maintenance recommended, schedule in September-October before heating season."),

    # Smart Thermostats
    ("Smart Thermostats", "Smart Thermostat Options",
     "Three brands dominate the smart thermostat market. Nest: best for ease of use, sleek design, Google Home integration — often works without C-wire. ecobee: comprehensive features, room sensors — includes power extender kit for missing C-wire. Honeywell: reliable value. Pricing: $130-$280 depending on brand and features. Savings: 8-23% on heating and cooling bills, approximately $150-$500+ annually for Ottawa homes. Payback period: 6-18 months. Enbridge offers $75 rebate for ENERGY STAR certified models."),

    # Ventilation
    ("Ventilation", "HRV and ERV Ventilation",
     "HRV (Heat Recovery Ventilator) is more efficient in winter. ERV (Energy Recovery Ventilator) is better for most Ottawa homeowners. Both connect to central climate system, controlled via remote, app, or thermostat. Some condensation is normal due to temperature differences between indoor and outdoor air. Service at the same time as other HVAC equipment."),

    # Maintenance
    ("Maintenance", "HVAC Maintenance Services",
     "Regular maintenance increases reliability, lifespan, and efficiency of heating and cooling equipment. Recommended every 1-3 years depending on condition and specification. Gas Man technicians inspect, lubricate, test, and clean all mechanical and electrical components. Pool heaters: best serviced in fall so winterizing can be done at the same time. Homeowners should regularly change furnace air filters between professional services."),

    # Commercial
    ("Commercial", "Commercial and New Build Services",
     "Gas Man Commercial Services work with new home builders and commercial contractors installing HVAC infrastructure including piping, ventilation, furnaces, air conditioners, and other gas equipment. Commercial installers have worked on the majority of new homes in Orleans, Manotick, Kanata, and Barrhaven. Always on schedule, built to specification and code, never sacrificing quality or safety."),

    # Emergency Procedures
    ("Emergency Procedures", "Emergency — Gas Smell",
     "CRITICAL SAFETY: If you smell gas, leave the house immediately. Do NOT turn on or off any lights or electrical switches. Call 911 first. Then call Gas Man at (613) 880-3888. Do not re-enter the home until emergency services clear it."),
    ("Emergency Procedures", "Emergency — No Heat",
     "If your furnace stops working: First check that the thermostat is set to HEAT and the temperature is set above room temperature. Check the furnace filter — a clogged filter can shut down the furnace. Check that the furnace power switch is ON. If none of these fix it, call Gas Man at (613) 880-3888 for same-day emergency repair service. We prioritize emergency HVAC repair calls."),
    ("Emergency Procedures", "Emergency — Carbon Monoxide",
     "If your carbon monoxide detector is going off: Leave the house immediately with all family members and pets. Call 911. Do not re-enter until cleared by emergency services. Then call Gas Man at (613) 880-3888 — we can inspect your furnace and gas appliances for CO leaks. All our installations are built to code to prevent CO issues."),
    ("Emergency Procedures", "Emergency — Water Heater Failure",
     "If your water heater stops working: For tankless, try resetting the unit (check your manual for reset procedure). Check for error codes on the display. If the issue persists, call Gas Man at (613) 880-3888. We offer priority same-day or next-day emergency repair for water heater failures."),
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        from database import KnowledgeEntry
        existing = db.query(KnowledgeEntry).count()
        if existing > 0:
            print(f"Knowledge base already has {existing} entries. Skipping seed.")
            return

        print(f"Seeding {len(SEED_DATA)} knowledge base entries...")
        for i, (category, title, content) in enumerate(SEED_DATA, 1):
            print(f"  [{i}/{len(SEED_DATA)}] {category} — {title}")
            create_entry(db, category, title, content)
        print("Seed complete!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
