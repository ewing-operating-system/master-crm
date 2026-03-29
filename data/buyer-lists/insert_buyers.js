const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

const connStr = 'postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:5432/postgres';

const FILES = [
  { file: 'aquascience_buyers.json', search: ['aquascience', 'aqua science'] },
  { file: 'hrcom_buyers.json', search: ['hr.com', 'hrcom'] },
  { file: 'springer_buyers.json', search: ['springer'] },
  { file: 'aircontrol_buyers.json', search: ['air control'] },
  { file: 'weiser_buyers.json', search: ['wieser', 'weiser'] },
  { file: 'designprecast_buyers.json', search: ['design precast'] },
];

async function main() {
  const client = new Client({ connectionString: connStr, ssl: false });
  await client.connect();
  console.log('Connected to Supabase');

  // Table columns: id, proposal_id, target_id, entity, buyer_company_name, buyer_contact_name,
  // buyer_title, buyer_email, buyer_phone, buyer_linkedin, buyer_type, buyer_city, buyer_state,
  // fit_score, fit_narrative, approach_strategy, approach_script, letter_sent_at, email_sent_at,
  // called_at, linkedin_sent_at, response, response_date, meeting_scheduled, dnc_checked_at,
  // dnc_clear, status, created_at, extra_fields

  // Get proposals
  const proposals = await client.query('SELECT id, company_name FROM proposals');
  console.log(`Found ${proposals.rows.length} proposals`);
  const proposalMap = {};
  for (const row of proposals.rows) {
    proposalMap[row.company_name.toLowerCase()] = row.id;
  }

  let totalInserted = 0;

  for (const entry of FILES) {
    const filePath = path.join(__dirname, entry.file);
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const companyName = data.company;

    // Find proposal_id
    let proposalId = null;
    for (const searchTerm of entry.search) {
      for (const [name, id] of Object.entries(proposalMap)) {
        if (name.includes(searchTerm)) {
          proposalId = id;
          break;
        }
      }
      if (proposalId) break;
    }

    console.log(`\n--- ${companyName} (proposal_id: ${proposalId || 'NULL'}) ---`);

    for (const buyer of data.buyers) {
      try {
        await client.query(`
          INSERT INTO engagement_buyers
            (proposal_id, entity, buyer_company_name, buyer_contact_name, buyer_title,
             buyer_type, buyer_city, buyer_state, fit_score, fit_narrative,
             approach_strategy, status)
          VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        `, [
          proposalId,
          companyName,
          buyer.buyer_name,
          buyer.contact_name || null,
          buyer.contact_title || null,
          buyer.buyer_type,
          buyer.city,
          buyer.state,
          buyer.fit_score,
          buyer.thesis,
          'We represent owners exploring strategic options. Frame as representing buyers interested in companies like theirs — never indicate the company is for sale.',
          'new'
        ]);
        totalInserted++;
        console.log(`  + ${buyer.buyer_name} (fit: ${buyer.fit_score})`);
      } catch (err) {
        console.error(`  ERROR inserting ${buyer.buyer_name}: ${err.message}`);
      }
    }
  }

  console.log(`\n=== DONE: ${totalInserted} buyers inserted across 6 companies ===`);
  await client.end();
}

main().catch(err => {
  console.error('Fatal error:', err.message);
  process.exit(1);
});
