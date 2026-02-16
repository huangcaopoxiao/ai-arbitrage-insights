#!/usr/bin/env node
/**
 * GPU Price Monitor - 曹皇显卡价格监控器 👑
 * Targets: RTX 4090 / 4080 / 4070 Ti Super
 * Alert threshold: >= 5% price drop
 */

const fs = require('fs');
const path = require('path');

const DB_PATH = path.join(__dirname, 'price_db.json');
const TARGET_GPUS = [
  { model: 'RTX 4090', targetPrice: 1599, retailers: ['bestbuy', 'newegg', 'amazon'] },
  { model: 'RTX 4080', targetPrice: 1199, retailers: ['bestbuy', 'newegg', 'amazon'] },
  { model: 'RTX 4070 Ti Super', targetPrice: 799, retailers: ['bestbuy', 'newegg', 'amazon'] }
];

// Simulated current prices (real implementation would scrape retailers)
// In production, these come from web scraping
const CURRENT_PRICES = {
  'RTX 4090': [
    { retailer: 'Best Buy', price: 1799.99, url: 'https://www.bestbuy.com/site/nvidia-rtx-4090' },
    { retailer: 'Newegg', price: 1759.99, url: 'https://www.newegg.com/pny-rtx-4090' },
    { retailer: 'Amazon', price: 1839.99, url: 'https://amazon.com/dp/B0BHJF2RH2' }
  ],
  'RTX 4080': [
    { retailer: 'Best Buy', price: 1099.99, url: 'https://www.bestbuy.com/site/nvidia-rtx-4080' },
    { retailer: 'Newegg', price: 1059.99, url: 'https://www.newegg.com/msi-rtx-4080' },
    { retailer: 'Amazon', price: 1129.99, url: 'https://amazon.com/dp/B0BHHNV7K2' }
  ],
  'RTX 4070 Ti Super': [
    { retailer: 'Best Buy', price: 799.99, url: 'https://www.bestbuy.com/site/nvidia-rtx-4070-ti-super' },
    { retailer: 'Newegg', price: 769.99, url: 'https://www.newegg.com/asus-rtx-4070-ti-super' },
    { retailer: 'Amazon', price: 789.99, url: 'https://amazon.com/dp/B0CQGNSP8P' }
  ]
};

function loadDatabase() {
  try {
    if (fs.existsSync(DB_PATH)) {
      return JSON.parse(fs.readFileSync(DB_PATH, 'utf8'));
    }
  } catch (e) {
    console.error('Error loading DB:', e.message);
  }
  return { lastUpdate: null, prices: {}, alerts: [] };
}

function saveDatabase(db) {
  fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2));
}

function calculateDropPercent(oldPrice, newPrice) {
  return ((oldPrice - newPrice) / oldPrice * 100).toFixed(1);
}

function generateAlerts(currentPrices, db) {
  const alerts = [];
  const timestamp = new Date().toISOString();
  
  for (const [model, retailers] of Object.entries(currentPrices)) {
    const previousPrices = db.prices[model] || [];
    
    for (const current of retailers) {
      const previous = previousPrices.find(p => p.retailer === current.retailer);
      
      if (previous && current.price < previous.price) {
        const dropPercent = calculateDropPercent(previous.price, current.price);
        
        if (parseFloat(dropPercent) >= 5) {
          alerts.push({
            timestamp,
            model,
            retailer: current.retailer,
            oldPrice: previous.price,
            newPrice: current.price,
            dropPercent: parseFloat(dropPercent),
            url: current.url,
            severity: parseFloat(dropPercent) >= 10 ? '🔥 HIGH' : '⚡ NORMAL'
          });
        }
      }
    }
  }
  
  return alerts;
}

function formatTelegramMessage(alerts) {
  if (alerts.length === 0) return null;
  
  const lines = [
    '👑 曹皇显卡价格监控 - 降价警报',
    '═══════════════════════════',
    ''
  ];
  
  for (const alert of alerts) {
    lines.push(`${alert.severity} ${alert.model}`);
    lines.push(`📉 降价: $${alert.oldPrice} → $${alert.newPrice} (-${alert.dropPercent}%)`);
    lines.push(`🏪 商家: ${alert.retailer}`);
    lines.push(`🔗 ${alert.url}`);
    lines.push('');
  }
  
  lines.push(`⏰ ${new Date().toLocaleString('zh-CN', { timeZone: 'America/Toronto' })}`);
  lines.push('💰 早买早享受，晚买有折扣');
  
  return lines.join('\n');
}

async function main() {
  console.log('👑 曹皇显卡价格监控启动...');
  console.log(`⏰ ${new Date().toLocaleString('zh-CN', { timeZone: 'America/Toronto' })}`);
  
  const db = loadDatabase();
  const alerts = generateAlerts(CURRENT_PRICES, db);
  
  // Update database with current prices
  db.lastUpdate = new Date().toISOString();
  db.prices = CURRENT_PRICES;
  
  if (alerts.length > 0) {
    db.alerts = [...(db.alerts || []), ...alerts];
    console.log(`\n🚨 发现 ${alerts.length} 个降价信号!`);
    
    const message = formatTelegramMessage(alerts);
    console.log('\n📨 Telegram 消息:');
    console.log(message);
    
    // Output for cron to pick up
    if (process.env.OUTPUT_MODE === 'telegram') {
      console.log('\n---TELEGRAM_MESSAGE---');
      console.log(message);
    }
  } else {
    console.log('\n✅ 无显著降价 (>5%)');
    
    // Show current lowest prices
    console.log('\n📊 当前最低价格:');
    for (const [model, retailers] of Object.entries(CURRENT_PRICES)) {
      const lowest = retailers.reduce((min, r) => r.price < min.price ? r : min);
      console.log(`  ${model}: $${lowest.price} @ ${lowest.retailer}`);
    }
  }
  
  saveDatabase(db);
  
  // Return summary for cron
  return {
    checked: Object.keys(CURRENT_PRICES).length,
    alerts: alerts.length,
    details: alerts
  };
}

main().then(result => {
  console.log('\n📈 监控完成');
  process.exit(0);
}).catch(err => {
  console.error('❌ 监控失败:', err);
  process.exit(1);
});
