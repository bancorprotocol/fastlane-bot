# Fastlane Bot FAQ

### **1. Default Target Tokens in the Fastlane Bot**
- **Question:** Are the tokens listed in the log the default target tokens for the Fastlane Bot?
- **Answer:** The listed tokens are the default. However, the flashloan tokens can be limited to those currently supported on Bancor3.

### **2. Fastlane Bot as a Web Application**
- **Question:** Can the Fastlane Bot operate as a web application?
- **Answer:** The Fastlane Bot is not designed as a web app. It functions as a backend framework for identifying and executing arbitrage trades using the Fast Lane smart contract on the blockchain.

### **3. Taxation Handling in the Fastlane Bot**
- **Question:** What is the approach of the Fastlane Bot in handling taxation on tokens?
- **Answer:** Tax tokens typically include a whitelist in their contract, allowing the whitelisting of smart contracts (like DEXs) to circumvent tax when used with specified DEXs.

### **4. Addressing 'Gas Required Exceeds Allowance' Error in the Fastlane Bot**
- **Question:** What steps should be taken if the bot displays a 'gas required exceeds allowance' error during transaction building?
- **Answer:** It is essential to ensure sufficient ETH in the wallet and to run the bot on its latest version with appropriate settings.

### **5. RPC Configuration to Infura in the Fastlane Bot**
- **Question:** Is switching the RPC in the Fastlane Bot to Infura feasible?
- **Answer:** Switching to Infura is possible by modifying the RPC endpoint in the configuration to an Infura endpoint. Replacing Alchemy in certain code sections, such as transaction helpers, may require additional adjustments.

### **6. Using a Private Node with the Fastlane Bot**
- **Question:** What considerations exist when using a private node with the Fastlane Bot?
- **Answer:** Running a private RPC node is achievable, but an Alchemy API key is necessary for specific functions like access list creation, priority fee setting, and private transaction submission.

### **7. Identifying and Executing Arbitrage Opportunities with the Fastlane Bot**
- **Question:** How does the Fastlane Bot identify and execute arbitrage opportunities?
- **Answer:** The bot searches for arbitrage opportunities between different DEXs, requiring a tradable token pair on two distinct DEXs and the detection of actual arbitrage opportunities between them.
