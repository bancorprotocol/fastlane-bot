# Fastlane Bot FAQ

### **1. Identifying and Executing Arbitrage Opportunities with the Fastlane Bot**
- **Question:** How does the Fastlane Bot identify and execute arbitrage opportunities?
- **Answer:** The bot searches for arbitrage opportunities between DEXes. When it finds an opportunity, the bot submits a transaction to the Fast Lane contract, which takes a flashloan and subsequently executes trades that close the arbitrage opportunity.

### **2. Using a Private Node or Infura with the Fastlane Bot**
- **Question:** Can a private node or Infura be used with the Fastlane Bot?
- **Answer:** Yes. The bot can use any RPC. This can be edited in the fastlane_bot/config/providers file - search for: self.RPC_URL. Note that some functions require an Alchemy API key, making it necessary unless the functions themselves are modified. These functions are in fastlane_bot/helpers/txhelpers, and include get_access_list, submit_private_transaction, and get_max_priority_fee_per_gas_alchemy.

### **3. Arbitraging Specific Tokens using the Fastlane Bot**
- **Question:** How can I search for arbitrage for specific tokens using the Fastlane Bot?
- **Answer:** The bot includes two Click Options - flashloan_tokens & target_tokens - that enable searching only pools that include specific tokens. 

### **4. Tax Token Handling in the Fastlane Bot**
- **Question:** Can the bot trade tax tokens?
- **Answer:** No. The bot currently does not support tax tokens.

### **5. Fastlane Bot as a Web Application**
- **Question:** Can the Fastlane Bot operate as a web application?
- **Answer:** The Fastlane Bot is not designed as a web app. It functions as a backend framework for identifying and executing arbitrage trades using the Fast Lane smart contract on the blockchain.

### **6. Addressing 'Gas Required Exceeds Allowance' Error in the Fastlane Bot**
- **Question:** What steps should be taken if the bot displays a 'gas required exceeds allowance' error during transaction building?
- **Answer:** The most common cause of this is not having enough ETH on the address used by the bot to execute transactions. 



