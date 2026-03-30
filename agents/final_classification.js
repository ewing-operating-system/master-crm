const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '/Users/clawdbot/.openclaw/workspace/.env' });

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('Missing Supabase credentials in .env file');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function finalClassification() {
  const targetId = '497c29bb-4c6a-516e-83ed-4ae10bf5627b';
  const targetName = 'Canyon State Enterprises LLC.';
  const queueItemId = '46ce0c37-e346-4c84-8d02-37460ac553a3';

  console.log('Final classification task');
  console.log(`Target: ${targetName}`);
  console.log(`Target ID: ${targetId}`);
  console.log(`Queue Item ID: ${queueItemId}`);

  try {
    // 1. Load target data
    console.log('\n1. Loading target data...');
    const { data: target, error: targetError } = await supabase
      .from('targets')
      .select('*')
      .eq('id', targetId)
      .single();

    if (targetError) {
      console.error('Error loading target:', targetError);
      throw targetError;
    }

    console.log('✅ Target loaded');
    console.log(`Company: ${target.company_name}`);
    console.log(`Vertical: ${target.vertical}`);
    console.log(`Pipeline Status: ${target.pipeline_status}`);

    // 2. Determine classification
    console.log('\n2. Determining classification...');
    
    // Based on analysis:
    // - Company: Canyon State Enterprises LLC.
    // - Vertical: construction
    // - Services: multi-trade construction (roofing, HVAC, plumbing, concrete, etc.)
    // - No explicit hiring, transaction, or capital intent found
    // - "No acquisitions" in research is negative context, not actual intent
    // - Company-type fallback: trades/home services → Next Chapter
    
    // Final classification decision:
    const classification = {
      entity: 'next_chapter',
      entity_sub_type: 'trades',
      classification_confidence: 1.0,
      classification_reason: 'Trades/home services company (construction vertical) - company-type fallback per Entity Classification Guide',
      classification_method: 'deterministic_decision_tree_manual_review'
    };
    
    console.log('✅ Classification determined:');
    console.log(JSON.stringify(classification, null, 2));

    // 3. Update target (add classification to notes since entity fields don't exist)
    console.log('\n3. Updating target...');
    
    const currentNotes = target.notes || '';
    const newNotes = `CLASSIFIED ${new Date().toISOString().split('T')[0]}: Entity=${classification.entity}, Sub-type=${classification.entity_sub_type}, Confidence=${classification.classification_confidence}, Reason=${classification.classification_reason}. ${currentNotes}`;
    
    const { data: updatedTarget, error: updateError } = await supabase
      .from('targets')
      .update({
        notes: newNotes,
        updated_at: new Date().toISOString()
      })
      .eq('id', targetId)
      .select()
      .single();

    if (updateError) {
      console.error('Error updating target:', updateError);
      throw updateError;
    }

    console.log('✅ Target updated (added classification to notes)');

    // 4. Handle queue item
    console.log('\n4. Handling queue item...');
    
    // First, check if queue item exists in any table
    // Try dialer_queue first (we know it exists)
    const { data: queueItem, error: queueError } = await supabase
      .from('dialer_queue')
      .select('*')
      .eq('id', queueItemId)
      .maybeSingle();
    
    if (queueError) {
      console.error('Error checking dialer_queue:', queueError);
    }
    
    if (queueItem) {
      console.log('✅ Found queue item in dialer_queue');
      
      // Update status to done
      const { data: updatedQueue, error: updateQueueError } = await supabase
        .from('dialer_queue')
        .update({
          status: 'done',
          updated_at: new Date().toISOString()
        })
        .eq('id', queueItemId)
        .select()
        .single();
        
      if (updateQueueError) {
        console.error('Error updating queue item:', updateQueueError);
      } else {
        console.log('✅ Queue item marked as done in dialer_queue');
      }
    } else {
      console.log('⚠️ Queue item not found in dialer_queue');
      
      // Check if there's a classifier-specific queue table
      // For now, we'll just log that we couldn't find it
      console.log('Note: Queue item handling skipped (table not found)');
    }

    // 5. Log to pipeline_log
    console.log('\n5. Logging to pipeline_log...');
    
    const logDetails = {
      classification: classification,
      target_name: targetName,
      target_vertical: target.vertical,
      queue_item_id: queueItemId,
      queue_item_found: !!queueItem,
      classification_notes: 'Manual review: "No acquisitions" in research is negative context, not actual intent. Classified as trades company (Next Chapter) per company-type fallback.',
      timestamp: new Date().toISOString()
    };
    
    const { data: logEntry, error: logError } = await supabase
      .from('pipeline_log')
      .insert({
        agent: 'classifier',
        action: 'classification',
        target_id: targetId,
        details: logDetails,
        created_at: new Date().toISOString()
      })
      .select()
      .single();

    if (logError) {
      console.error('Error logging to pipeline_log:', logError);
      throw logError;
    }

    console.log('✅ Logged to pipeline_log');

    console.log('\n🎉 FINAL CLASSIFICATION COMPLETED SUCCESSFULLY!');
    console.log(`\nSummary for "${targetName}":`);
    console.log(`- Entity: ${classification.entity} (Next Chapter M&A Advisory)`);
    console.log(`- Sub-type: ${classification.entity_sub_type} (trades/home services)`);
    console.log(`- Confidence: ${classification.classification_confidence}/2.0`);
    console.log(`- Reason: ${classification.classification_reason}`);
    console.log(`- Target updated: ✓ (notes field)`);
    console.log(`- Queue item handled: ${queueItem ? '✓ (marked as done)' : '⚠ (not found)'}`);
    console.log(`- Pipeline log: ✓`);

    return {
      success: true,
      classification,
      targetUpdated: true,
      queueItemHandled: !!queueItem,
      logged: true
    };

  } catch (error) {
    console.error('Error in final classification:', error);
    
    // Try to log the error
    try {
      await supabase
        .from('pipeline_log')
        .insert({
          agent: 'classifier',
          action: 'classification_error',
          target_id: targetId,
          details: {
            error: error.message,
            timestamp: new Date().toISOString()
          },
          created_at: new Date().toISOString()
        });
    } catch (logError) {
      console.error('Failed to log error:', logError);
    }
    
    throw error;
  }
}

// Run the final classification
finalClassification()
  .then(result => {
    console.log('\nTask completed successfully');
    process.exit(0);
  })
  .catch(error => {
    console.error('\nTask failed:', error);
    process.exit(1);
  });