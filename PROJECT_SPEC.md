# PROJECT_SPEC.md — Gas Man Ottawa AI Chat Assistant

## 1. Customer-Facing Chat Widget

### Appearance
- Floating chat bubble (bottom-right corner) with flame/orange theme (#E8531E)
- Pulsing green dot indicating "online 24/7"
- Opens to a chat window (380px wide, 520px tall on desktop, responsive on mobile)
- Header shows "Gas Man Assistant" with "Answers in seconds, 24/7"
- Smooth open/close animation
- Must not interfere with existing page elements or Jobber booking forms

### Chat Behavior
- Opens with a friendly greeting and 3-4 quick suggestion buttons
- Typing indicator (animated dots) before bot responds
- Supports free-text input and suggestion buttons
- Conversations are stored in SQLite with timestamps
- Bot responds in the same language the customer writes in (English or French minimum)

### Suggested Quick Actions (shown on first open)
- "I need a new furnace"
- "Emergency — no heat!"
- "Book a free estimate"
- "Do you service my area?"

### Guided Conversation Flows

#### Furnace Flow
1. "How old is your current furnace?"
2. "Do you know the brand?"
3. "Is your main priority keeping costs down, best comfort, or somewhere in the middle?"
4. Recommend appropriate tier (single-stage / two-stage / modulating) with price range
5. Offer to book free estimate

#### Water Heater Flow
1. "Do you currently have a tank or tankless water heater?"
2. "How many people in your household?"
3. "How many bathrooms?"
4. Recommend tank vs tankless with reasoning and price range
5. Offer to book free estimate

#### AC Flow
1. "Do you have existing ductwork in your home?"
2. "Are you replacing an old AC or adding AC for the first time?"
3. Recommend central vs ductless vs heat pump with price ranges
4. Mention heat pump rebates ($5,000-$7,500)
5. Offer to book free estimate

#### Emergency Flow
- If customer mentions: gas smell, carbon monoxide, CO detector, no heat, furnace not working, emergency
- IMMEDIATELY respond with safety instructions
- Gas smell: "Leave the house immediately. Call 911 first. Then call Gas Man at (613) 880-3888"
- No heat in winter: "Check your thermostat settings and filter first. If those are fine, call us at (613) 880-3888 for same-day emergency service"

#### Service Area Flow
- If customer asks about a specific area, check against known service areas in knowledge base
- For areas not listed: "We may be able to help! Leave your address and we'll confirm"

### Lead Capture
- When customer is ready to book, collect: name, phone, email, address, service needed
- Store as a lead in SQLite database
- Display in admin panel with notification badge

---

## 2. Admin Panel

### Authentication
- Simple username/password login
- Credentials stored in .env (ADMIN_USERNAME, ADMIN_PASSWORD)
- Default: admin / gasman2024
- JWT or session-based auth for API calls

### Knowledge Base Management
- Display knowledge entries in editable cards/sections organized by category
- Categories: Services, Pricing, Brands, Service Areas, FAQs, Emergency Procedures, Company Info
- Each entry has: id, category, title, content (text)
- **Add entry**: Admin fills in category, title, content → backend embeds the content → upserts to Pinecone with metadata (id, category, title) → saves to SQLite as backup
- **Edit entry**: Admin updates content → backend re-embeds → upserts to Pinecone (same vector ID, new embedding) → updates SQLite
- **Delete entry**: Removes from Pinecone and SQLite
- Seed with Gas Man data on first run (see Section 4 below)
- Show total entry count and last sync timestamp

### AI Instructions Management
- **Stored in SQLite, NOT in Pinecone** — instructions are rules/personality, not searchable knowledge
- Single large text area where the admin can edit the full system prompt
- Default instructions pre-filled on first run (see Section 5 below)
- Save button with confirmation
- Show "last updated" timestamp
- Optional: version history (store previous versions so admin can revert)

### Conversation Logs
- List of all conversations with timestamp, preview of first customer message
- Click to expand and see full conversation (all messages in order)
- Filter by date range
- Show total conversation count, today's count, and daily average
- Flag/star important conversations for review
- Export conversations as CSV (optional)

### Leads Dashboard
- List of captured leads with: name, phone, email, service needed, timestamp
- Status toggle: "New" / "Contacted" / "Booked" / "Closed"
- Filter by status
- Simple stats: total leads this week, this month, uncontacted count
- Notification badge on sidebar showing uncontacted lead count

---

## 3. Backend API

### Endpoints

```
# Chat
POST /api/chat
  Body: { message: string, conversation_id: string | null }
  Logic:
    1. If no conversation_id, create new conversation in SQLite
    2. Embed user message using OpenAI embeddings
    3. Query Pinecone for top 5-8 relevant knowledge chunks
    4. Load AI instructions from SQLite
    5. Build prompt: instructions + retrieved chunks + conversation history
    6. Call Claude Sonnet API
    7. Store user message + bot response in SQLite
    8. Return { response: string, conversation_id: string }

GET /api/widget/config
  Returns: { greeting: string, suggestions: [], theme: { primaryColor, etc } }

# Admin - Knowledge Base
GET    /api/admin/knowledge-base
POST   /api/admin/knowledge-base
  → Embed content, upsert to Pinecone, save to SQLite
PUT    /api/admin/knowledge-base/{id}
  → Re-embed content, upsert to Pinecone (same ID), update SQLite
DELETE /api/admin/knowledge-base/{id}
  → Delete from Pinecone and SQLite

# Admin - AI Instructions
GET /api/admin/instructions
  Returns: { instructions: string, updated_at: timestamp }
PUT /api/admin/instructions
  Body: { instructions: string }
  → Save to SQLite (NOT to Pinecone)

# Admin - Conversations
GET /api/admin/conversations
  Query params: ?from=date&to=date&page=1&limit=20
GET /api/admin/conversations/{id}
  Returns full conversation with all messages

# Admin - Leads
GET  /api/admin/leads
  Query params: ?status=new&page=1&limit=20
POST /api/admin/leads
  Body: { name, phone, email, address, service_needed }
PUT  /api/admin/leads/{id}
  Body: { status: "contacted" | "booked" | "closed" }

# Admin - Stats
GET /api/admin/stats
  Returns: { total_conversations, today_conversations, total_leads, uncontacted_leads, this_week_leads, this_month_leads }

# Admin - Auth
POST /api/admin/login
  Body: { username, password }
  Returns: { token }
```

### Database Models (SQLite)

```python
# AI Instructions — editable via admin panel, loaded on every chat request
class AIInstructions:
    id: int
    instructions: text        # The full system prompt
    updated_at: datetime

# Knowledge Base Entry — synced to Pinecone
class KnowledgeEntry:
    id: str (uuid)            # Same ID used as Pinecone vector ID
    category: str             # Services, Pricing, Brands, etc.
    title: str
    content: text
    created_at: datetime
    updated_at: datetime

# Conversation
class Conversation:
    id: str (uuid)
    started_at: datetime
    last_message_at: datetime
    message_count: int
    flagged: bool

# Message
class Message:
    id: int
    conversation_id: str (FK)
    role: str                 # "user" or "assistant"
    content: text
    timestamp: datetime

# Lead
class Lead:
    id: int
    name: str
    phone: str
    email: str
    address: str (optional)
    service_needed: str
    status: str               # "new", "contacted", "booked", "closed"
    conversation_id: str (FK, optional)
    created_at: datetime
```

### Pinecone Schema

```
Index: gasman-chatbot
Namespace: gasman (multi-tenant ready)
Dimension: 1536 (for text-embedding-3-small)

Each vector:
  id: knowledge_entry.id (uuid)
  values: embedding of knowledge_entry.content
  metadata:
    category: str
    title: str
    content: str (stored for retrieval display)
```

---

## 4. Seed Knowledge Base Data

Each item below becomes a separate KnowledgeEntry, embedded and upserted to Pinecone on first run.

### Company Info
- **Title**: Company Overview
- **Content**: Gas Man Ottawa Inc. Founded in 2004 by Jeff. Located at 6770 Breanna Cardill St, Greely, ON K4P 0C3. Phone: (613) 880-3888. Email: jeff@gasmanottawa.com. Website: gasmanottawa.com. Service in English and French. TSSA Licensed, Fully Insured.

- **Title**: Guarantees and Warranties
- **Content**: Gas Man provides a 1-year installation guarantee on parts and labour. Lifetime warranty on installation errors. Gas Man is an authorized repair contractor — if equipment is covered under manufacturer warranty, Gas Man bills the manufacturer, not the customer. All work built to code.

- **Title**: How Quoting Works
- **Content**: Gas Man uses Jobber for digital quotations. Customers receive professional quotes electronically and can approve, reject, or modify them. All estimates are FREE and no obligation — a technician visits your home to assess needs and provide an accurate quote.

### Service Areas
- **Title**: Service Areas
- **Content**: Gas Man services all of Ottawa including: Orleans, Kanata, Barrhaven, Nepean, Gloucester, Manotick, Rockland, Cumberland, Limoges, Embrun, Vanier, South Keys, Pineview, Innes Road, Blackburn Hamlet, Beacon Hill, Stittsville, Bells Corners, Hunt Club Road, Greely, March Road, Bridlewood. Also serves rural areas — inquire about out-of-town and special rural service.

### Furnaces
- **Title**: Furnace Brands
- **Content**: Gas Man supplies and installs furnaces from all major brands: Rheem, Trane, Carrier, Goodman, Amana, Bryant, York, and more. We favour furnaces that offer exceptional value and quality. If we wouldn't put it in our home, we won't put it in yours.

- **Title**: Furnace Types and Pricing
- **Content**: Three types of furnaces available. Single-stage 95% AFUE: $3,500-$5,000 installed — basic, reliable, full blast or off. Two-stage 96% AFUE: $4,500-$6,500 installed — quieter, more even temperature, best value for most Ottawa homes, approximately $100/year gas savings over single-stage. Modulating 98% AFUE: $5,500-$7,500+ installed — whisper quiet, most consistent temperature, premium option. Labour ($500-$1,500) is typically included in these prices. Canada mandates minimum 95% AFUE so all new furnaces are high-efficiency.

- **Title**: Furnace Installation Details
- **Content**: Furnace installation takes 4-8 hours, usually completed in one day. Time varies based on furnace location, accessibility, and old furnace removal. Ottawa homes typically need 60,000-120,000 BTU depending on square footage and insulation quality. High-efficiency furnaces use PVC sidewall venting instead of metal chimney — conversion cost $200-$500 one-time. Manufacturer warranty covers 10-year parts. Gas Man adds 1-year installation guarantee on top.

- **Title**: Furnace Features
- **Content**: Modern furnaces offer features like ECM blower motors (50-75% less electricity than old PSC motors), two-stage heating for better comfort, smart AI-controlled functionality, WiFi connectivity and app control for temperature monitoring. Exact Comfort models add extra temperature sensors around the home. Some models offer one-button warranty service through the furnace app.

- **Title**: Furnace Rebates
- **Content**: Check with Enbridge and Natural Resources Canada for current rebate programs on energy-efficient furnace upgrades. Enbridge offers $250 for ECM blower motors when paired with qualifying furnace. Ask during free estimate about any currently running government programs.

- **Title**: Furnace Recommendation
- **Content**: For most Ottawa homes, a two-stage 96% AFUE furnace is the sweet spot. It costs $1,000-$1,500 more than single-stage but delivers noticeably better comfort, quieter operation, and approximately $100 per year in gas savings. The modulating 98% model costs an additional $1,000-$2,000 on top for only marginal improvements — the price difference is better invested in ductwork, a smart thermostat, or whole-home humidifier.

### Air Conditioning
- **Title**: AC Types and Pricing
- **Content**: Three main cooling options for Ottawa homes. Central AC: $3,800-$7,500+ installed — cools entire home through existing ductwork, 15-20 year lifespan. Ductless Mini-Split: $3,000-$5,000 per zone — no ductwork required, wall-mounted units cool individual rooms, multi-zone systems cool up to 5 rooms from one outdoor unit. Heat Pump: $5,500-$12,000+ installed — cools in summer AND heats in winter, highest efficiency, qualifies for largest rebates.

- **Title**: AC Brands and Recommendations
- **Content**: Gas Man installs trusted manufacturers including Rheem, Goodman, and other high-quality brands. We are authorized installers so manufacturer warranty is fully backed by factory support. For most Ottawa homes with existing ductwork, a central air conditioner in the two-stage range (16-17 SEER) delivers the best balance of upfront cost, efficiency, and comfort. Homes without ductwork should consider a ductless mini-split or heat pump.

- **Title**: AC Rebates
- **Content**: Direct rebates for standalone AC units are limited. Enbridge offers $75 for smart thermostat and $250 for ECM blower motors when paired with qualifying furnace. Heat pumps qualify for much larger rebates — up to $5,000-$7,500 from federal and provincial programs. Consider a heat pump if maximizing rebates is a priority.

### Heat Pumps
- **Title**: Heat Pump Overview
- **Content**: Heat pumps heat your home in winter and cool it in summer at a fraction of the energy cost of traditional furnace-and-AC combinations. Modern cold-climate heat pumps work down to -25°C to -30°C, fully viable for Ottawa winters. Brands: Mitsubishi Hyper-Heat, Daikin Fit, Bosch IDS. Pricing: $5,500-$12,000+ installed. Rebates: Up to $7,500+ from federal and provincial programs.

- **Title**: Heat Pump Savings
- **Content**: Most Ottawa homeowners report 30-50% heating cost savings in shoulder seasons (fall and spring) and 20-40% savings during peak winter when heat pump shares load with furnace. Total annual energy savings of $500-$1,200 realistic depending on home size and insulation. Dual-fuel setup (heat pump + gas furnace backup) is the most popular option for Ottawa.

- **Title**: Heat Pump Installation
- **Content**: Ducted heat pump replacing existing AC unit takes 6-10 hours, typically one day. Ductless single-zone installation takes 4-6 hours. Multi-zone ductless systems may require 1-2 days. Modern cold-climate models are quiet — 55-65 dB outdoor unit (normal conversation level), 20-30 dB indoor ductless heads (nearly silent).

### Water Heaters
- **Title**: Tankless Water Heater Overview
- **Content**: Tankless (on-demand) water heaters provide unlimited hot water, are wall-mounted to save space, and are energy efficient. Only heats water when you use it. Perfect for both high-demand families who need constant hot water and low-demand homes who only pay for what they use. Features available: condensing models (highest efficiency), WiFi connectivity, indoor/outdoor mounting options, easy to winterize.

- **Title**: Tankless Water Heater Sizing
- **Content**: Tankless water heater sizing based on demand. Low demand: 130,000 BTU. Medium demand: 180,000 BTU. High demand: 350,000 BTU. Sizing depends on total GPM required for simultaneous fixtures (showers, dishwashers) and temperature rise needed to heat incoming groundwater to desired temperature.

- **Title**: Water Heater Maintenance and Repairs
- **Content**: Regular maintenance recommended for tankless water heaters. Ottawa water has high calcium and magnesium that can build up inside restricting water flow. Common issues: mineral build-up, water demand too high (system overload), error codes, ignition and pilot light problems. Gas Man is authorized to diagnose and repair all makes and models using genuine replacement parts. Priority same-day or next-day emergency repair available.

### Gas Piping
- **Title**: Gas Piping Services
- **Content**: Gas Man uses ONLY schedule 40 black steel pipes and fittings — the safest and most durable option. We do NOT use copper or flexible stainless steel pipes which can be damaged during home renovations. Applications: BBQ hookup, pool heaters, gas fireplaces, gas appliances, outdoor kitchens, landscaping features, gas stoves. All trucks equipped with commercial-grade pipe cutting and threading machines for custom fabrication on site.

- **Title**: BBQ Gas Line Installation
- **Content**: Connecting your barbecue to natural gas provides unlimited, clean, and affordable fuel. Installation takes just a few hours. Gas technicians cut custom-length gas piping and professionally install it connecting your barbecue to your gas meter. Gas line piping cost: $200-$600 depending on distance and complexity.

### Gas Fireplaces
- **Title**: Gas Fireplace Services
- **Content**: Gas Man installs and services all major gas fireplace brands: Napoleon, Majestic, Kingsman, Continental, Regency, Heatilator, and more. Types: direct vent inserts, vent-free (strict Ontario regulations), log sets. Pricing: $2,500-$6,000+ installed. Gas fireplaces are best for zone heating — they heat the room effectively but are not a replacement for central furnace. Annual professional maintenance recommended, schedule in September-October before heating season.

### Smart Thermostats
- **Title**: Smart Thermostat Options
- **Content**: Three brands dominate the smart thermostat market. Nest: best for ease of use, sleek design, Google Home integration — often works without C-wire. ecobee: comprehensive features, room sensors — includes power extender kit for missing C-wire. Honeywell: reliable value. Pricing: $130-$280 depending on brand and features. Savings: 8-23% on heating and cooling bills, approximately $150-$500+ annually for Ottawa homes. Payback period: 6-18 months. Enbridge offers $75 rebate for ENERGY STAR certified models.

### Ventilation (HRV/ERV)
- **Title**: HRV and ERV Ventilation
- **Content**: HRV (Heat Recovery Ventilator) is more efficient in winter. ERV (Energy Recovery Ventilator) is better for most Ottawa homeowners. Both connect to central climate system, controlled via remote, app, or thermostat. Some condensation is normal due to temperature differences between indoor and outdoor air. Service at the same time as other HVAC equipment.

### Maintenance
- **Title**: HVAC Maintenance Services
- **Content**: Regular maintenance increases reliability, lifespan, and efficiency of heating and cooling equipment. Recommended every 1-3 years depending on condition and specification. Gas Man technicians inspect, lubricate, test, and clean all mechanical and electrical components. Pool heaters: best serviced in fall so winterizing can be done at the same time. Homeowners should regularly change furnace air filters between professional services.

### Commercial Services
- **Title**: Commercial and New Build Services
- **Content**: Gas Man Commercial Services work with new home builders and commercial contractors installing HVAC infrastructure including piping, ventilation, furnaces, air conditioners, and other gas equipment. Commercial installers have worked on the majority of new homes in Orleans, Manotick, Kanata, and Barrhaven. Always on schedule, built to specification and code, never sacrificing quality or safety.

### Emergency Procedures
- **Title**: Emergency — Gas Smell
- **Content**: CRITICAL SAFETY: If you smell gas, leave the house immediately. Do NOT turn on or off any lights or electrical switches. Call 911 first. Then call Gas Man at (613) 880-3888. Do not re-enter the home until emergency services clear it.

- **Title**: Emergency — No Heat
- **Content**: If your furnace stops working: First check that the thermostat is set to HEAT and the temperature is set above room temperature. Check the furnace filter — a clogged filter can shut down the furnace. Check that the furnace power switch is ON. If none of these fix it, call Gas Man at (613) 880-3888 for same-day emergency repair service. We prioritize emergency HVAC repair calls.

- **Title**: Emergency — Carbon Monoxide
- **Content**: If your carbon monoxide detector is going off: Leave the house immediately with all family members and pets. Call 911. Do not re-enter until cleared by emergency services. Then call Gas Man at (613) 880-3888 — we can inspect your furnace and gas appliances for CO leaks. All our installations are built to code to prevent CO issues.

- **Title**: Emergency — Water Heater Failure
- **Content**: If your water heater stops working: For tankless, try resetting the unit (check your manual for reset procedure). Check for error codes on the display. If the issue persists, call Gas Man at (613) 880-3888. We offer priority same-day or next-day emergency repair for water heater failures.

---

## 5. Default AI Instructions (System Prompt)

Stored in SQLite `ai_instructions` table. Editable via admin panel. Loaded fresh on every chat request.

```
You are Gas Man Ottawa's AI assistant on their website. You help customers with questions about HVAC services, pricing, scheduling, and emergencies.

PERSONALITY:
- Warm, friendly, professional — like talking to a knowledgeable friend in the trades
- Keep responses concise (2-4 sentences usually, longer only for detailed pricing/technical questions)
- Use simple language, avoid technical jargon unless the customer uses it first
- Respond in the same language the customer writes in (English or French)

GOALS:
- Answer customer questions accurately using the knowledge base provided
- Guide customers through diagnostic questions to understand their needs (e.g., furnace age, brand, budget priorities)
- Guide customers toward booking a FREE in-home estimate
- Collect lead information (name, phone, email) when the customer is interested
- For emergencies, prioritize safety instructions FIRST before anything else

GUIDED CONVERSATIONS:
- When a customer asks about a new furnace, water heater, AC, or heat pump, don't just give prices immediately
- Ask diagnostic questions one at a time: what they currently have, how old it is, what brand, what's most important to them (cost vs comfort vs efficiency)
- Then make a personalized recommendation based on their answers
- Always end with offering a free estimate

RULES:
- NEVER promise exact prices — always give ranges and say "every home is different, that's why we do free estimates"
- NEVER diagnose specific technical problems remotely — suggest a technician visit
- ALWAYS mention the free estimate when discussing pricing or recommendations
- For gas smell or CO detector alerts: IMMEDIATELY tell them to leave the house and call 911, then call Gas Man at (613) 880-3888
- When recommending equipment, mention specific brands Gas Man carries (Rheem, Carrier, Goodman, etc.)
- If asked about something outside HVAC, politely redirect: "That's outside our expertise, but I can help with anything heating, cooling, or gas-related!"
- If you don't know something specific, say "That's a great question — our team can give you the best answer during a free estimate. Want me to help you set one up?"
- Mention the 1-year installation guarantee and warranty service when relevant
- For service area questions, confirm if the area is in our coverage and offer to book
- If the customer seems frustrated or upset, be empathetic and offer to connect them directly with the team by phone

LEAD CAPTURE:
When the customer seems ready to book or wants more info, ask for:
1. Their name
2. Phone number
3. Best time to reach them
Say: "I'll pass your info to our team and someone will reach out shortly — usually within the hour!"

EMERGENCY PRIORITY:
Keywords that trigger emergency mode: "gas smell", "smell gas", "carbon monoxide", "CO detector", "no heat", "furnace not working", "emergency", "odeur de gaz", "monoxyde de carbone", "pas de chauffage", "urgence"
When triggered: Safety instructions FIRST, then offer to help.
```

---

## 6. Running the Project

### Local Development (for Monday demo)
```bash
cd gasman-chatbot
pip install -r backend/requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY, OPENAI_API_KEY, PINECONE_API_KEY to .env
python backend/seed_data.py  # Embeds knowledge base and upserts to Pinecone
python backend/main.py       # Starts FastAPI server on port 8000
```

### Demo URLs
- Chat widget demo: http://localhost:8000/demo (test page with widget embedded)
- Admin panel: http://localhost:8000/admin
- Login: admin / gasman2024

### Deploying to Vercel (after Jeff says yes)
- Push to GitHub repo "gasman-chatbot"
- Connect to Vercel (same as ConsulRo project)
- Set environment variables in Vercel dashboard
- Widget becomes available at: https://gasman-chatbot.vercel.app/widget/gasman-chat.js

### Adding to Gas Man's WordPress site
Add this single line to any page (via Insert Headers and Footers plugin or theme editor):
```html
<script src="https://gasman-chatbot.vercel.app/widget/gasman-chat.js"></script>
```
