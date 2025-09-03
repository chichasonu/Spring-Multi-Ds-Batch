import java.util.*;
import java.util.regex.*;
import java.security.SecureRandom;
import java.util.concurrent.ConcurrentHashMap;

// Token entity to store mapping
class Token {
    private String originalValue;
    private String tokenValue;
    private String type;
    private long timestamp;
    
    public Token(String originalValue, String tokenValue, String type) {
        this.originalValue = originalValue;
        this.tokenValue = tokenValue;
        this.type = type;
        this.timestamp = System.currentTimeMillis();
    }
    
    // Getters
    public String getOriginalValue() { return originalValue; }
    public String getTokenValue() { return tokenValue; }
    public String getType() { return type; }
    public long getTimestamp() { return timestamp; }
}

// Main tokenization service
public class DataTokenizationAPI {
    
    private static final Map<String, Token> tokenStore = new ConcurrentHashMap<>();
    private static final Map<String, String> reverseTokenStore = new ConcurrentHashMap<>();
    private static final SecureRandom random = new SecureRandom();
    
    // Regex patterns for different data types
    private static final Pattern AMOUNT_PATTERN = Pattern.compile("\\$([0-9]+(?:\\.[0-9]{2})?)");
    private static final Pattern MERCHANT_PATTERN = Pattern.compile("\\bat\\s+([A-Z][A-Z0-9\\s&]+?)(?=\\s+and|\\s*\\.|$)");
    
    /**
     * Main method to tokenize and mask input text
     * @param input The original text containing sensitive data
     * @return TokenizationResult containing masked text and token mappings
     */
    public static TokenizationResult tokenizeAndMask(String input) {
        String processedText = input;
        Map<String, String> tokenMappings = new HashMap<>();
        
        // Process amounts
        processedText = processAmounts(processedText, tokenMappings);
        
        // Process merchant names
        processedText = processMerchants(processedText, tokenMappings);
        
        return new TokenizationResult(processedText, tokenMappings);
    }
    
    /**
     * Process and tokenize monetary amounts
     */
    private static String processAmounts(String text, Map<String, String> mappings) {
        Matcher matcher = AMOUNT_PATTERN.matcher(text);
        StringBuffer result = new StringBuffer();
        
        while (matcher.find()) {
            String fullAmount = matcher.group(0); // e.g., "$71.75"
            String numericAmount = matcher.group(1); // e.g., "71.75"
            
            String token = getOrCreateToken(fullAmount, "AMOUNT");
            String maskedAmount = "$***.**";
            
            mappings.put(token, fullAmount);
            matcher.appendReplacement(result, maskedAmount + " [TOKEN:" + token + "]");
        }
        matcher.appendTail(result);
        return result.toString();
    }
    
    /**
     * Process and tokenize merchant names
     */
    private static String processMerchants(String text, Map<String, String> mappings) {
        Matcher matcher = MERCHANT_PATTERN.matcher(text);
        StringBuffer result = new StringBuffer();
        
        while (matcher.find()) {
            String merchantName = matcher.group(1).trim();
            
            String token = getOrCreateToken(merchantName, "MERCHANT");
            String maskedMerchant = "***MERCHANT***";
            
            mappings.put(token, merchantName);
            matcher.appendReplacement(result, "at " + maskedMerchant + " [TOKEN:" + token + "]");
        }
        matcher.appendTail(result);
        return result.toString();
    }
    
    /**
     * Generate or retrieve existing token for a value
     */
    private static String getOrCreateToken(String originalValue, String type) {
        // Check if token already exists
        String existingToken = reverseTokenStore.get(originalValue);
        if (existingToken != null) {
            return existingToken;
        }
        
        // Generate new token
        String token = generateToken(type);
        
        // Store bidirectional mapping
        Token tokenObj = new Token(originalValue, token, type);
        tokenStore.put(token, tokenObj);
        reverseTokenStore.put(originalValue, token);
        
        return token;
    }
    
    /**
     * Generate a secure random token
     */
    private static String generateToken(String type) {
        String prefix = type.equals("AMOUNT") ? "AMT_" : "MER_";
        StringBuilder token = new StringBuilder(prefix);
        
        String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        for (int i = 0; i < 8; i++) {
            token.append(chars.charAt(random.nextInt(chars.length())));
        }
        
        return token.toString();
    }
    
    /**
     * Detokenize text by replacing tokens with original values
     * @param tokenizedText Text containing tokens
     * @return Original text with sensitive data restored
     */
    public static String detokenize(String tokenizedText) {
        String result = tokenizedText;
        
        // Pattern to match tokens
        Pattern tokenPattern = Pattern.compile("\\[TOKEN:(\\w+)\\]");
        Matcher matcher = tokenPattern.matcher(tokenizedText);
        
        StringBuffer sb = new StringBuffer();
        while (matcher.find()) {
            String token = matcher.group(1);
            Token tokenObj = tokenStore.get(token);
            
            if (tokenObj != null) {
                matcher.appendReplacement(sb, "");
                // Replace the masked value before the token with original value
                String beforeToken = sb.toString();
                if (tokenObj.getType().equals("AMOUNT")) {
                    beforeToken = beforeToken.replaceAll("\\$\\*\\*\\*\\.\\*\\*$", tokenObj.getOriginalValue());
                } else if (tokenObj.getType().equals("MERCHANT")) {
                    beforeToken = beforeToken.replaceAll("\\*\\*\\*MERCHANT\\*\\*\\*$", tokenObj.getOriginalValue());
                }
                sb.setLength(0);
                sb.append(beforeToken);
            } else {
                matcher.appendReplacement(sb, matcher.group(0)); // Keep original if token not found
            }
        }
        matcher.appendTail(sb);
        
        return sb.toString();
    }
    
    /**
     * Get token information
     */
    public static Token getTokenInfo(String token) {
        return tokenStore.get(token);
    }
    
    /**
     * Clear all stored tokens (for testing or reset purposes)
     */
    public static void clearTokenStore() {
        tokenStore.clear();
        reverseTokenStore.clear();
    }
    
    // Result class to hold tokenization results
    public static class TokenizationResult {
        private final String maskedText;
        private final Map<String, String> tokenMappings;
        
        public TokenizationResult(String maskedText, Map<String, String> tokenMappings) {
            this.maskedText = maskedText;
            this.tokenMappings = tokenMappings;
        }
        
        public String getMaskedText() { return maskedText; }
        public Map<String, String> getTokenMappings() { return tokenMappings; }
        
        @Override
        public String toString() {
            return "TokenizationResult{\n" +
                   "  maskedText='" + maskedText + "'\n" +
                   "  tokenMappings=" + tokenMappings + "\n" +
                   "}";
        }
    }
    
    // Demo and test method
    public static void main(String[] args) {
        // Test with various amount formats
        String[] testInputs = {
            "Spent $71.75 at LOS POLLOS and $43.43 at QMART. Income Exceeds recent expenses $122.50",
            "Large transaction of $12,000 at BANK and $1,500.25 at STORE",
            "Payment $15,000.00 processed at VENDOR and small fee $5.99 at SERVICE",
            "Transfer $250,000 to ACCOUNT and charge $2,500.50 at MERCHANT"
        };
        
        for (int i = 0; i < testInputs.length; i++) {
            String input = testInputs[i];
            System.out.println("=== Test Case " + (i + 1) + " ===");
            System.out.println("Original text:");
            System.out.println(input);
            System.out.println();
            
            // Tokenize and mask
            TokenizationResult result = tokenizeAndMask(input);
            
            System.out.println("Masked and tokenized text:");
            System.out.println(result.getMaskedText());
            System.out.println();
            
            System.out.println("Token mappings:");
            result.getTokenMappings().forEach((token, value) -> 
                System.out.println("  " + token + " -> " + value));
            System.out.println();
            
            // Demonstrate detokenization
            String detokenized = detokenize(result.getMaskedText());
            System.out.println("Detokenized text:");
            System.out.println(detokenized);
            System.out.println();
            
            if (i < testInputs.length - 1) {-----------------------
                System.out.println("---");
            }
        }
        
        // Show all stored token information
        System.out.println("=== All Stored Tokens ===");
        tokenStore.values().forEach(tokenInfo -> {
            System.out.println("Token: " + tokenInfo.getTokenValue() + 
                             " -> " + tokenInfo.getOriginalValue() + 
                             " (Type: " + tokenInfo.getType() + ")");
        });
    }
}--------------------------------------------------
