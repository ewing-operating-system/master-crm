#!/usr/bin/env node
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '/Users/clawdbot/.openclaw/workspace/.env' });

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('Missing Supabase credentials');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function classifyRemaining() {
  console.log('Classifying remaining unclassified targets...');
  
  // Get count of unclassified targets
  const { data: targets, error } = await supabase
    .from('targets')
    .select('id, company_name, vertical, notes')
    .or('notes.not.ilike.%ENTITY:%,notes.not.ilike.%Entity=%')
    .limit(100);
    
  if (error) {
    console.error('Error:', error);
    return;
  }
  
  console.log(`Found ${targets.length} unclassified targets`);
  
  if (targets.length === 0) {
    console.log('✅ All targets are classified!');
    return;
  }
  
  console.log('Starting classification...');
  // Simple classification logic
  for (const target of targets) {
    const vertical = target.vertical?.toLowerCase() || '';
    let entity = 'unknown';
    
    if (vertical.includes('hvac') || vertical.includes('plumbing') || 
        vertical.includes('pest') || vertical.includes('construction')) {
      entity = 'next_chapter';
    } else if (vertical.includes('electrical')) {
      entity = 'and_capital';
    }
    
    const newNotes = `${target.notes || ''}\nCLASSIFIED ${new Date().toISOString().split('T')[0]}: Entity=${entity}`;
    
    await supabase
      .from('targets')
      .update({ notes: newNotes, updated_at: new Date().toISOString() })
      .eq('id', target.id);
      
    console.log(`✓ ${target.company_name}: ${entity}`);
  }
  
  console.log('✅ Classification complete');
}

classifyRemaining().catch(console.error);
