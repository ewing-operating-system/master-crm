#!/usr/bin/env node
/**
 * Rebuild all 4 sell-side interactive proposal pages using the 10-section template.
 * ADDS sections. NEVER removes existing content.
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const SUPABASE_URL = 'https://dwrnfpjcvydhmhnvyzov.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s';
const ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3NTcyOTAsImV4cCI6MjA5MDMzMzI5MH0.z0Gu1TWdGPcdptB5W7efnYMmxBbvD353ExG99ftQivY';

function supabaseGet(endpoint) {
  return new Promise((resolve, reject) => {
    const url = `${SUPABASE_URL}/rest/v1/${endpoint}`;
    https.get(url, {
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`
      }
    }, (res) => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch(e) { reject(new Error(`Parse error: ${data.substring(0,200)}`)); }
      });
    }).on('error', reject);
  });
}

function esc(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#x27;');
}

function fmtCurrency(val) {
  if (!val || isNaN(val)) return '[TO BE CONFIRMED]';
  const n = Number(val);
  if (n >= 1000000) return '$' + (n/1000000).toFixed(1) + 'M';
  if (n >= 1000) return '$' + Math.round(n/1000).toLocaleString() + 'K';
  return '$' + n.toLocaleString();
}

function fmtNumber(val) {
  if (!val) return '[TO BE CONFIRMED]';
  return Number(val).toLocaleString();
}

// Company-specific data that supplements the DB
const COMPANY_DATA = {
  'AquaScience': {
    slug: 'aquascience',
    multiples: { low: 4.0, mid: 5.5, high: 8.0 },
    ebitdaMargin: 0.15,
    defaultCommercial: 30,
    defaultRecurring: 35,
    tradeLabel: 'Water Treatment',
    currentMultipleRange: '4.0x - 8.0x',
    activeBuyers: 25,
    recentDeals: 15,
    whyNow: [
      'EPA PFAS maximum contaminant levels (4 ppt) finalized in 2024 are creating mandatory demand for treatment solutions across New England',
      'Water treatment businesses with recurring revenue and regulatory specialization are trading at record multiples as buyers compete for scarce quality targets',
      'The northeast market has fewer quality operators than demand warrants, creating a seller\'s market for established companies with AquaScience\'s profile'
    ],
    comparables: [
      { type: 'Regional Water Treatment', size: '$12M', multiple: '6.5x', buyer: 'PE Platform', date: '2025' },
      { type: 'Water Services Provider', size: '$8M', multiple: '5.2x', buyer: 'Strategic', date: '2024' },
      { type: 'Environmental Services', size: '$15M', multiple: '7.0x', buyer: 'PE Roll-up', date: '2025' }
    ],
    snapshot: {
      fleetSize: '[TO BE CONFIRMED]',
      licenses: 'State water treatment certifications, PFAS remediation, radon mitigation',
      serviceMix: '[TO BE CONFIRMED]% Service / [TO BE CONFIRMED]% Equipment Sales',
      ebitdaMarginDisplay: '~20%',
      recurringRevenue: '~35%',
      serviceArea: 'Rhode Island and New England'
    },
    strategicBuyers: ['Culligan International', 'Pentair', 'Grundfos', 'Evoqua Water Technologies (Xylem)', 'Essential Utilities'],
    pePlatforms: [
      { name: 'BDT & MSD Partners', fund: 'BDT Capital Partners' },
      { name: 'Advent International', fund: 'Advent International GPE X' },
      { name: 'US Water Services', fund: 'Alaris Capital Partners' }
    ],
    independentCount: 15,
    regionalBuyers: ['Whitewater Management', 'Regional NE Water Operators'],
    funnelTotal: '60+',
    funnelOutreach: 40,
    funnelNDAs: 12,
    funnelIOIs: '5-8',
    funnelLOIs: '2-3',
    feeScenarios: [
      { price: '$6.4M', fee: '$448K', credit: '$10K', effective: '6.8%' },
      { price: '$8.8M', fee: '$616K', credit: '$10K', effective: '6.9%' },
      { price: '$12.8M', fee: '$896K', credit: '$10K', effective: '6.9%' }
    ],
    execSummary: `Larry, you built AquaScience from the ground up 41 years ago -- before the internet existed as a sales channel -- and turned it into one of the most trusted water treatment companies in the northeast. You've served over 100,000 customers, earned a 4.8 Google rating, and positioned the company at the exact intersection of where regulations and buyer demand are heading.

You want to sell AquaScience at the right time to the right buyer. Someone who values what you've built, keeps the team together, and pays you what the business is actually worth.

That's exactly what Next Chapter does. We represent business owners like you -- people who built something real with their hands and their reputation -- and we find the buyer who sees that value and pays for it.

Based on our preliminary review, we believe AquaScience is positioned to achieve a valuation in the range of $6.4M to $12.8M, representing approximately 4.0x to 8.0x your real profit after we add back owner perks.`,
    levers: {
      positive: [
        { name: 'Recurring Filter/Salt Delivery Revenue', desc: 'Monthly delivery routes create predictable cash flow that buyers value at 2-3x premium over one-time equipment sales.' },
        { name: 'PFAS/Radon Regulatory Specialization', desc: 'EPA mandates on PFAS (4 ppt MCL) and state radon requirements convert discretionary spending into compliance-driven demand.' },
        { name: 'Dual-Channel Model (Service + eCommerce)', desc: 'National eCommerce platform provides scalable customer acquisition that most local service companies cannot replicate.' },
        { name: '100K+ Customer Installed Base', desc: 'Massive installed base represents untapped recurring revenue activation -- the highest-ROI post-acquisition value creation play.' },
        { name: '41-Year Operating History', desc: 'Four decades of brand trust compounds into customer retention, referral networks, and premium pricing power that cannot be bought.' }
      ],
      opportunity: [
        { name: 'Owner Dependency Risk', desc: 'If Larry Casey\'s relationships and knowledge walk out the door, the acquisition risk spikes and multiples compress 1-2x.' },
        { name: 'Recurring Revenue Penetration', desc: 'Current recurring revenue percentage may underweight the installed base potential -- activating service agreements on existing customers is key.' },
        { name: 'Single-Location Operations', desc: 'Geographic concentration in Rhode Island limits addressable market; multi-location expansion would command geographic premium.' },
        { name: 'Employee Bench Depth', desc: 'With 11 employees, key-person risk extends beyond the owner -- losing 1-2 senior technicians could impact service capacity materially.' },
        { name: 'Financial Reporting Sophistication', desc: 'Accrual-based financials, job costing, and segmented reporting by service line dramatically improve buyer confidence and due diligence speed.' }
      ]
    },
    nextStepDate: 'April 14, 2026',
    phase1Date: 'April 21, 2026'
  },

  'Air Control': {
    slug: 'air-control',
    multiples: { low: 3.5, mid: 6.0, high: 8.0 },
    ebitdaMargin: 0.15,
    defaultCommercial: 30,
    defaultRecurring: 30,
    tradeLabel: 'HVAC',
    currentMultipleRange: '4.0x - 12.0x',
    activeBuyers: 40,
    recentDeals: 25,
    whyNow: [
      'HVAC is the most active home services M&A vertical in 2025-2026, with PE-backed platforms competing aggressively for quality operators in high-income metro areas',
      'The Northern Virginia / DC metro market commands geographic premiums of 1.5-2.0x above national averages because of customer density and household income',
      'With interest rates stabilizing, acquirers who paused in 2023-2024 are back in the market with fresh capital and aggressive growth mandates'
    ],
    comparables: [
      { type: 'Residential HVAC (Mid-Atlantic)', size: '$4.5M', multiple: '7.0x', buyer: 'PE Platform', date: '2025' },
      { type: 'HVAC Service Company', size: '$3.2M', multiple: '5.5x', buyer: 'Strategic', date: '2024' },
      { type: 'Home Services (DC Metro)', size: '$6M', multiple: '8.0x', buyer: 'PE Roll-up', date: '2025' }
    ],
    snapshot: {
      fleetSize: '[TO BE CONFIRMED]',
      licenses: 'Virginia HVAC contractor license, EPA 608 certifications',
      serviceMix: '[TO BE CONFIRMED]% Service / [TO BE CONFIRMED]% Install',
      ebitdaMarginDisplay: '~20%',
      recurringRevenue: '~30%',
      serviceArea: 'McLean, VA and Northern Virginia / DC Metro'
    },
    strategicBuyers: ['F.H. Furr Plumbing, Heating, AC & Electrical', 'Service Experts', 'Horizon Services'],
    pePlatforms: [
      { name: 'Ally Services / Watchtower Capital', fund: 'Watchtower Capital' },
      { name: 'Paramount Mechanical Corporation', fund: 'Stonebridge Partners' },
      { name: 'United Air Temp', fund: 'Littlejohn & Co.' }
    ],
    independentCount: 20,
    regionalBuyers: ['Apex Service Partners', 'Wrench Group', 'Redwood Services'],
    funnelTotal: '80+',
    funnelOutreach: 50,
    funnelNDAs: 15,
    funnelIOIs: '5-8',
    funnelLOIs: '2-3',
    feeScenarios: [
      { price: '$2.1M', fee: '$210K', credit: '$10K', effective: '9.5%' },
      { price: '$3.6M', fee: '$360K', credit: '$10K', effective: '9.7%' },
      { price: '$4.8M', fee: '$480K', credit: '$10K', effective: '9.8%' }
    ],
    execSummary: `Fred, you've built Air Control into a trusted HVAC operation serving one of the wealthiest zip codes in America -- McLean, Virginia. Eighteen years of clean ownership, a team that delivers, and a customer base that pays premium prices because they trust you with their home comfort.

You want to sell Air Control at the right time to the right buyer. Someone who values the relationships you've built in Northern Virginia, keeps your team employed, and writes you a check that reflects what this business is actually worth in the DC metro market.

That's what Next Chapter does. We represent HVAC owners who built their business one truck at a time, and we find the buyer who understands that a McLean address and an 18-year reputation aren't just lines on a spreadsheet -- they're worth real money.

Based on our preliminary review, we believe Air Control is positioned to achieve a valuation in the range of $2.1M to $4.8M, representing approximately 3.5x to 8.0x your real profit after we add back owner perks.`,
    levers: {
      positive: [
        { name: 'McLean/Fairfax County Premium Location', desc: 'Acquirers pay a geographic premium of 1.5-2.0x for HVAC companies in high-income metro areas where customer lifetime value significantly exceeds national averages.' },
        { name: 'Revenue-Per-Employee Efficiency', desc: '$600K revenue per employee suggests a premium service model with strong margins, making the business immediately profitable for any buyer from day one.' },
        { name: '18-Year Clean Ownership History', desc: 'Single owner-operator with nearly two decades of clean records simplifies due diligence and reduces transaction risk for buyers.' },
        { name: 'DC Metro Market Density', desc: 'Northern Virginia has one of the highest concentrations of affluent homeowners in the country -- perfect territory for HVAC service contracts.' },
        { name: 'Residential Focus Advantage', desc: 'Residential HVAC commands premium multiples in 2025-2026 because recurring maintenance contracts create predictable cash flow buyers love.' }
      ],
      opportunity: [
        { name: 'Team Size / Scalability', desc: 'At 5 employees, the business runs lean but may face capacity constraints -- adding 2-3 technicians pre-sale could increase valuation by demonstrating growth readiness.' },
        { name: 'Owner Dependency', desc: 'If Fred\'s customer relationships and operational knowledge are concentrated in his hands, buyers will discount the multiple by 1-2x for transition risk.' },
        { name: 'Recurring Revenue Formalization', desc: 'Formalizing maintenance agreements (target: 40%+ recurring) would push the multiple from the middle of the range toward the top.' },
        { name: 'Documentation and SOPs', desc: 'Written standard operating procedures and documented processes show buyers the business can run without you -- that\'s worth real money at closing.' },
        { name: 'Digital Presence / Lead Generation', desc: 'Investing in a modern website and local SEO before going to market demonstrates organic lead flow that buyers find extremely valuable.' }
      ]
    },
    nextStepDate: 'April 14, 2026',
    phase1Date: 'April 21, 2026'
  },

  'Springer Floor': {
    slug: 'springer-floor',
    multiples: { low: 3.0, mid: 4.5, high: 6.5 },
    ebitdaMargin: 0.15,
    defaultCommercial: 40,
    defaultRecurring: 30,
    tradeLabel: 'Floor Care / Carpet Cleaning',
    currentMultipleRange: '3.0x - 6.5x',
    activeBuyers: 20,
    recentDeals: 10,
    whyNow: [
      'Commercial facility maintenance is seeing increased PE interest as investors recognize the recurring revenue characteristics and essential-service nature of floor care',
      'The Forever Kleen recurring revenue program puts Springer Floor in the top tier of floor care operators nationally -- buyers will pay a premium for subscription models',
      'Iowa\'s central location and 26-city footprint make Springer Floor an ideal Midwest beachhead for national consolidators'
    ],
    comparables: [
      { type: 'Commercial Floor Care', size: '$1.2M', multiple: '5.0x', buyer: 'PE Platform', date: '2025' },
      { type: 'Carpet Cleaning Service', size: '$800K', multiple: '3.5x', buyer: 'Regional', date: '2024' },
      { type: 'Facility Services', size: '$2M', multiple: '5.5x', buyer: 'Strategic', date: '2025' }
    ],
    snapshot: {
      fleetSize: '[TO BE CONFIRMED]',
      licenses: 'IICRC Master Certification, National Instructor credentials',
      serviceMix: '[TO BE CONFIRMED]% Commercial / [TO BE CONFIRMED]% Residential',
      ebitdaMarginDisplay: '~22%',
      recurringRevenue: 'Forever Kleen subscribers + commercial contracts',
      serviceArea: '26 cities across Iowa and surrounding states'
    },
    strategicBuyers: ['Stanley Steemer', 'COIT Cleaning and Restoration', 'ABM Industries', 'Cintas Corporation', 'Pritchard Industries'],
    pePlatforms: [
      { name: 'milliCare', fund: 'The Riverside Company' },
      { name: 'ServiceMaster Brands', fund: 'Roark Capital' },
      { name: 'NEXClean', fund: 'Rainier Partners' }
    ],
    independentCount: 10,
    regionalBuyers: ['Marsden Holding (St. Paul, MN)', 'Midwest facility services operators'],
    funnelTotal: '50+',
    funnelOutreach: 35,
    funnelNDAs: 10,
    funnelIOIs: '4-6',
    funnelLOIs: '2-3',
    feeScenarios: [
      { price: '$600K', fee: '$60K', credit: '$10K', effective: '8.3%' },
      { price: '$900K', fee: '$90K', credit: '$10K', effective: '8.9%' },
      { price: '$1.3M', fee: '$130K', credit: '$10K', effective: '9.2%' }
    ],
    execSummary: `Terri, you've built Springer Floor Care into something most floor care companies never achieve -- a 26-city operation with an IICRC national instructor on staff and a recurring revenue program (Forever Kleen) that keeps customers coming back quarter after quarter. That's not just a cleaning company. That's a platform.

You want to sell Springer Floor Care at the right time to the right buyer. Someone who recognizes that the Forever Kleen program, the IICRC credential, and the 26-city territory aren't just selling points -- they're the exact assets that strategic buyers and PE groups are paying top dollar for right now.

That's what Next Chapter does. We represent owners who built their business on quality work and repeat customers, and we find the buyer who understands the difference between a company that cleans floors and a platform that owns a territory.

Based on our preliminary review, we believe Springer Floor Care is positioned to achieve a valuation in the range of $600K to $1.3M, representing approximately 3.0x to 6.5x your real profit after we add back owner perks.`,
    levers: {
      positive: [
        { name: 'Forever Kleen Recurring Revenue Program', desc: 'Quarterly subscription model transforms one-time customers into repeat revenue. Buyers pay a premium for businesses where customers come back automatically.' },
        { name: 'IICRC National Instructor on Staff', desc: 'Having a nationally certified instructor gives Springer Floor institutional credibility, a training pipeline, and technical authority that commands pricing power.' },
        { name: '26-City Service Territory', desc: 'An acquirer would need 3-5 years and significant capital to replicate this geographic footprint organically. Territory = value.' },
        { name: 'Commercial Contract Base', desc: 'Commercial customers with recurring floor care needs provide predictable revenue that banks and buyers can underwrite with confidence.' },
        { name: 'Brand Recognition Across Iowa', desc: 'Decades of presence across 26 cities creates a brand moat that new entrants cannot buy or build quickly.' }
      ],
      opportunity: [
        { name: 'Revenue Scale', desc: 'At ~$900K revenue, the business sits at the lower end of institutional buyer interest. Growing to $1.2M+ pre-sale would unlock a wider buyer pool and higher multiples.' },
        { name: 'Owner Transition Planning', desc: 'Documenting key relationships, processes, and operational knowledge ensures the business value transfers fully to the new owner.' },
        { name: 'Technology and CRM Systems', desc: 'Modern scheduling, CRM, and route optimization tools demonstrate operational maturity and reduce buyer integration risk.' },
        { name: 'Upsell Penetration on Existing Accounts', desc: 'Cross-selling additional services (tile, hardwood, restoration) to existing Forever Kleen subscribers represents untapped revenue growth.' },
        { name: 'Financial Reporting Clarity', desc: 'Clean, segmented financials by service line and territory make buyer due diligence faster and support higher confidence in the numbers.' }
      ]
    },
    nextStepDate: 'April 14, 2026',
    phase1Date: 'April 21, 2026'
  },

  'HR.com Ltd': {
    slug: 'hrcom-ltd',
    multiples: { low: 3.0, mid: 5.0, high: 8.0 },
    ebitdaMargin: 0.20,
    defaultCommercial: 100,
    defaultRecurring: 60,
    tradeLabel: 'HR Technology & Media',
    currentMultipleRange: '5.0x - 15.0x',
    activeBuyers: 30,
    recentDeals: 20,
    whyNow: [
      'HR technology platforms with engaged communities are trading at record valuations as enterprises invest in workforce management and compliance tools',
      'The HR.com domain alone carries significant strategic value -- two-letter .com domains in major industry verticals are irreplaceable assets',
      'AI-driven transformation of HR is creating acquisition urgency among platforms seeking community access and content distribution channels'
    ],
    comparables: [
      { type: 'HR Media Platform', size: '$25M', multiple: '8.0x', buyer: 'PE Platform', date: '2025' },
      { type: 'B2B Community Platform', size: '$40M', multiple: '10.0x', buyer: 'Strategic', date: '2024' },
      { type: 'HR Tech & Events', size: '$18M', multiple: '6.0x', buyer: 'PE Roll-up', date: '2025' }
    ],
    snapshot: {
      fleetSize: 'N/A (Digital Platform)',
      licenses: 'HRCI/SHRM accredited content provider',
      serviceMix: 'Events / Certifications / Media / Sponsorship',
      ebitdaMarginDisplay: '[TO BE CONFIRMED]',
      recurringRevenue: '~60% (subscriptions + recurring sponsorships)',
      serviceArea: 'Global (HQ: Grimsby, Ontario)'
    },
    strategicBuyers: ['Paychex', 'ADP', 'SAP SuccessFactors', 'Workday'],
    pePlatforms: [
      { name: 'Thoma Bravo', fund: 'Thoma Bravo Fund XV' },
      { name: 'Vista Equity Partners', fund: 'Vista Equity Fund VIII' },
      { name: 'HG Capital', fund: 'HG Capital Trust' }
    ],
    independentCount: 12,
    regionalBuyers: ['Deel (San Francisco)', 'Randstad Digital'],
    funnelTotal: '50+',
    funnelOutreach: 30,
    funnelNDAs: 12,
    funnelIOIs: '4-6',
    funnelLOIs: '2-3',
    feeScenarios: [
      { price: '$42M', fee: '$2.1M', credit: '$10K', effective: '5.0%' },
      { price: '$64M', fee: '$3.2M', credit: '$10K', effective: '5.0%' },
      { price: '$125M', fee: '$6.25M', credit: '$10K', effective: '5.0%' }
    ],
    execSummary: `Debbie, you built HR.com from scratch in 1999 and turned it into the world's largest community of HR professionals. You own one of the most valuable two-letter domain names on the internet. You've built a content engine, a certification platform, and an events business that reaches millions of HR decision-makers every year.

You want to sell HR.com at the right time to the right buyer. Someone who recognizes that the domain, the community, and the platform you built over 27 years aren't just a media company -- they're a strategic asset that gives the buyer instant access to the entire HR industry.

That's what Next Chapter does. We represent founders who built platforms that define their industry, and we find the buyer who understands the difference between building a community from scratch and acquiring one that already commands the space.

Based on our preliminary review, we believe HR.com is positioned to achieve a valuation in the range of $42M to $125M, representing the combined value of the platform, community, domain, and content assets.`,
    levers: {
      positive: [
        { name: 'Two-Letter .com Domain (HR.com)', desc: 'One of the most valuable domain names in the HR industry. Specialist brokers value it at $15-20M standalone. It drives organic traffic, brand authority, and instant credibility.' },
        { name: 'Largest HR Professional Community', desc: 'Millions of HR decision-makers engaged on the platform. This audience is the product that strategic buyers cannot replicate without years of investment.' },
        { name: 'HRCI/SHRM Accredited Content Engine', desc: 'Accredited certification content creates a recurring engagement loop. HR professionals return because they need the credentials, not just because they want to.' },
        { name: 'Multi-Revenue-Stream Platform', desc: 'Events, certifications, media sponsorships, and subscriptions create diversified revenue that reduces risk and increases valuation multiples.' },
        { name: '27-Year Brand Authority', desc: 'Founded in 1999 and continuously operating for 27 years. This kind of institutional brand trust in the HR space is irreplaceable.' }
      ],
      opportunity: [
        { name: 'Revenue Disclosure', desc: 'Financial transparency with potential buyers is critical. Audited financials and clear revenue segmentation will unlock the highest multiples.' },
        { name: 'AI Integration Strategy', desc: 'Demonstrating an AI-powered roadmap for the platform (personalization, content matching, community engagement) dramatically increases strategic value.' },
        { name: 'Enterprise Sales Channel', desc: 'Formalizing enterprise sales (corporate HR department subscriptions) would create a high-value recurring revenue stream that commands premium multiples.' },
        { name: 'International Expansion Potential', desc: 'Showing a clear playbook for international growth gives buyers a value creation thesis that justifies paying a premium today.' },
        { name: 'Founder Transition Plan', desc: 'A documented transition plan showing the business can thrive post-Debbie reduces buyer risk perception and protects the multiple.' }
      ]
    },
    nextStepDate: 'April 14, 2026',
    phase1Date: 'April 21, 2026'
  }
};

function generateProposal(dbData, cd, buyers) {
  const companyName = dbData.company_name;
  const ownerName = dbData.owner_name;
  const vertical = dbData.vertical;
  const city = dbData.city;
  const state = dbData.state;
  const revenue = dbData.estimated_revenue;
  const employees = dbData.employee_count;
  const yearsInBusiness = dbData.years_in_business;
  const strengths = dbData.top_3_strengths || [];
  const narrative = dbData.company_narrative || '';
  const marketAnalysis = dbData.market_analysis || '';
  const attackPlan = dbData.attack_plan || '';
  const valRange = dbData.valuation_range || {};
  const evLow = dbData.estimated_ev_low;
  const evMid = dbData.estimated_ev_mid;
  const evHigh = dbData.estimated_ev_high;
  const engagementFee = dbData.engagement_fee || 10000;
  const successFeePct = dbData.success_fee_pct || 7;

  const revenueNum = parseFloat(String(revenue).replace(/[^0-9.]/g,'')) || 0;
  const employeeNum = parseInt(String(employees).replace(/[^0-9]/g,'')) || 0;
  const yearsNum = yearsInBusiness ? (yearsInBusiness > 1900 ? 2026 - yearsInBusiness : yearsInBusiness) : 0;

  // Get real buyers for this company
  const companyBuyers = buyers.filter(b =>
    b.entity === companyName ||
    b.entity === companyName + ' LLC' ||
    b.entity === cd.slug
  );

  const strategicBuyersList = cd.strategicBuyers.map(b => `<li>${esc(b)}</li>`).join('\n                    ');
  const pePlatformsList = cd.pePlatforms.map(b => `<li>${esc(b.name)} <span style="color:var(--text-secondary)">(backed by ${esc(b.fund)})</span></li>`).join('\n                    ');
  const regionalBuyersList = cd.regionalBuyers.map(b => `<li>${esc(b)}</li>`).join('\n                    ');

  const comparablesRows = cd.comparables.map(c => `
                    <tr>
                        <td>${esc(c.type)}</td>
                        <td>${esc(c.size)}</td>
                        <td>${esc(c.multiple)}</td>
                        <td>${esc(c.buyer)}</td>
                        <td>${esc(c.date)}</td>
                    </tr>`).join('');

  const feeRows = cd.feeScenarios.map(f => `
                    <tr>
                        <td>${esc(f.price)}</td>
                        <td>${esc(f.fee)}</td>
                        <td>${esc(f.credit)}</td>
                        <td>${esc(f.effective)}</td>
                    </tr>`).join('');

  // Build EBITDA levers from existing HTML data (preserved from originals)
  const narrativeParagraphs = narrative.split('\n').filter(p => p.trim()).map(p => `<p>${esc(p)}</p>`).join('\n');
  const marketParagraphs = marketAnalysis.split('\n').filter(p => p.trim()).map(p => `<p>${esc(p)}</p>`).join('\n');

  const strengthsHtml = strengths.map((s, i) => `
            <div class="strength-card">
                <div class="strength-number">${i+1}</div>
                <p>${esc(s)}</p>
            </div>`).join('');

  const whyNowHtml = cd.whyNow.map(w => `<li>${esc(w)}</li>`).join('\n                    ');

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Confidential Proposal &mdash; ${esc(companyName)} | Next Chapter M&amp;A Advisory</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-tertiary: #21262d;
    --bg-card: #1c2128;
    --text-primary: #c9d1d9;
    --text-secondary: #8b949e;
    --text-heading: #e6edf3;
    --accent: #58a6ff;
    --accent-hover: #79b8ff;
    --green: #3fb950;
    --green-bg: rgba(63, 185, 80, 0.1);
    --green-border: rgba(63, 185, 80, 0.3);
    --amber: #d29922;
    --amber-bg: rgba(210, 153, 34, 0.1);
    --amber-border: rgba(210, 153, 34, 0.3);
    --red: #f85149;
    --border: #30363d;
    --border-light: #21262d;
    --gradient-start: #58a6ff;
    --gradient-end: #a371f7;
}
* { margin:0; padding:0; box-sizing:border-box; }
html { scroll-behavior: smooth; }
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.7;
    font-size: 15px;
}
.container { max-width: 1000px; margin: 0 auto; padding: 40px 24px; }

/* Section 1: Cover Header */
.header {
    background: linear-gradient(135deg, #161b22 0%, #0d1117 50%, #161b22 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 48px 40px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--gradient-start), var(--gradient-end));
}
.header h1 {
    font-size: 36px;
    font-weight: 800;
    color: var(--text-heading);
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}
.header .firm-tagline {
    font-size: 16px;
    color: var(--accent);
    font-weight: 500;
    margin-bottom: 16px;
}
.header .engagement-type {
    display: inline-block;
    background: rgba(88,166,255,0.1);
    border: 1px solid rgba(88,166,255,0.3);
    border-radius: 20px;
    padding: 4px 16px;
    font-size: 12px;
    font-weight: 600;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 16px;
}
.header-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-top: 16px;
    font-size: 14px;
    color: var(--text-secondary);
}
.header-meta span {
    display: flex;
    align-items: center;
    gap: 6px;
}
.header-meta .dot { color: var(--accent); }
.confidential {
    margin-top: 20px;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--text-secondary);
    opacity: 0.7;
}

/* General sections */
.section {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 36px;
    margin-bottom: 24px;
}
.section-title {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-heading);
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-title .icon {
    font-size: 20px;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: rgba(88,166,255,0.1);
}
.section p { margin-bottom: 14px; color: var(--text-primary); }

/* Strengths */
.strengths-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
}
.strength-card {
    background: var(--green-bg);
    border: 1px solid var(--green-border);
    border-radius: 10px;
    padding: 20px;
    position: relative;
}
.strength-card .strength-number {
    position: absolute;
    top: 12px;
    right: 14px;
    font-size: 36px;
    font-weight: 800;
    color: var(--green);
    opacity: 0.2;
}
.strength-card p { font-size: 14px; line-height: 1.6; color: var(--text-primary); margin: 0; }

/* Sliders */
.slider-group { margin-bottom: 28px; }
.slider-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}
.slider-label-text { font-weight: 600; font-size: 14px; color: var(--text-heading); }
.slider-value {
    font-weight: 700;
    font-size: 18px;
    color: var(--accent);
    min-width: 120px;
    text-align: right;
}
.slider-row { display: flex; align-items: center; gap: 16px; }
.slider-row input[type="range"] { flex: 1; }
.slider-row input[type="number"] {
    width: 130px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 12px;
    color: var(--text-heading);
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 600;
    text-align: right;
}
.slider-row input[type="number"]:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(88,166,255,0.15);
}
.split-display {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 8px;
    font-size: 13px;
    color: var(--text-secondary);
}
.split-display span { padding: 4px 12px; border-radius: 6px; background: var(--bg-tertiary); }
input[type="range"] {
    -webkit-appearance: none;
    appearance: none;
    height: 6px;
    border-radius: 3px;
    background: var(--bg-tertiary);
    outline: none;
    cursor: pointer;
}
input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: var(--accent);
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(88,166,255,0.3);
    transition: transform 0.15s, box-shadow 0.15s;
}
input[type="range"]::-webkit-slider-thumb:hover {
    transform: scale(1.15);
    box-shadow: 0 2px 12px rgba(88,166,255,0.5);
}
input[type="range"]::-moz-range-thumb {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: var(--accent);
    cursor: pointer;
    border: none;
}

/* Valuation */
.valuation-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}
.val-box {
    text-align: center;
    padding: 28px 20px;
    border-radius: 12px;
    border: 1px solid var(--border);
    transition: transform 0.2s, box-shadow 0.2s;
}
.val-box:hover { transform: translateY(-2px); }
.val-box.conservative { background: rgba(139, 148, 158, 0.08); border-color: rgba(139, 148, 158, 0.3); }
.val-box.likely { background: rgba(88, 166, 255, 0.08); border-color: rgba(88, 166, 255, 0.3); box-shadow: 0 0 20px rgba(88, 166, 255, 0.05); }
.val-box.optimistic { background: rgba(63, 185, 80, 0.08); border-color: rgba(63, 185, 80, 0.3); }
.val-label { font-size: 12px; text-transform: uppercase; letter-spacing: 1.5px; color: var(--text-secondary); margin-bottom: 8px; }
.val-amount { font-size: 30px; font-weight: 800; letter-spacing: -0.5px; }
.val-box.conservative .val-amount { color: var(--text-secondary); }
.val-box.likely .val-amount { color: var(--accent); }
.val-box.optimistic .val-amount { color: var(--green); }
.methodology {
    background: var(--bg-tertiary);
    border-radius: 8px;
    padding: 16px 20px;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.7;
    border-left: 3px solid var(--accent);
}

/* EBITDA Levers */
.levers-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.levers-column h3 {
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}
.levers-column.positive h3 { color: var(--green); }
.levers-column.opportunity h3 { color: var(--amber); }
.lever-card {
    display: flex;
    gap: 12px;
    padding: 14px;
    border-radius: 8px;
    margin-bottom: 10px;
    transition: transform 0.15s;
}
.lever-card:hover { transform: translateX(4px); }
.lever-positive { background: var(--green-bg); border: 1px solid var(--green-border); }
.lever-opportunity { background: var(--amber-bg); border: 1px solid var(--amber-border); }
.lever-icon {
    font-size: 12px;
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    margin-top: 2px;
}
.lever-positive .lever-icon { color: var(--green); background: rgba(63,185,80,0.15); }
.lever-opportunity .lever-icon { color: var(--amber); background: rgba(210,153,34,0.15); }
.lever-name { font-weight: 600; font-size: 14px; color: var(--text-heading); margin-bottom: 4px; }
.lever-desc { font-size: 13px; color: var(--text-secondary); line-height: 1.5; }

/* Fee cards */
.fee-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
.fee-card {
    background: var(--bg-card);
    border: 2px solid var(--border);
    border-radius: 12px;
    padding: 28px 24px;
    cursor: pointer;
    transition: all 0.25s;
    position: relative;
    text-align: center;
}
.fee-card:hover {
    border-color: var(--accent);
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}
.fee-card.selected {
    border-color: var(--accent);
    background: rgba(88,166,255,0.06);
    box-shadow: 0 0 30px rgba(88,166,255,0.15);
}
.fee-card.popular::before {
    content: 'MOST POPULAR';
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--accent);
    color: #fff;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 3px 12px;
    border-radius: 10px;
}
.fee-option-name { font-size: 18px; font-weight: 700; color: var(--text-heading); margin-bottom: 4px; }
.fee-option-subtitle { font-size: 12px; color: var(--text-secondary); margin-bottom: 20px; }
.fee-detail { padding: 8px 0; border-bottom: 1px solid var(--border-light); font-size: 14px; }
.fee-detail:last-child { border-bottom: none; }
.fee-detail .label { color: var(--text-secondary); font-size: 12px; }
.fee-detail .value { font-weight: 700; color: var(--text-heading); font-size: 20px; }
.fee-tagline { margin-top: 16px; font-size: 13px; font-style: italic; color: var(--text-secondary); }
.checkmark {
    display: none;
    position: absolute;
    top: 14px;
    right: 14px;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--accent);
    color: #fff;
    font-size: 16px;
    align-items: center;
    justify-content: center;
}
.fee-card.selected .checkmark { display: flex; }

/* CTA */
.cta-section { text-align: center; padding: 40px; }
.cta-btn {
    display: none;
    margin: 0 auto;
    padding: 18px 48px;
    font-size: 18px;
    font-weight: 700;
    color: #fff;
    background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s;
    font-family: inherit;
    letter-spacing: 0.5px;
}
.cta-btn.visible { display: inline-block; }
.cta-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(88,166,255,0.3);
}
.confirmation {
    display: none;
    text-align: center;
    padding: 40px;
    background: var(--green-bg);
    border: 1px solid var(--green-border);
    border-radius: 12px;
    margin-top: 20px;
}
.confirmation.show { display: block; }
.confirmation h3 { color: var(--green); font-size: 24px; margin-bottom: 12px; }
.confirmation p { color: var(--text-primary); font-size: 16px; }

/* TOC */
.toc {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px 36px;
    margin-bottom: 24px;
}
.toc-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
}
.toc-list {
    list-style: none;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px 24px;
}
.toc-list a {
    color: var(--accent);
    text-decoration: none;
    font-size: 14px;
    padding: 4px 0;
    display: block;
    transition: color 0.15s;
}
.toc-list a:hover { color: var(--accent-hover); text-decoration: underline; }
.drivers-list { list-style: none; padding: 0; }
.drivers-list li {
    padding: 10px 0;
    border-bottom: 1px solid var(--border-light);
    font-size: 14px;
    color: var(--text-primary);
    display: flex;
    gap: 10px;
    align-items: flex-start;
}
.drivers-list li::before { content: '\\2713'; color: var(--green); font-weight: bold; flex-shrink: 0; }

/* New: Tables */
.data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 14px;
}
.data-table th {
    background: var(--bg-tertiary);
    color: var(--text-heading);
    font-weight: 600;
    padding: 12px 16px;
    text-align: left;
    border-bottom: 2px solid var(--border);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.data-table td {
    padding: 10px 16px;
    border-bottom: 1px solid var(--border-light);
    color: var(--text-primary);
}
.data-table tr:hover td { background: rgba(88,166,255,0.03); }

/* New: Process phases */
.phase-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.phase-card {
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    position: relative;
}
.phase-card .phase-number {
    position: absolute;
    top: 12px;
    right: 14px;
    font-size: 48px;
    font-weight: 800;
    color: var(--accent);
    opacity: 0.1;
}
.phase-card h4 {
    color: var(--accent);
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}
.phase-card .phase-weeks {
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 12px;
}
.phase-card ul {
    list-style: none;
    padding: 0;
}
.phase-card li {
    font-size: 13px;
    color: var(--text-primary);
    padding: 4px 0;
    display: flex;
    gap: 8px;
    align-items: flex-start;
}
.phase-card li::before {
    content: '\\25A2';
    color: var(--accent);
    flex-shrink: 0;
    margin-top: 1px;
}

/* New: Buyer funnel */
.funnel-bar {
    display: flex;
    align-items: center;
    margin: 8px 0;
    gap: 12px;
}
.funnel-label {
    width: 120px;
    text-align: right;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-heading);
    flex-shrink: 0;
}
.funnel-fill {
    height: 28px;
    border-radius: 6px;
    background: linear-gradient(90deg, var(--gradient-start), var(--gradient-end));
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 10px;
    font-size: 12px;
    font-weight: 700;
    color: #fff;
    min-width: 40px;
    transition: width 0.5s;
}

/* New: Snapshot grid */
.snapshot-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
}
.snapshot-item {
    background: var(--bg-tertiary);
    border-radius: 8px;
    padding: 14px 16px;
}
.snapshot-item .snap-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-secondary);
    margin-bottom: 4px;
}
.snapshot-item .snap-value {
    font-size: 16px;
    font-weight: 700;
    color: var(--text-heading);
}

/* New: Next steps */
.next-step-box {
    background: linear-gradient(135deg, rgba(88,166,255,0.08), rgba(163,113,247,0.08));
    border: 2px solid var(--accent);
    border-radius: 12px;
    padding: 32px;
    text-align: center;
}
.next-step-box h3 {
    color: var(--accent);
    font-size: 20px;
    margin-bottom: 16px;
}
.next-step-box .step-action {
    font-size: 16px;
    color: var(--text-heading);
    font-weight: 600;
    margin-bottom: 8px;
}
.next-step-box .step-date {
    font-size: 14px;
    color: var(--text-secondary);
}

/* Fee illustration table */
.fee-illustration {
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid var(--border);
}
.fee-illustration h4 {
    color: var(--text-heading);
    margin-bottom: 12px;
    font-size: 16px;
}
.fee-note {
    margin-top: 12px;
    font-size: 13px;
    color: var(--text-secondary);
    font-style: italic;
}

@media (max-width: 768px) {
    .container { padding: 16px; }
    .header { padding: 28px 20px; }
    .header h1 { font-size: 26px; }
    .section { padding: 24px 20px; }
    .valuation-grid { grid-template-columns: 1fr; }
    .fee-grid { grid-template-columns: 1fr; }
    .levers-grid { grid-template-columns: 1fr; }
    .phase-grid { grid-template-columns: 1fr; }
    .toc-list { grid-template-columns: 1fr; }
    .val-amount { font-size: 24px; }
    .slider-row { flex-direction: column; }
    .slider-row input[type="number"] { width: 100%; }
    .snapshot-grid { grid-template-columns: 1fr 1fr; }
}
@media print {
    body { background: #fff; color: #1a1a2e; }
    .section { border: 1px solid #ddd; break-inside: avoid; }
    .fee-card { break-inside: avoid; }
    input[type="range"] { display: none; }
}
</style>
</head>
<body>
<div class="container">

    <!-- SECTION 1: COVER PAGE HEADER -->
    <div class="header" id="top">
        <div class="firm-tagline">Next Chapter M&amp;A Advisory</div>
        <div class="engagement-type">Sell-Side Advisory</div>
        <h1>${esc(companyName)}</h1>
        <div class="header-meta">
            <span><span class="dot">&#9679;</span> ${esc(ownerName)}</span>
            <span><span class="dot">&#9679;</span> ${esc(vertical)}</span>
            <span><span class="dot">&#9679;</span> ${esc(city)}, ${esc(state)}</span>
            ${yearsNum ? `<span><span class="dot">&#9679;</span> Est. ${yearsInBusiness > 1900 ? yearsInBusiness : 'N/A'}</span>` : ''}
        </div>
        <div class="confidential">Confidential Advisory Proposal &mdash; Prepared by Next Chapter M&amp;A Advisory &mdash; March 2026</div>
    </div>

    <!-- TABLE OF CONTENTS -->
    <div class="toc">
        <div class="toc-title">Quick Navigation</div>
        <ul class="toc-list">
            <li><a href="#exec-summary">Executive Summary</a></li>
            <li><a href="#market-overview">Market Overview</a></li>
            <li><a href="#snapshot">Company Snapshot</a></li>
            <li><a href="#story">Your Company Story</a></li>
            <li><a href="#strengths">Top 3 Strengths</a></li>
            <li><a href="#profile">Interactive Business Profile</a></li>
            <li><a href="#valuation">Estimated Value Range</a></li>
            <li><a href="#levers">What Drives Your Valuation</a></li>
            <li><a href="#process">Our Process</a></li>
            <li><a href="#buyers">Buyer Universe</a></li>
            <li><a href="#fees">Fee Structure</a></li>
            <li><a href="#attack">How We Would Sell Your Business</a></li>
            <li><a href="#next-steps">Next Steps</a></li>
        </ul>
    </div>

    <!-- SECTION 2: EXECUTIVE SUMMARY -->
    <div class="section" id="exec-summary">
        <div class="section-title"><div class="icon">&#128172;</div> A Personal Note</div>
        ${cd.execSummary.split('\n\n').map(p => `<p>${esc(p.trim())}</p>`).join('\n        ')}
        <p>This proposal outlines our approach, timeline, fee structure, and the specific steps we will take to get you the best outcome.</p>
    </div>

    <!-- SECTION 3: MARKET OVERVIEW -->
    <div class="section" id="market-overview">
        <div class="section-title"><div class="icon">&#128200;</div> ${esc(cd.tradeLabel)} M&amp;A Market Overview</div>

        <div class="snapshot-grid" style="margin-bottom: 24px;">
            <div class="snapshot-item">
                <div class="snap-label">Current Multiples</div>
                <div class="snap-value">${esc(cd.currentMultipleRange)}</div>
            </div>
            <div class="snapshot-item">
                <div class="snap-label">Active Buyers</div>
                <div class="snap-value">${cd.activeBuyers}+</div>
            </div>
            <div class="snapshot-item">
                <div class="snap-label">Recent Deals (12 mo)</div>
                <div class="snap-value">${cd.recentDeals}+</div>
            </div>
        </div>

        <h4 style="color: var(--text-heading); margin-bottom: 12px; font-size: 16px;">Why Now</h4>
        <ul class="drivers-list" style="margin-bottom: 24px;">
            ${whyNowHtml}
        </ul>

        <h4 style="color: var(--text-heading); margin-bottom: 12px; font-size: 16px;">Recent Comparable Transactions</h4>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Company Type</th>
                    <th>Deal Size</th>
                    <th>Multiple</th>
                    <th>Buyer Type</th>
                    <th>Year</th>
                </tr>
            </thead>
            <tbody>${comparablesRows}
            </tbody>
        </table>

        ${marketParagraphs ? `<div style="margin-top: 20px;">${marketParagraphs}</div>` : ''}
    </div>

    <!-- SECTION 4: COMPANY SNAPSHOT -->
    <div class="section" id="snapshot">
        <div class="section-title"><div class="icon">&#128202;</div> ${esc(companyName)} &mdash; At a Glance</div>
        <div class="snapshot-grid">
            <div class="snapshot-item">
                <div class="snap-label">Trade Vertical</div>
                <div class="snap-value">${esc(vertical)}</div>
            </div>
            ${yearsNum ? `<div class="snapshot-item">
                <div class="snap-label">Year Founded</div>
                <div class="snap-value">${yearsInBusiness > 1900 ? yearsInBusiness : '[TO BE CONFIRMED]'}</div>
            </div>` : ''}
            <div class="snapshot-item">
                <div class="snap-label">Location</div>
                <div class="snap-value">${esc(city)}, ${esc(state)}</div>
            </div>
            <div class="snapshot-item">
                <div class="snap-label">Employees</div>
                <div class="snap-value">${esc(String(employees))}</div>
            </div>
            <div class="snapshot-item">
                <div class="snap-label">Annual Revenue</div>
                <div class="snap-value">${revenueNum ? fmtCurrency(revenueNum) : esc(String(revenue))}</div>
            </div>
            <div class="snapshot-item">
                <div class="snap-label">EBITDA Margin</div>
                <div class="snap-value">${esc(cd.snapshot.ebitdaMarginDisplay)}</div>
            </div>
            <div class="snapshot-item">
                <div class="snap-label">Revenue Mix</div>
                <div class="snap-value">${esc(cd.snapshot.serviceMix)}</div>
            </div>
            <div class="snapshot-item">
                <div class="snap-label">Recurring Revenue</div>
                <div class="snap-value">${esc(cd.snapshot.recurringRevenue)}</div>
            </div>
            <div class="snapshot-item">
                <div class="snap-label">Licenses</div>
                <div class="snap-value" style="font-size: 13px;">${esc(cd.snapshot.licenses)}</div>
            </div>
            <div class="snapshot-item">
                <div class="snap-label">Fleet Size</div>
                <div class="snap-value">${esc(cd.snapshot.fleetSize)}</div>
            </div>
            <div class="snapshot-item">
                <div class="snap-label">Service Area</div>
                <div class="snap-value" style="font-size: 13px;">${esc(cd.snapshot.serviceArea)}</div>
            </div>
        </div>
    </div>

    <!-- EXISTING: Company Story -->
    <div class="section" id="story">
        <div class="section-title"><div class="icon">&#128214;</div> Your Company Story</div>
        ${narrativeParagraphs}
    </div>

    <!-- EXISTING: Top 3 Strengths -->
    <div class="section" id="strengths">
        <div class="section-title"><div class="icon">&#9733;</div> Your Top 3 Strengths</div>
        <div class="strengths-grid">${strengthsHtml}
        </div>
    </div>

    <!-- EXISTING: Interactive Business Profile (Sliders) -->
    <div class="section" id="profile">
        <div class="section-title"><div class="icon">&#9881;</div> Interactive Business Profile</div>
        <p style="color: var(--text-secondary); font-size: 13px; margin-bottom: 24px;">
            Adjust these sliders to see how changes in your business metrics impact what your business is worth. All changes are saved automatically.
        </p>

        <div class="slider-group">
            <div class="slider-label">
                <span class="slider-label-text">Estimated Annual Revenue</span>
                <span class="slider-value" id="revenue-display">${fmtCurrency(revenueNum)}</span>
            </div>
            <div class="slider-row">
                <input type="range" id="revenue-slider" min="500000" max="50000000" step="100000" value="${revenueNum || 1000000}">
                <input type="number" id="revenue-input" min="500000" max="50000000" step="100000" value="${revenueNum || 1000000}">
            </div>
        </div>

        <div class="slider-group">
            <div class="slider-label">
                <span class="slider-label-text">Employee Count</span>
                <span class="slider-value" id="employees-display">${employeeNum || 10}</span>
            </div>
            <div class="slider-row">
                <input type="range" id="employees-slider" min="1" max="200" step="1" value="${employeeNum || 10}">
                <input type="number" id="employees-input" min="1" max="200" step="1" value="${employeeNum || 10}">
            </div>
        </div>

        <div class="slider-group">
            <div class="slider-label">
                <span class="slider-label-text">Commercial vs Residential Split</span>
                <span class="slider-value" id="split-display">${cd.defaultCommercial}% / ${100 - cd.defaultCommercial}%</span>
            </div>
            <div class="slider-row">
                <input type="range" id="commercial-slider" min="0" max="100" step="5" value="${cd.defaultCommercial}">
                <input type="number" id="commercial-input" min="0" max="100" step="5" value="${cd.defaultCommercial}">
            </div>
            <div class="split-display">
                <span>Commercial: <strong id="commercial-pct">${cd.defaultCommercial}%</strong></span>
                <span>Residential: <strong id="residential-pct">${100 - cd.defaultCommercial}%</strong></span>
            </div>
        </div>

        <div class="slider-group">
            <div class="slider-label">
                <span class="slider-label-text">Recurring Revenue %</span>
                <span class="slider-value" id="recurring-display">${cd.defaultRecurring}%</span>
            </div>
            <div class="slider-row">
                <input type="range" id="recurring-slider" min="0" max="100" step="5" value="${cd.defaultRecurring}">
                <input type="number" id="recurring-input" min="0" max="100" step="5" value="${cd.defaultRecurring}">
            </div>
        </div>

        <div class="slider-group">
            <div class="slider-label">
                <span class="slider-label-text">Years in Business</span>
                <span class="slider-value" id="years-display">${yearsNum || 10}</span>
            </div>
            <div class="slider-row">
                <input type="range" id="years-slider" min="1" max="100" step="1" value="${yearsNum || 10}">
                <input type="number" id="years-input" min="1" max="100" step="1" value="${yearsNum || 10}">
            </div>
        </div>
    </div>

    <!-- EXISTING: Estimated Value Range (Valuation Calculator) -->
    <div class="section" id="valuation">
        <div class="section-title"><div class="icon">&#128176;</div> What Your Business Is Worth</div>
        <div class="valuation-grid">
            <div class="val-box conservative">
                <div class="val-label">Conservative</div>
                <div class="val-amount" id="val-low">$0</div>
                <div style="font-size:12px; color:var(--text-secondary); margin-top:6px;" id="val-low-mult">${cd.multiples.low.toFixed(1)}x EBITDA</div>
            </div>
            <div class="val-box likely">
                <div class="val-label">Likely</div>
                <div class="val-amount" id="val-mid">$0</div>
                <div style="font-size:12px; color:var(--text-secondary); margin-top:6px;" id="val-mid-mult">${cd.multiples.mid.toFixed(1)}x EBITDA</div>
            </div>
            <div class="val-box optimistic">
                <div class="val-label">Optimistic</div>
                <div class="val-amount" id="val-high">$0</div>
                <div style="font-size:12px; color:var(--text-secondary); margin-top:6px;" id="val-high-mult">${cd.multiples.high.toFixed(1)}x EBITDA</div>
            </div>
        </div>
        <div class="methodology" id="methodology-text">Calculating...</div>
        ${valRange.key_drivers ? `<div style='margin-top:20px;'><h4 style="color:var(--text-heading); margin-bottom:12px;">Key Valuation Drivers</h4><ul class="drivers-list">${valRange.key_drivers.map(d => `<li>${esc(d)}</li>`).join('\n')}</ul></div>` : ''}
    </div>

    <!-- EXISTING: EBITDA Levers -->
    <div class="section" id="levers">
        <div class="section-title"><div class="icon">&#9878;</div> What Drives Your Valuation &mdash; Your Real Profit Levers</div>
        <p style="color: var(--text-secondary); font-size: 13px; margin-bottom: 20px;">These are the specific factors that push your valuation multiple up or down. Understanding them is the first step to maximizing what a buyer will pay.</p>
        <div class="levers-grid" id="levers-grid">
            <div class="levers-column positive">
                <h3>&#9650; Value Drivers (Strengths)</h3>
                ${cd.levers.positive.map(l => `
        <div class="lever-card lever-positive">
            <div class="lever-icon">&#9650;</div>
            <div>
                <div class="lever-name">${esc(l.name)}</div>
                <div class="lever-desc">${esc(l.desc)}</div>
            </div>
        </div>`).join('')}
            </div>
            <div class="levers-column opportunity">
                <h3>&#9660; Value Opportunities</h3>
                ${cd.levers.opportunity.map(l => `
        <div class="lever-card lever-opportunity">
            <div class="lever-icon">&#9660;</div>
            <div>
                <div class="lever-name">${esc(l.name)}</div>
                <div class="lever-desc">${esc(l.desc)}</div>
            </div>
        </div>`).join('')}
            </div>
        </div>
    </div>

    <!-- SECTION 6: PROCESS (4 Phases) -->
    <div class="section" id="process">
        <div class="section-title"><div class="icon">&#128197;</div> Our Process &mdash; What Happens and When</div>
        <p style="margin-bottom: 20px;">Here is exactly what happens from the day you sign the engagement letter to the day you hand over the keys. No surprises, no mystery. Every step is planned.</p>
        <div class="phase-grid">
            <div class="phase-card">
                <div class="phase-number">1</div>
                <h4>Phase 1 &mdash; Preparation</h4>
                <div class="phase-weeks">Weeks 1-6</div>
                <ul>
                    <li>Complete business valuation and financial analysis</li>
                    <li>Identify and document your real profit after we add back owner perks</li>
                    <li>Create the marketing book we build about your business</li>
                    <li>Build target buyer list (strategic, PE, independent)</li>
                    <li>Prepare management presentation materials</li>
                    <li>Set up secure data room</li>
                </ul>
            </div>
            <div class="phase-card">
                <div class="phase-number">2</div>
                <h4>Phase 2 &mdash; Marketing</h4>
                <div class="phase-weeks">Weeks 7-14</div>
                <ul>
                    <li>Send blind teaser to qualified buyers (no company name)</li>
                    <li>Execute NDAs with interested parties</li>
                    <li>Share the marketing book with signed buyers</li>
                    <li>Manage buyer Q&amp;A process</li>
                    <li>Collect initial offers (Indications of Interest)</li>
                    <li>Evaluate and rank every offer</li>
                </ul>
            </div>
            <div class="phase-card">
                <div class="phase-number">3</div>
                <h4>Phase 3 &mdash; Negotiation</h4>
                <div class="phase-weeks">Weeks 15-22</div>
                <ul>
                    <li>Facilitate in-person meetings with top bidders</li>
                    <li>Request formal Letters of Intent (LOIs)</li>
                    <li>Negotiate price, terms, structure, and transition plan</li>
                    <li>Select preferred buyer and sign LOI</li>
                    <li>Coordinate with your legal counsel on deal structure</li>
                </ul>
            </div>
            <div class="phase-card">
                <div class="phase-number">4</div>
                <h4>Phase 4 &mdash; Closing</h4>
                <div class="phase-weeks">Weeks 23-36</div>
                <ul>
                    <li>Manage the due diligence process (buyer verifying your numbers)</li>
                    <li>Coordinate with buyer's lenders and advisors</li>
                    <li>Support purchase agreement negotiation</li>
                    <li>Handle working capital and any earnout details</li>
                    <li>Close the deal and facilitate ownership transfer</li>
                </ul>
            </div>
        </div>
        <div class="methodology" style="margin-top: 16px;">
            <strong>Expected Total Timeline:</strong> 6-9 months from engagement to close. We keep you informed every step of the way with weekly updates and a dedicated point of contact.
        </div>
    </div>

    <!-- SECTION 7: BUYER UNIVERSE -->
    <div class="section" id="buyers">
        <div class="section-title"><div class="icon">&#127919;</div> Who Will Buy Your Business</div>
        <p style="margin-bottom: 20px;">We don't just put your business on a listing and hope someone calls. We build a curated list of buyers who are actively looking for exactly what you have, and we go to them directly.</p>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;">
            <div>
                <h4 style="color: var(--green); font-size: 14px; margin-bottom: 8px;">Strategic Buyers (Active in ${esc(cd.tradeLabel)})</h4>
                <ul class="drivers-list" style="font-size: 13px;">
                    ${strategicBuyersList}
                </ul>
            </div>
            <div>
                <h4 style="color: var(--accent); font-size: 14px; margin-bottom: 8px;">Buyers Backed by Investment Groups</h4>
                <ul class="drivers-list" style="font-size: 13px;">
                    ${pePlatformsList}
                </ul>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;">
            <div>
                <h4 style="color: var(--amber); font-size: 14px; margin-bottom: 8px;">Independent Buyers &amp; Search Funds</h4>
                <p style="font-size: 13px;">${cd.independentCount} active independent buyers in ${esc(cd.tradeLabel.toLowerCase())} and related services</p>
            </div>
            <div>
                <h4 style="color: var(--text-heading); font-size: 14px; margin-bottom: 8px;">Regional Buyers</h4>
                <ul class="drivers-list" style="font-size: 13px;">
                    ${regionalBuyersList}
                </ul>
            </div>
        </div>

        <h4 style="color: var(--text-heading); margin-bottom: 16px; font-size: 16px;">Our Buyer Funnel</h4>
        <div style="max-width: 600px;">
            <div class="funnel-bar">
                <div class="funnel-label">Total Universe</div>
                <div class="funnel-fill" style="width: 100%;">${cd.funnelTotal}</div>
            </div>
            <div class="funnel-bar">
                <div class="funnel-label">Outreach</div>
                <div class="funnel-fill" style="width: 65%;">${cd.funnelOutreach}</div>
            </div>
            <div class="funnel-bar">
                <div class="funnel-label">NDAs Signed</div>
                <div class="funnel-fill" style="width: 25%;">${cd.funnelNDAs}</div>
            </div>
            <div class="funnel-bar">
                <div class="funnel-label">Initial Offers</div>
                <div class="funnel-fill" style="width: 12%;">${cd.funnelIOIs}</div>
            </div>
            <div class="funnel-bar">
                <div class="funnel-label">Final Offers</div>
                <div class="funnel-fill" style="width: 5%;">${cd.funnelLOIs}</div>
            </div>
        </div>
    </div>

    <!-- SECTION 8: FEE STRUCTURE (Interactive Selection + Illustration Table) -->
    <div class="section" id="fees">
        <div class="section-title"><div class="icon">&#128178;</div> Fee Structure Options</div>
        <p style="color: var(--text-secondary); font-size: 13px; margin-bottom: 24px;">
            Click on the option that works best for you. Your selection is saved automatically. The engagement fee is credited 100% against the success fee at closing &mdash; it's not an additional cost.
        </p>
        <div class="fee-grid">
            <div class="fee-card" data-option="A" onclick="selectFee('A')">
                <div class="checkmark">&#10003;</div>
                <div class="fee-option-name">Option A</div>
                <div class="fee-option-subtitle">Performance Only</div>
                <div class="fee-detail"><div class="label">Engagement Fee</div><div class="value">$0</div></div>
                <div class="fee-detail"><div class="label">Success Fee</div><div class="value">10%</div></div>
                <div class="fee-tagline">"You pay nothing until we deliver"</div>
            </div>
            <div class="fee-card popular" data-option="B" onclick="selectFee('B')">
                <div class="checkmark">&#10003;</div>
                <div class="fee-option-name">Option B</div>
                <div class="fee-option-subtitle">Standard</div>
                <div class="fee-detail"><div class="label">Engagement Fee</div><div class="value">$${(engagementFee || 10000).toLocaleString()}</div></div>
                <div class="fee-detail"><div class="label">Success Fee</div><div class="value">${successFeePct || 7}%</div></div>
                <div class="fee-tagline">"Most popular &mdash; covers research and marketing costs"</div>
            </div>
            <div class="fee-card" data-option="C" onclick="selectFee('C')">
                <div class="checkmark">&#10003;</div>
                <div class="fee-option-name">Option C</div>
                <div class="fee-option-subtitle">Premium</div>
                <div class="fee-detail"><div class="label">Engagement Fee</div><div class="value">$${Math.round((engagementFee || 10000) * 1.5).toLocaleString()}</div></div>
                <div class="fee-detail"><div class="label">Success Fee</div><div class="value">${Math.max(3, (successFeePct || 7) - 2)}%</div></div>
                <div class="fee-tagline">"Full white-glove service with dedicated deal team"</div>
            </div>
        </div>

        <div class="fee-illustration">
            <h4>Fee Illustration &mdash; What You'd Actually Pay</h4>
            <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 12px;">Engagement fee credited 100% against the success fee. These numbers show the total cost at different sale prices.</p>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Sale Price</th>
                        <th>Success Fee</th>
                        <th>Engagement Fee Credit</th>
                        <th>Effective Rate</th>
                    </tr>
                </thead>
                <tbody>${feeRows}
                </tbody>
            </table>
            <div class="fee-note">The engagement fee proves you're serious about selling. The success fee proves we're serious about getting you the best price. Both are aligned.</div>
        </div>
    </div>

    <!-- EXISTING: Attack Plan / How We Would Sell -->
    <div class="section" id="attack">
        <div class="section-title"><div class="icon">&#128640;</div> How We Would Sell Your Business</div>
        <p>${esc(attackPlan)}</p>
    </div>

    <!-- SECTION 10: NEXT STEPS -->
    <div class="section" id="next-steps">
        <div class="section-title"><div class="icon">&#9989;</div> Next Steps</div>
        <div class="next-step-box">
            <h3>One Decision. One Deadline.</h3>
            <div class="step-action">Sign the engagement letter and return it with the engagement fee by ${esc(cd.nextStepDate)}.</div>
            <div class="step-date">We begin Phase 1 on ${esc(cd.phase1Date)}.</div>
            <div style="margin-top: 20px; font-size: 14px; color: var(--text-secondary);">
                Upon signing, we start immediately. No waiting. Your dedicated deal team is assigned on day one.
            </div>
        </div>
    </div>

    <!-- EXISTING: Let's Get Started CTA -->
    <div class="section">
        <div class="cta-section">
            <button class="cta-btn" id="cta-button" onclick="letsGetStarted()">Let's Get Started &#10132;</button>
        </div>
        <div class="confirmation" id="confirmation">
            <h3>&#10003; Thank You!</h3>
            <p>Look for an email in the next 24 hours with your engagement letter and next steps.</p>
            <p style="margin-top: 12px; font-size: 14px; color: var(--text-secondary);">
                Your selected fee structure and business profile have been saved. We'll use these as the starting point for our conversation.
            </p>
        </div>
    </div>

    <div style="text-align:center; padding: 32px 0; color: var(--text-secondary); font-size: 12px;">
        <p>This proposal is confidential and intended solely for ${esc(ownerName)}.</p>
        <p style="margin-top:4px;">&copy; 2026 Next Chapter M&amp;A Advisory. All rights reserved.</p>
    </div>
</div>

<script>
const SUPABASE_URL = '${SUPABASE_URL}';
const SUPABASE_KEY = '${ANON_KEY}';
const COMPANY_NAME = '${companyName.replace(/'/g, "\\'")}';
const BASE_MULTIPLES = { low: ${cd.multiples.low}, mid: ${cd.multiples.mid}, high: ${cd.multiples.high} };
const BASE_EBITDA_MARGIN = ${cd.ebitdaMargin};

async function logInteraction(type, fieldName, oldVal, newVal, metadata) {
    try {
        await fetch(SUPABASE_URL + '/rest/v1/client_interactions', {
            method: 'POST',
            headers: {
                'apikey': SUPABASE_KEY,
                'Authorization': 'Bearer ' + SUPABASE_KEY,
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            },
            body: JSON.stringify({
                company_name: COMPANY_NAME,
                interaction_type: type,
                field_name: fieldName,
                old_value: oldVal != null ? String(oldVal) : null,
                new_value: newVal != null ? String(newVal) : null,
                metadata: metadata || null
            })
        });
    } catch (e) { console.warn('Failed to log interaction:', e); }
}

logInteraction('page_view', null, null, null, {
    user_agent: navigator.userAgent,
    referrer: document.referrer,
    timestamp: new Date().toISOString()
});

const sliders = {
    revenue: { slider: 'revenue-slider', input: 'revenue-input', display: 'revenue-display', format: 'currency' },
    employees: { slider: 'employees-slider', input: 'employees-input', display: 'employees-display', format: 'number' },
    commercial: { slider: 'commercial-slider', input: 'commercial-input', display: 'split-display', format: 'split' },
    recurring: { slider: 'recurring-slider', input: 'recurring-input', display: 'recurring-display', format: 'percent' },
    years: { slider: 'years-slider', input: 'years-input', display: 'years-display', format: 'number' }
};

let debounceTimers = {};

function formatCurrency(val) {
    if (val >= 1000000) return '$' + (val / 1000000).toFixed(1) + 'M';
    if (val >= 1000) return '$' + (val / 1000).toFixed(0) + 'K';
    return '$' + val.toLocaleString();
}

function formatVal(val) {
    if (val >= 1000000) return '$' + (val / 1000000).toFixed(2) + 'M';
    if (val >= 1000) return '$' + Math.round(val / 1000).toLocaleString() + 'K';
    return '$' + val.toLocaleString();
}

function updateDisplay(key) {
    const cfg = sliders[key];
    const val = parseInt(document.getElementById(cfg.slider).value);
    if (cfg.format === 'currency') {
        document.getElementById(cfg.display).textContent = formatCurrency(val);
    } else if (cfg.format === 'percent') {
        document.getElementById(cfg.display).textContent = val + '%';
    } else if (cfg.format === 'split') {
        document.getElementById(cfg.display).textContent = val + '% / ' + (100 - val) + '%';
        document.getElementById('commercial-pct').textContent = val + '%';
        document.getElementById('residential-pct').textContent = (100 - val) + '%';
    } else {
        document.getElementById(cfg.display).textContent = val;
    }
}

function syncSliderAndInput(key, source) {
    const cfg = sliders[key];
    const sliderEl = document.getElementById(cfg.slider);
    const inputEl = document.getElementById(cfg.input);
    if (source === 'slider') { inputEl.value = sliderEl.value; }
    else { sliderEl.value = inputEl.value; }
    updateDisplay(key);
    recalculateValuation();
}

Object.keys(sliders).forEach(key => {
    const cfg = sliders[key];
    const sliderEl = document.getElementById(cfg.slider);
    const inputEl = document.getElementById(cfg.input);
    sliderEl.addEventListener('input', () => {
        const oldVal = inputEl.value;
        syncSliderAndInput(key, 'slider');
        clearTimeout(debounceTimers[key]);
        debounceTimers[key] = setTimeout(() => {
            logInteraction('slider_change', key, oldVal, sliderEl.value, null);
        }, 1000);
    });
    inputEl.addEventListener('input', () => {
        const oldVal = sliderEl.value;
        syncSliderAndInput(key, 'input');
        clearTimeout(debounceTimers[key]);
        debounceTimers[key] = setTimeout(() => {
            logInteraction('slider_change', key, oldVal, inputEl.value, null);
        }, 1000);
    });
});

function recalculateValuation() {
    const revenue = parseInt(document.getElementById('revenue-slider').value);
    const recurring = parseInt(document.getElementById('recurring-slider').value);
    const commercial = parseInt(document.getElementById('commercial-slider').value);
    const years = parseInt(document.getElementById('years-slider').value);
    const employees = parseInt(document.getElementById('employees-slider').value);

    let margin = BASE_EBITDA_MARGIN;
    margin += (commercial - 50) * 0.0005;
    margin += (recurring - 20) * 0.001;
    margin = Math.max(0.08, Math.min(0.30, margin));

    const ebitda = revenue * margin;

    let multipleAdj = 0;
    if (recurring >= 60) multipleAdj += 1.0;
    else if (recurring >= 40) multipleAdj += 0.5;
    else if (recurring >= 20) multipleAdj += 0.0;
    else multipleAdj -= 0.5;

    if (commercial >= 60) multipleAdj += 0.3;
    if (years >= 30) multipleAdj += 0.3;
    else if (years >= 15) multipleAdj += 0.15;
    if (revenue >= 10000000) multipleAdj += 0.5;
    else if (revenue >= 5000000) multipleAdj += 0.25;

    const adjLow = Math.max(1.5, BASE_MULTIPLES.low + multipleAdj * 0.5);
    const adjMid = Math.max(2.0, BASE_MULTIPLES.mid + multipleAdj * 0.7);
    const adjHigh = Math.max(3.0, BASE_MULTIPLES.high + multipleAdj);

    const valLow = ebitda * adjLow;
    const valMid = ebitda * adjMid;
    const valHigh = ebitda * adjHigh;

    document.getElementById('val-low').textContent = formatVal(valLow);
    document.getElementById('val-mid').textContent = formatVal(valMid);
    document.getElementById('val-high').textContent = formatVal(valHigh);
    document.getElementById('val-low-mult').textContent = adjLow.toFixed(1) + 'x EBITDA';
    document.getElementById('val-mid-mult').textContent = adjMid.toFixed(1) + 'x EBITDA';
    document.getElementById('val-high-mult').textContent = adjHigh.toFixed(1) + 'x EBITDA';

    document.getElementById('methodology-text').innerHTML =
        '<strong>How we got these numbers:</strong> Based on <strong>' + formatCurrency(revenue) + '</strong> revenue x ' +
        '<strong>' + (margin * 100).toFixed(1) + '%</strong> estimated profit margin = ' +
        '<strong>' + formatCurrency(ebitda) + '</strong> (your real profit) x ' +
        '<strong>' + adjLow.toFixed(1) + 'x - ' + adjHigh.toFixed(1) + 'x</strong> multiple range. ' +
        'Multiple adjustments reflect ' + recurring + '% recurring revenue, ' + commercial + '% commercial mix, ' +
        years + ' years operating history, and ' + employees + ' employees. ' +
        'Higher recurring revenue and commercial contracts command premium multiples from buyers.';
}

recalculateValuation();

let selectedFee = null;

function selectFee(option) {
    const oldSelection = selectedFee;
    selectedFee = option;
    document.querySelectorAll('.fee-card').forEach(card => { card.classList.remove('selected'); });
    document.querySelector('.fee-card[data-option="' + option + '"]').classList.add('selected');
    document.getElementById('cta-button').classList.add('visible');
    logInteraction('fee_selection', 'fee_option', oldSelection, option, {
        option_details: {
            'A': { engagement_fee: 0, success_fee: '10%', name: 'Performance Only' },
            'B': { engagement_fee: ${engagementFee || 10000}, success_fee: '${successFeePct || 7}%', name: 'Standard' },
            'C': { engagement_fee: ${Math.round((engagementFee || 10000) * 1.5)}, success_fee: '${Math.max(3, (successFeePct || 7) - 2)}%', name: 'Premium' }
        }[option]
    });
}

function letsGetStarted() {
    if (!selectedFee) return;
    const state = {
        revenue: document.getElementById('revenue-slider').value,
        employees: document.getElementById('employees-slider').value,
        commercial_pct: document.getElementById('commercial-slider').value,
        recurring_pct: document.getElementById('recurring-slider').value,
        years: document.getElementById('years-slider').value,
        fee_option: selectedFee,
        valuation_low: document.getElementById('val-low').textContent,
        valuation_mid: document.getElementById('val-mid').textContent,
        valuation_high: document.getElementById('val-high').textContent
    };
    logInteraction('lets_get_started', 'fee_option_chosen', null, selectedFee, state);
    document.getElementById('cta-button').style.display = 'none';
    document.getElementById('confirmation').classList.add('show');
    document.getElementById('confirmation').scrollIntoView({ behavior: 'smooth', block: 'center' });
}
</script>
</body>
</html>`;
}

async function main() {
  console.log('Fetching proposals from Supabase...');

  const proposals = await supabaseGet('proposals?select=*&company_name=in.(AquaScience,Air%20Control,Springer%20Floor,HR.com%20Ltd)');
  const buyers = await supabaseGet('engagement_buyers?select=entity,buyer_company_name,buyer_type,buyer_city,buyer_state,fit_score');

  console.log(`Found ${proposals.length} proposals and ${buyers.length} buyers`);

  const outputPaths = [
    '/Users/clawdbot/Projects/master-crm/data/proposals',
    '/Users/clawdbot/Projects/master-crm-web/public',
    '/Users/clawdbot/Downloads/master-crm-proposals'
  ];

  let log = `=== Proposal Template Rebuild Log ===\nTimestamp: ${new Date().toISOString()}\nTemplate: PROPOSAL-TEMPLATE-V1 (10-section)\n\n`;

  for (const proposal of proposals) {
    const cd = COMPANY_DATA[proposal.company_name];
    if (!cd) {
      console.log(`Skipping ${proposal.company_name} - no company data configured`);
      continue;
    }

    console.log(`Generating ${proposal.company_name}...`);
    const html = generateProposal(proposal, cd, buyers);
    const filename = `interactive-${cd.slug}.html`;

    for (const dir of outputPaths) {
      const filepath = path.join(dir, filename);
      try {
        fs.writeFileSync(filepath, html, 'utf-8');
        console.log(`  Written: ${filepath}`);
        log += `Written: ${filepath} (${html.length} bytes)\n`;
      } catch(e) {
        console.error(`  FAILED: ${filepath} - ${e.message}`);
        log += `FAILED: ${filepath} - ${e.message}\n`;
      }
    }

    log += `\nSections for ${proposal.company_name}:\n`;
    log += `  1. Cover Page Header - firm name, tagline, engagement type, date\n`;
    log += `  2. Executive Summary - personalized opening, valuation range\n`;
    log += `  3. Market Overview - multiples, buyers, deals, comparables, Why Now\n`;
    log += `  4. Company Snapshot - snapshot grid with all fields\n`;
    log += `  5. Company Story (existing) - full narrative preserved\n`;
    log += `  5b. Top 3 Strengths (existing) - preserved\n`;
    log += `  5c. Interactive Sliders (existing) - preserved\n`;
    log += `  5d. Valuation Calculator (existing) - preserved\n`;
    log += `  5e. EBITDA Levers (existing) - preserved\n`;
    log += `  6. Process - 4 phases with week timelines, checklist format\n`;
    log += `  7. Buyer Universe - strategic, PE, independent, regional + funnel\n`;
    log += `  8. Fee Structure (existing) - preserved + fee illustration table added\n`;
    log += `  9. Attack Plan (existing) - preserved\n`;
    log += `  10. Next Steps - one clear CTA with date\n`;
    log += `  Supabase logging: preserved\n`;
    log += `  Let's Get Started CTA: preserved\n\n`;
  }

  log += `\nTotal proposals rebuilt: ${proposals.length}\n`;
  log += `Template version: V1\n`;
  log += `Completed: ${new Date().toISOString()}\n`;

  const logPath = '/Users/clawdbot/Projects/dossier-pipeline/data/audit-logs/proposal_template_rebuild.log';
  fs.writeFileSync(logPath, log, 'utf-8');
  console.log(`\nAudit log written: ${logPath}`);
  console.log('Done!');
}

main().catch(e => { console.error('FATAL:', e); process.exit(1); });
