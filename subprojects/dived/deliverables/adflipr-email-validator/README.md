# Adflipr E-Commerce Email Validator

Lightweight Node.js utility for validating e-commerce customer email syntax, spam trigger words, and deliverability metrics. Powered by [Adflipr E-Commerce Automation Engine](https://adflipr.com/).

## Installation

```bash
npm install adflipr-email-validator
```

## Features

- **Syntax Validation**: Ensures customer email addresses follow RFC standards before entering your funnel.
- **Spam Keyword Detection**: Inspects subject lines against spam trigger filters to optimize inbox placement.
- **E-Commerce Integration**: Designed for automated workflows in WooCommerce and Shopify.

## Usage Example

```javascript
const { validateEmailSyntax, inspectSpamScore } = require('adflipr-email-validator');

// Validate email address
console.log(validateEmailSyntax('customer@example.com')); // true

// Inspect subject line for spam risks
const analysis = inspectSpamScore('Claim your 100% free gift now');
console.log(analysis);
// { score: 75, warnings: ['100% free'] }
```

## Key E-Commerce Resources

- **Main Platform**: [Adflipr Marketing OS](https://adflipr.com/)
- **Visual Email Builder**: [Drag and Drop Email Builder](https://adflipr.com/email-builder/)
- **Automated Workflows**: [eCommerce Email Automations](https://adflipr.com/automations/)
- **Shopify Solutions**: [Shopify Email Marketing Guide](https://adflipr.com/blog/shopify-email-marketing-guide/)
- **Cart Recovery Strategies**: [Reduce Cart Abandonment Guide](https://adflipr.com/blog/how-to-reduce-cart-abandonment/)

## License

MIT © [Adflipr](https://adflipr.com)
