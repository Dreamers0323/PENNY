# chatbot/penny_chatbot.py
# Enhanced AI-Powered Penny chatbot for user interactions (Accounts + Purchases)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import re
import spacy
from spacy.matcher import Matcher, PhraseMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from account.account_service import AccountService
from purchases.purchase_service import PurchaseService
from loan.loan_service import LoanService

class PennyChatbot:
    def __init__(self, user_id, session=None):
        self.user_id = user_id
        self.session = session
        
        # Initialize state from session or create new
        if session and 'penny_state' in session:
            self.state = session['penny_state']
            self.context = session.get('penny_context', {})
        else:
            self.state = None
            self.context = {}
        
        # Add persistent context for multi-turn conversations
        self.conversation_context = {
            "purchases": {},  # Store multiple purchases being planned
            "user_info": {},  # Store user's salary, family size, etc.
            "last_calculation": None  # Store last calculation for updates
        }
        
        try:
            self.account_service = AccountService()
            self.purchase_service = PurchaseService(user_id)
            self.loan_service = LoanService()
        except Exception as e:
            print(f"Error initializing PennyChatbot services: {e}")
            raise

        # === Enhanced NLP Setup ===
        self.nlp = spacy.load("en_core_web_sm")
        self.matcher = Matcher(self.nlp.vocab)
        self.phrase_matcher = PhraseMatcher(self.nlp.vocab)
        
        # Initialize intent classification
        self._setup_intent_classification()
        self._setup_entity_extraction()

    def _setup_intent_classification(self):
        """Set up advanced intent classification using multiple approaches"""
        
        # 1. Training data for intent classification
        self.intent_examples = {
            "balance_inquiry": [
                "what's my balance", "show my balance", "how much money do I have",
                "check balance", "current balance", "account balance", "my funds",
                "how much is in my account", "what do I have in savings", "total balance"
            ],
            "account_summary": [
                "show my accounts", "account summary", "list my accounts", 
                "what accounts do I have", "account information", "my bank accounts",
                "account details", "show account info", "my accounts"
            ],
            "transaction_history": [
                "show transactions", "transaction history", "recent transactions",
                "what did I spend", "payment history", "my transactions", 
                "show my spending", "transaction details", "recent payments"
            ],
            "purchase_planning": [
                "can I buy", "should I purchase", "can I afford", "buying advice",
                "purchase planning", "afford to buy", "help me buy", "planning to buy",
                "want to purchase", "thinking of buying", "can I get", "is it affordable",
                "will I be able to buy", "financial planning for purchase"
            ],
            "multiple_purchase_planning": [
                "both", "and", "also", "as well", "together", "combined",
                "how long for both", "total cost", "all together"
            ],
            "family_update": [
                "i have a family", "we are", "family of", "support", "people",
                "family members", "household size"
            ],
            "budget_inquiry": [
                "my budget", "budget summary", "show budgets", "budget status",
                "how much can I spend", "spending limits", "budget information",
                "check my budget", "budget details"
            ],
            "savings_goals": [
                "savings goals", "my goals", "saving progress", "goal status",
                "how close to my goal", "savings plan", "goal summary",
                "check my goals", "savings target"
            ],
            "loan_inquiry": [
                "my loans", "loan information", "loan balance", "loan status",
                "debt information", "what do I owe", "loan details",
                "outstanding loans", "loan summary"
            ],
            "greeting": [
                "hello", "hi", "hey", "good morning", "good afternoon",
                "greetings", "hi there", "hello there"
            ],
            "help": [
                "help", "what can you do", "how can you help", "assist me",
                "what are your capabilities", "help me", "assistance"
            ],
            "complaint": [
                "problem", "issue", "complaint", "error", "not working",
                "having trouble", "something wrong", "malfunction"
            ]
        }
        
        # 2. Create training data for TF-IDF
        self.all_examples = []
        self.all_labels = []
        
        for intent, examples in self.intent_examples.items():
            self.all_examples.extend(examples)
            self.all_labels.extend([intent] * len(examples))
        
        # 3. Train TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(self.all_examples)

    def _setup_entity_extraction(self):
        """Set up entity extraction patterns"""
        
        # Money patterns
        money_patterns = [
            [{"TEXT": {"REGEX": r"^\d+$"}}, {"LOWER": {"IN": ["kwacha", "zmw", "k"]}}],
            [{"TEXT": {"REGEX": r"^\d+,\d+$"}}, {"LOWER": {"IN": ["kwacha", "zmw", "k"]}}],
            [{"LOWER": {"IN": ["zmw", "k"]}}, {"TEXT": {"REGEX": r"^\d+$"}}],
            [{"TEXT": {"REGEX": r"^\d+\.\d+$"}}],  # Decimal numbers
        ]
        
        # Purchase intention patterns
        purchase_patterns = [
            [{"LEMMA": {"IN": ["buy", "purchase", "get", "afford"]}},
             {"POS": {"IN": ["DET", "ADJ"]}, "OP": "*"},
             {"POS": "NOUN", "OP": "+"}],
        ]
        
        # Add patterns to matcher
        self.matcher.add("MONEY_AMOUNT", money_patterns)
        self.matcher.add("PURCHASE_INTENT", purchase_patterns)

    def classify_intent(self, user_input):
        """Advanced intent classification using TF-IDF similarity"""
        try:
            # Clean and preprocess input
            cleaned_input = user_input.lower().strip()
            
            # Check for multiple purchase indicators
            if any(word in cleaned_input for word in ["both", "and", "together", "combined", "as well"]) and \
               any(word in cleaned_input for word in ["car", "house", "buy", "purchase", "cost", "long"]):
                return "multiple_purchase_planning", 0.8
            
            # Check for family update indicators
            if any(phrase in cleaned_input for phrase in ["i have a family", "we are", "family of", "family and"]):
                return "family_update", 0.8
            
            # Vectorize the input
            input_vector = self.vectorizer.transform([cleaned_input])
            
            # Calculate similarities
            similarities = cosine_similarity(input_vector, self.tfidf_matrix).flatten()
            
            # Find best match
            best_match_idx = np.argmax(similarities)
            best_similarity = similarities[best_match_idx]
            
            # If similarity is high enough, return the intent
            if best_similarity > 0.2:  # Lower threshold for better matching
                predicted_intent = self.all_labels[best_match_idx]
                return predicted_intent, best_similarity
            
            return None, 0.0
            
        except Exception as e:
            print(f"Error in intent classification: {e}")
            return None, 0.0

    def extract_entities(self, user_input):
        """Enhanced entity extraction"""
        doc = self.nlp(user_input)
        entities = {
            "money_amounts": [],
            "items": [],
            "numbers": [],
            "dates": [],
            "family_size": None
        }
        
        # Look for family size indicators
        family_patterns = [
            r'we are (\d+)', r'family of (\d+)', r'(\d+) people', 
            r'(\d+) members', r'household of (\d+)', r'support (\d+)'
        ]
        
        text_lower = user_input.lower()
        for pattern in family_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    entities["family_size"] = int(match.group(1))
                    break
                except:
                    pass
        
        # Use spaCy's built-in NER
        for ent in doc.ents:
            if ent.label_ == "MONEY":
                entities["money_amounts"].append(self._clean_money(ent.text))
            elif ent.label_ in ["PRODUCT", "ORG"]:
                entities["items"].append(ent.text)
            elif ent.label_ == "CARDINAL":
                try:
                    entities["numbers"].append(int(ent.text.replace(",", "")))
                except:
                    pass
            elif ent.label_ == "DATE":
                entities["dates"].append(ent.text)
        
        # Use custom patterns
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            label = self.nlp.vocab.strings[match_id]
            span_text = doc[start:end].text
            
            if label == "MONEY_AMOUNT":
                entities["money_amounts"].append(self._clean_money(span_text))
            elif label == "PURCHASE_INTENT":
                # Extract the item being purchased
                item = doc[start:end].text.split()[-1]  # Get the last word (likely the item)
                entities["items"].append(item)
        
        # Extract numbers using regex as backup
        numbers = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', user_input)
        for num_str in numbers:
            try:
                num = float(num_str.replace(",", ""))
                entities["numbers"].append(num)
            except:
                pass
        
        return entities

    def _clean_money(self, money_text):
        """Clean and standardize money amounts"""
        # Remove currency symbols and convert to float
        cleaned = re.sub(r'[^\d.,]', '', money_text)
        cleaned = cleaned.replace(',', '')
        try:
            return float(cleaned)
        except:
            return 0.0

    def analyze_purchase_feasibility(self, item, cost, salary, family_size=1):
        """Smart purchase analysis"""
        try:
            # Calculate living costs based on Zambian standards
            base_cost_per_person = 1833  # ZMW 11,000 / 6 people
            living_cost = base_cost_per_person * family_size
            
            # Calculate disposable income
            disposable_income = salary - living_cost
            
            if disposable_income <= 0:
                return {
                    "feasible": False,
                    "reason": "insufficient_income",
                    "message": f"Your salary of ZMW {salary:,.0f} doesn't cover basic living expenses of ZMW {living_cost:,.0f} for {family_size} people."
                }
            
            # Calculate savings potential (use 60% of disposable income for safety)
            monthly_savings = disposable_income * 0.6
            months_needed = cost / monthly_savings if monthly_savings > 0 else float('inf')
            
            # Determine feasibility
            if months_needed <= 3:
                feasibility = "immediately_affordable"
            elif months_needed <= 12:
                feasibility = "short_term_goal"
            elif months_needed <= 36:
                feasibility = "long_term_goal"
            else:
                feasibility = "not_practical"
            
            return {
                "feasible": feasibility != "not_practical",
                "feasibility_level": feasibility,
                "months_needed": months_needed,
                "monthly_savings_needed": monthly_savings,
                "disposable_income": disposable_income,
                "living_cost": living_cost
            }
            
        except Exception as e:
            print(f"Error in purchase analysis: {e}")
            return {"feasible": False, "reason": "calculation_error"}

    def analyze_multiple_purchases(self, purchases, salary, family_size=1):
        """Analyze multiple purchases together"""
        try:
            total_cost = sum(purchase['cost'] for purchase in purchases.values())
            
            # Get individual analysis for context
            individual_analyses = {}
            for item, purchase_info in purchases.items():
                individual_analyses[item] = self.analyze_purchase_feasibility(
                    item, purchase_info['cost'], salary, family_size
                )
            
            # Analyze combined purchase
            combined_analysis = self.analyze_purchase_feasibility(
                "combined purchases", total_cost, salary, family_size
            )
            
            return {
                "individual": individual_analyses,
                "combined": combined_analysis,
                "total_cost": total_cost
            }
            
        except Exception as e:
            print(f"Error in multiple purchase analysis: {e}")
            return None

    def process_message(self, user_input):
        try:
            user_input = user_input.strip()
            print(f"Processing message: '{user_input}' for user {self.user_id}")
            print(f"Current state: {self.state}, Context: {self.context}")
            print(f"Conversation context: {self.conversation_context}")

            # Handle stateful conversations first
            if self.state == "purchase_item":
                return self._handle_purchase_flow(user_input)

            # Classify intent using AI
            intent, confidence = self.classify_intent(user_input)
            entities = self.extract_entities(user_input)
            
            print(f"Intent: {intent}, Confidence: {confidence:.2f}")
            print(f"Entities: {entities}")

            # Handle family update
            if intent == "family_update" or entities.get("family_size"):
                return self._handle_family_update(user_input, entities)

            # Handle multiple purchase planning
            if intent == "multiple_purchase_planning":
                return self._handle_multiple_purchase_question(user_input, entities)

            # Handle clear intents first (with higher priority)
            if intent == "balance_inquiry":
                return self._get_balance_response()
            elif intent == "account_summary":
                return self._get_account_summary_response()
            elif intent == "transaction_history":
                return self._get_transactions_response()
            elif intent == "budget_inquiry":
                return self._get_budget_summary_response()
            elif intent == "savings_goals":
                return self._get_savings_goals_response()
            elif intent == "loan_inquiry":
                return self._get_loans_response()
            elif intent == "greeting":
                return "Hello! I'm Penny, your AI financial assistant. I can help you with account information, budgets, savings goals, and smart purchase planning. What would you like to know?"
            elif intent == "help":
                return self._get_help_response()
            elif intent == "complaint":
                return self._get_complaint_response()

            # Handle purchase planning only if it's clearly a purchase question
            elif intent == "purchase_planning" or self._is_strong_purchase_question(user_input, entities):
                return self._handle_smart_purchase_question(user_input, entities)

            # Fallback for unrecognized intents
            return "I'm here to help with your banking and financial needs. You can ask me about your accounts, balances, transactions, budgets, savings goals, or get advice on purchases. What would you like to know?"

        except Exception as e:
            print(f"Error in process_message: {e}")
            return "I'm sorry, I encountered an error. Please try asking about your accounts, balance, or financial planning."

    def _handle_family_update(self, user_input, entities):
        """Handle family size updates and recalculate previous analyses"""
        family_size = entities.get("family_size")
        
        if family_size:
            # Update user info
            self.conversation_context["user_info"]["family_size"] = family_size
            
            # If we have a recent purchase calculation, update it
            if self.conversation_context["last_calculation"]:
                last_calc = self.conversation_context["last_calculation"]
                
                # Recalculate with family size
                updated_analysis = self.analyze_purchase_feasibility(
                    last_calc["item"],
                    last_calc["cost"],
                    last_calc["salary"],
                    family_size
                )
                
                # Store updated calculation
                self.conversation_context["last_calculation"]["family_size"] = family_size
                self.conversation_context["last_calculation"]["analysis"] = updated_analysis
                
                response = f"Thanks for letting me know you have a family of {family_size}! Let me recalculate the {last_calc['item']} purchase with your family size in mind:\n\n"
                response += self._format_purchase_analysis(
                    last_calc["item"], 
                    last_calc["cost"], 
                    last_calc["salary"], 
                    updated_analysis
                )
                
                return response
            else:
                return f"Got it! I've noted that you have a family of {family_size} people. This will be considered in any future purchase planning."
        
        # Try to extract family size from text
        text_lower = user_input.lower()
        family_patterns = [
            r'we are (\d+)', r'family of (\d+)', r'(\d+) people', 
            r'(\d+) members'
        ]
        
        for pattern in family_patterns:
            match = re.search(pattern, text_lower)
            if match:
                family_size = int(match.group(1))
                return self._handle_family_update(user_input, {"family_size": family_size})
        
        return "I understand you mentioned family. Could you tell me how many people are in your household (including yourself)?"

    def _handle_multiple_purchase_question(self, user_input, entities):
        """Handle questions about multiple purchases"""
        try:
            # Check if we have stored purchases
            if not self.conversation_context["purchases"]:
                return "I don't have information about multiple purchases yet. Please tell me about each item you want to buy with their costs."
            
            # Get user's salary and family size
            salary = self.conversation_context["user_info"].get("salary")
            family_size = self.conversation_context["user_info"].get("family_size", 1)
            
            if not salary:
                return "I need to know your salary to calculate the total timeline. What's your monthly salary?"
            
            # Analyze all purchases together
            analysis = self.analyze_multiple_purchases(
                self.conversation_context["purchases"], 
                salary, 
                family_size
            )
            
            if analysis:
                return self._format_multiple_purchase_analysis(analysis)
            else:
                return "I couldn't calculate the combined purchase timeline. Please try again."
            
        except Exception as e:
            print(f"Error in multiple purchase handling: {e}")
            return "I encountered an error calculating multiple purchases. Please try asking about each item separately."

    def _format_multiple_purchase_analysis(self, analysis):
        """Format multiple purchase analysis response"""
        try:
            individual = analysis["individual"]
            combined = analysis["combined"]
            total_cost = analysis["total_cost"]
            
            response_parts = [f"**Combined Purchase Analysis (Total: ZMW {total_cost:,.0f})**\n"]
            
            # Individual breakdown
            response_parts.append("**Individual Items:**")
            for item, item_analysis in individual.items():
                if item_analysis["feasible"]:
                    months = item_analysis["months_needed"]
                    response_parts.append(f"• {item.title()}: {months:.0f} months")
                else:
                    response_parts.append(f"• {item.title()}: Not feasible individually")
            
            response_parts.append("")
            
            # Combined analysis
            if combined["feasible"]:
                months = combined["months_needed"]
                savings_needed = combined["monthly_savings_needed"]
                
                if combined["feasibility_level"] == "immediately_affordable":
                    response_parts.append(f"✅ **All items together: {months:.0f} months**")
                elif combined["feasibility_level"] == "short_term_goal":
                    response_parts.append(f"✅ **All items together: {months:.0f} months** (Short-term goal)")
                elif combined["feasibility_level"] == "long_term_goal":
                    response_parts.append(f"⚠️ **All items together: {months:.0f} months** ({months/12:.1f} years)")
                
                response_parts.append(f"💵 **Required monthly savings: ZMW {savings_needed:,.0f}**")
                
                # Strategy recommendation
                shortest_individual = min(
                    (months for analysis in individual.values() if analysis["feasible"] for months in [analysis["months_needed"]]),
                    default=float('inf')
                )
                
                if shortest_individual < months:
                    response_parts.append(f"\n💡 **Strategy suggestion:** Buy items one by one starting with the most affordable, then save for the next. This might be faster than saving for everything at once.")
            
            else:
                response_parts.append("❌ **Combined purchase is not feasible** with your current salary and family expenses.")
                
                # Show what's individually possible
                feasible_items = [item for item, analysis in individual.items() if analysis["feasible"]]
                if feasible_items:
                    response_parts.append(f"However, you could afford: {', '.join(feasible_items)} individually.")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            print(f"Error formatting multiple purchase analysis: {e}")
            return "I couldn't format the analysis properly. Please try again."

    def _is_strong_purchase_question(self, user_input, entities):
        """Determine if this is clearly a purchase-related question (stricter criteria)"""
        strong_purchase_indicators = [
            "can i buy", "should i buy", "can i afford", "afford to buy",
            "purchase", "buying", "want to buy"
        ]
        
        text_lower = user_input.lower()
        
        # Must have strong purchase indicators AND relevant entities
        has_strong_purchase_intent = any(indicator in text_lower for indicator in strong_purchase_indicators)
        has_money = len(entities["money_amounts"]) > 0 or len(entities["numbers"]) > 0
        has_item = (len(entities["items"]) > 0 or 
                   any(word in text_lower for word in ["car", "house", "phone", "laptop", "furniture"]))
        
        # Require both strong intent AND supporting entities
        return has_strong_purchase_intent and (has_money or has_item)

    def _handle_smart_purchase_question(self, user_input, entities):
        """Handle intelligent purchase questions with context awareness"""
        try:
            print(f"Smart purchase question analysis:")
            print(f"Input: {user_input}")
            print(f"Entities: {entities}")
            
            # Extract key information from the question
            money_amounts = entities["money_amounts"] + entities["numbers"]
            items = entities["items"]
            
            # Remove duplicates and sort
            money_amounts = list(set(money_amounts))
            money_amounts.sort()
            
            print(f"Money amounts found: {money_amounts}")
            print(f"Items found: {items}")
            
            # Try to identify cost and salary from the question
            cost = None
            salary = None
            
            # Look for contextual clues
            text_lower = user_input.lower()
            
            # Better regex patterns for extracting salary and cost
            salary_patterns = [
                r'salary.*?(\d+(?:,\d+)*)',
                r'earn.*?(\d+(?:,\d+)*)',
                r'make.*?(\d+(?:,\d+)*)',
                r'income.*?(\d+(?:,\d+)*)',
                r'with.*?(\d+(?:,\d+)*)',  # "with a salary of X"
            ]
            
            cost_patterns = [
                r'costs?.*?(\d+(?:,\d+)*)',
                r'price.*?(\d+(?:,\d+)*)',
                r'worth.*?(\d+(?:,\d+)*)',
                r'(\d+(?:,\d+)*).*?(?:car|house|phone|laptop|item)',  # "15000 car"
            ]
            
            # Try to find salary first
            for pattern in salary_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    salary = float(match.group(1).replace(',', ''))
                    print(f"Found salary: {salary}")
                    break
            
            # Try to find cost
            for pattern in cost_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    cost = float(match.group(1).replace(',', ''))
                    print(f"Found cost: {cost}")
                    break
            
            # If we have exactly 2 numbers and haven't identified both
            if len(money_amounts) == 2 and (not salary or not cost):
                amounts = sorted(money_amounts)
                
                # Use context clues
                if "with" in text_lower and "salary" in text_lower:
                    # Pattern: "Can I buy X that costs Y with salary of Z"
                    salary = amounts[1]  # Usually second number
                    cost = amounts[0]
                elif "salary" in text_lower:
                    # If salary mentioned, find which number is near "salary"
                    if not salary:
                        salary = amounts[1]  # Often the second number mentioned
                    cost = amounts[0] if salary == amounts[1] else amounts[1]
                elif "costs" in text_lower or "cost" in text_lower:
                    # Pattern: "costs X with salary Y"
                    cost = amounts[0]
                    salary = amounts[1]
                else:
                    # Default: first number is cost, second is salary
                    cost = amounts[0]
                    salary = amounts[1]
                    
                print(f"Using heuristics - Cost: {cost}, Salary: {salary}")
            
            # Try to identify the item
            item = "item"
            if items:
                item = items[0]
            else:
                # Look for common items in text
                common_items = ["car", "house", "phone", "laptop", "computer", "tv", "television", "furniture", "bicycle", "bike"]
                for potential_item in common_items:
                    if potential_item in text_lower:
                        item = potential_item
                        break
            
            print(f"Final extraction - Item: {item}, Cost: {cost}, Salary: {salary}")
            
            # Store user information for context
            if salary:
                self.conversation_context["user_info"]["salary"] = salary
            if cost and item:
                self.conversation_context["purchases"][item] = {"cost": cost}
            
            # If we have both cost and salary, provide immediate analysis
            if cost and salary and cost > 0 and salary > 0:
                print("Providing immediate analysis")
                
                # Use existing family size if available
                family_size = self.conversation_context["user_info"].get("family_size", 1)
                
                analysis = self.analyze_purchase_feasibility(item, cost, salary, family_size)
                
                # Store this calculation for potential updates
                self.conversation_context["last_calculation"] = {
                    "item": item,
                    "cost": cost,
                    "salary": salary,
                    "family_size": family_size,
                    "analysis": analysis
                }
                
                return self._format_purchase_analysis(item, cost, salary, analysis)
            
            # If missing information, start the guided flow
            else:
                print("Starting guided flow - missing information")
                self.state = "purchase_item"
                self.context = {}
                if item != "item":
                    self.context["item"] = item
                if cost and cost > 0:
                    self.context["cost"] = cost
                if salary and salary > 0:
                    self.context["salary"] = salary
                
                self._save_state()
                
                if cost and salary:
                    return "Do you have family members you support? (yes/no)"
                elif cost and not salary:
                    return f"I can help you plan for buying a {item} that costs ZMW {cost:,.0f}. What's your monthly salary?"
                elif salary and not cost:
                    return f"I can help you plan a purchase with your salary of ZMW {salary:,.0f}. What would you like to buy and how much does it cost?"
                elif item != "item":
                    return f"I can help you plan for buying a {item}! What's the cost and what's your monthly salary? Please tell me both amounts."
                else:
                    return "I'd be happy to help you plan a purchase! What would you like to buy?"

        except Exception as e:
            print(f"Error in _handle_smart_purchase_question: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to guided flow
            self.state = "purchase_item"
            self.context = {}
            self._save_state()
            return "I'd be happy to help you plan a purchase! What would you like to buy?"

    def _format_purchase_analysis(self, item, cost, salary, analysis):
        """Format the purchase analysis response"""
        if not analysis["feasible"]:
            if analysis.get("reason") == "insufficient_income":
                return f"❌ I'm sorry, but with a salary of ZMW {salary:,.0f}, {analysis['message']} You might need to increase your income or reduce expenses first."
            else:
                return f"❌ Based on my analysis, purchasing a {item} for ZMW {cost:,.0f} may not be feasible with your current salary of ZMW {salary:,.0f}."
        
        months = analysis["months_needed"]
        savings_needed = analysis["monthly_savings_needed"]
        
        if analysis["feasibility_level"] == "immediately_affordable":
            return (f"✅ **Great news!** You can afford the {item} right away!<br><br>"
                   f"💰 With your salary of ZMW {salary:,.0f}, you have enough disposable income "
                   f"to purchase this {item} for ZMW {cost:,.0f} within {months:.0f} months.<br><br>"
                   f"💡 **Recommendation:** Save ZMW {savings_needed:,.0f} per month.")
        
        elif analysis["feasibility_level"] == "short_term_goal":
            return (f"✅ **Definitely achievable!**<br><br>"
                   f"🎯 You can buy the {item} (ZMW {cost:,.0f}) in approximately **{months:.0f} months**<br>"
                   f"💰 Monthly salary: ZMW {salary:,.0f}<br>"
                   f"💵 Recommended savings: ZMW {savings_needed:,.0f}/month<br><br>"
                   f"This is a great short-term financial goal!")
        
        elif analysis["feasibility_level"] == "long_term_goal":
            return (f"⚠️ **Long-term planning needed**<br><br>"
                   f"🎯 You can buy the {item} in approximately **{months:.0f} months** ({months/12:.1f} years)<br>"
                   f"💰 Monthly salary: ZMW {salary:,.0f}<br>"
                   f"💵 Recommended savings: ZMW {savings_needed:,.0f}/month<br><br>"
                   f"💡 Consider if this is the best use of your money or if there are alternatives.")
        
        else:
            return (f"❌ This purchase would take over {months:.0f} months to achieve, which may not be practical. "
                   f"Consider increasing your income or finding a less expensive alternative.")

    def _save_state(self):
        """Save state to session"""
        if self.session is not None:
            self.session['penny_state'] = self.state
            self.session['penny_context'] = self.context
    
    def _reset_state(self):
        """Reset conversation state"""
        self.state = None
        self.context = {}
        self._save_state()

    def _handle_purchase_flow(self, user_input):
        """Handle the stateful purchase planning conversation"""
        try:
            print(f"In purchase flow - Context: {self.context}")
            print(f"User input: {user_input}")
            
            # Check if user wants to exit purchase flow
            if any(word in user_input.lower() for word in ["cancel", "stop", "exit", "nevermind", "accounts", "balance", "help"]):
                self._reset_state()
                # Process as new request
                return self.process_message(user_input)
            
            # Check if user is providing both cost and salary in response
            entities = self.extract_entities(user_input)
            numbers = entities["numbers"] + entities["money_amounts"]
            numbers = [n for n in numbers if n > 0]  # Remove zeros
            
            # Step 1: Get the item name (only if we don't have it)
            if "item" not in self.context:
                self.context["item"] = user_input.strip()
                return f"Perfect! I'll help you plan for buying a {user_input}. How much does it cost and what's your monthly salary? You can tell me both amounts."

            # Step 2: Get cost and salary
            if "cost" not in self.context or "salary" not in self.context:
                text_lower = user_input.lower()
                
                # Check if user is reminding us of previously mentioned numbers
                if ("remember" in text_lower or "told you" in text_lower or 
                    "said" in text_lower) and len(numbers) >= 2:
                    # User is repeating the information - extract it properly
                    amounts = sorted(numbers)
                    
                    # Use context to determine which is which
                    if "salary" in text_lower:
                        # Find salary number
                        salary_match = re.search(r'salary.*?(\d+(?:,\d+)*)', text_lower)
                        if salary_match:
                            self.context["salary"] = float(salary_match.group(1).replace(',', ''))
                        else:
                            self.context["salary"] = amounts[0]  # Assume first/smaller number
                            
                        # Other number is cost
                        for num in numbers:
                            if num != self.context["salary"]:
                                self.context["cost"] = num
                                break
                    else:
                        # Default assumption: larger number is cost
                        self.context["cost"] = amounts[-1]  # Largest number
                        self.context["salary"] = amounts[0]   # Smallest number
                        
                elif len(numbers) >= 2:
                    # Two numbers provided - determine which is which
                    amounts = sorted(numbers)
                    
                    if "salary" in text_lower or "earn" in text_lower:
                        # Find number mentioned near "salary"
                        salary_match = re.search(r'salary.*?(\d+(?:,\d+)*)', text_lower)
                        if salary_match:
                            self.context["salary"] = float(salary_match.group(1).replace(',', ''))
                            # Other number is cost
                            for num in numbers:
                                if num != self.context["salary"]:
                                    self.context["cost"] = num
                                    break
                        else:
                            # Assume order: "salary is X and car is Y"
                            self.context["salary"] = amounts[0]
                            self.context["cost"] = amounts[1]
                    elif "cost" in text_lower or "car" in text_lower:
                        # Find number mentioned near "cost" or item
                        cost_match = re.search(r'(?:cost|car).*?(\d+(?:,\d+)*)', text_lower)
                        if cost_match:
                            self.context["cost"] = float(cost_match.group(1).replace(',', ''))
                            # Other number is salary
                            for num in numbers:
                                if num != self.context["cost"]:
                                    self.context["salary"] = num
                                    break
                        else:
                            # Default: first number is salary, second is cost
                            self.context["salary"] = amounts[0]
                            self.context["cost"] = amounts[1]
                    else:
                        # Default heuristic: smaller number is salary, larger is cost
                        self.context["salary"] = amounts[0]
                        self.context["cost"] = amounts[1]
                    
                    print(f"Extracted - Salary: {self.context.get('salary')}, Cost: {self.context.get('cost')}")
                    return "Do you have family members you support? (yes/no)"
                    
                elif len(numbers) == 1:
                    if "cost" not in self.context:
                        self.context["cost"] = numbers[0]
                        return f"Great! The {self.context['item']} costs ZMW {numbers[0]:,.0f}. Now, what's your monthly salary?"
                    else:
                        self.context["salary"] = numbers[0]
                        return "Do you have family members you support? (yes/no)"
                else:
                    return "I need both the cost and your salary to help you. Please tell me both amounts in ZMW. For example: 'The car costs 15000 and my salary is 8000'"

            # Step 3: Family information
            if "has_family" not in self.context:
                text_lower = user_input.lower()
                if any(word in text_lower for word in ["yes", "yeah", "yep", "i do", "i have"]):
                    self.context["has_family"] = True
                    return "How many people do you support in total (including yourself)?"
                elif any(word in text_lower for word in ["no", "nope", "none", "don't", "dont"]):
                    self.context["has_family"] = False
                    self.context["family_size"] = 1
                    return self._calculate_final_plan()
                else:
                    return "Please answer yes or no - do you support any family members?"

            # Step 4: Get family size
            if self.context.get("has_family") and "family_size" not in self.context:
                try:
                    family_size = int(re.findall(r'\d+', user_input)[0])
                    if family_size < 1:
                        return "Please enter a valid number (1 or more)."
                    self.context["family_size"] = family_size
                    return self._calculate_final_plan()
                except (ValueError, IndexError):
                    return "Please enter the number of people you support (e.g., 3)."

            return self._calculate_final_plan()
            
        except Exception as e:
            print(f"Error in purchase flow: {e}")
            import traceback
            traceback.print_exc()
            self._reset_state()
            return "Sorry, I encountered an error. Let's start over - what would you like to buy?"

    def _calculate_final_plan(self):
        """Calculate and return the final purchase plan"""
        try:
            cost = self.context["cost"]
            salary = self.context["salary"]
            family_size = self.context.get("family_size", 1)
            item = self.context.get("item", "item")
            
            # Store in conversation context for future reference
            self.conversation_context["user_info"]["salary"] = salary
            self.conversation_context["user_info"]["family_size"] = family_size
            self.conversation_context["purchases"][item] = {"cost": cost}
            
            analysis = self.analyze_purchase_feasibility(item, cost, salary, family_size)
            
            # Store this calculation for potential updates
            self.conversation_context["last_calculation"] = {
                "item": item,
                "cost": cost,
                "salary": salary,
                "family_size": family_size,
                "analysis": analysis
            }
            
            response = self._format_purchase_analysis(item, cost, salary, analysis)
            
            self._reset_state()
            return response
                
        except Exception as e:
            print(f"Error in final plan calculation: {e}")
            self._reset_state()
            return "Sorry, I encountered an error calculating your plan. Please try again."

    # Keep all your existing response methods unchanged
    def _get_balance_response(self):
        """Get balance information"""
        try:
            accounts = self.account_service.get_accounts_by_user(self.user_id)
            if not accounts:
                return "You don't have any accounts yet. Please create an account first."
            
            response_parts = ["Here are your account balances:"]
            total_balance = 0
            
            for acc in accounts:
                response_parts.append(f"• {acc['account_type']}: ZMW {acc['balance']:.2f}")
                total_balance += acc['balance']
            
            response_parts.append(f"<br><strong>Total balance: ZMW {total_balance:.2f}</strong>")
            return "<br>".join(response_parts)
        except Exception as e:
            print(f"Error in _get_balance_response: {e}")
            return "I couldn't retrieve your balance information. Please try again later."

    def _get_account_summary_response(self):
        """Get account summary"""
        try:
            accounts = self.account_service.get_accounts_by_user(self.user_id)
            if not accounts:
                return "You don't have any accounts yet."
            
            response_parts = ["Here's your account summary:"]
            for acc in accounts:
                status = "Active" if acc['active'] else "Inactive"
                response_parts.append(f"• {acc['account_type']} ({acc['account_id'][-6:]}) - ZMW {acc['balance']:.2f} ({status})")
            
            return "<br>".join(response_parts)
        except Exception as e:
            print(f"Error in _get_account_summary_response: {e}")
            return "I couldn't retrieve your account information. Please try again later."

    def _get_transactions_response(self):
        """Get recent transactions"""
        try:
            accounts = self.account_service.get_accounts_by_user(self.user_id)
            if not accounts:
                return "You don't have any accounts yet."
            
            response_parts = ["Recent transactions:"]
            has_transactions = False
            
            for acc in accounts:
                txns = self.account_service.get_transaction_history(acc['account_id'])
                if txns:
                    has_transactions = True
                    response_parts.append(f"<br><strong>{acc['account_type']} account:</strong>")
                    for i, txn in enumerate(txns[:3]):  # Show only last 3 transactions per account
                        txn_type, amount, timestamp = txn
                        sign = "+" if txn_type in ["deposit", "transfer_in"] else "-"
                        response_parts.append(f"  {sign}ZMW {amount:.2f} ({txn_type}) on {timestamp[:10]}")
            
            if not has_transactions:
                return "No recent transactions found."
            
            return "<br>".join(response_parts)
        except Exception as e:
            print(f"Error in _get_transactions_response: {e}")
            return "I couldn't retrieve your transaction history. Please try again later."

    def _get_budget_summary_response(self):
        """Get budget summary"""
        try:
            budget_summary = self.purchase_service.get_budget_summary()
            if not budget_summary:
                return "You haven't set any budgets yet. Visit the 'Plans' section to create budgets."
            
            return (f"<strong>Budget summary:</strong><br>"
                   f"Total budget: ZMW {budget_summary['total_budget']:.2f}<br>"
                   f"Spent: ZMW {budget_summary['total_spent']:.2f}<br>"
                   f"Remaining: ZMW {budget_summary['remaining']:.2f}")
            
        except Exception as e:
            print(f"Error in _get_budget_summary_response: {e}")
            return "I couldn't retrieve your budget information. Please try again later."

    def _get_savings_goals_response(self):
        """Get savings goals"""
        try:
            goals = self.purchase_service.get_savings_goals()
            if not goals:
                return "You don't have any savings goals yet. Visit the 'Plans' section to create goals."
            
            response_parts = ["Your savings goals:"]
            for goal in goals:
                goal_name = goal['goal_name']
                target_amount = float(goal['target_amount'])
                saved_amount = float(goal['saved_amount'])
                
                progress = (saved_amount / target_amount * 100) if target_amount > 0 else 0
                remaining = target_amount - saved_amount
                
                if remaining <= 0:
                    status = "✅ Complete!"
                else:
                    status = f"ZMW {remaining:.2f} remaining"
                
                response_parts.append(
                    f"• {goal_name}: ZMW {saved_amount:.2f}/ZMW {target_amount:.2f} "
                    f"({progress:.1f}%) - {status}"
                )
            
            return "<br>".join(response_parts)
            
        except Exception as e:
            print(f"Error in _get_savings_goals_response: {e}")
            import traceback
            traceback.print_exc()
            return "I couldn't retrieve your savings goals. Please try again later."

    def _get_loans_response(self):
        """Get loan information"""
        try:
            loans = self.loan_service.get_loans_by_user(self.user_id)
            if not loans:
                return "You don't have any active loans. You can apply for one in the Loan section."
        
            response_parts = ["Here are your loans:"]
            for loan in loans:
                response_parts.append(
                    f"• {loan['loan_type']} of ZMW {loan['principal']:.2f}, "
                    f"remaining: ZMW {loan['balance']:.2f}, "
                    f"interest: {loan['interest_rate']}%, "
                    f"term: {loan['term']} months"
                )
            return "<br>".join(response_parts)
        except Exception as e:
            print(f"Error in _get_loans_response: {e}")
            return "I couldn't retrieve your loan information. Please try again later."

    def _get_complaint_response(self):
        """Handle user complaints"""
        return (
            "I'm sorry you're experiencing an issue. "
            "Could you describe the problem in more detail? "
            "I can log it for review, or if it's urgent please contact customer support or visit your nearest branch."
        )

    def _get_help_response(self):
        """Get help message"""
        return """<strong>I'm your AI financial assistant! I can help you with:</strong><br><br>
💰 <strong>Account Information</strong><br>
- Check your balance and account details<br>
- View recent transactions and history<br><br>
📊 <strong>Smart Financial Planning</strong><br>
- "Can I afford to buy a car that costs 50,000?"<br>
- "Should I purchase a laptop with my 8,000 salary?"<br>
- Budget and savings goal tracking<br><br>
🎯 <strong>Purchase Planning</strong><br>
- Intelligent affordability analysis<br>
- Personalized saving strategies<br>
- Family-based financial planning<br><br>
🏦 <strong>Banking Services</strong><br>
- Loan information and details<br>
- Account summaries and management<br><br>
💬 <strong>Natural Conversation</strong><br>
Just ask me anything about your finances in your own words!<br>
I understand natural language and context.<br><br>
<em>Try asking: "Can I buy a phone that costs 3000 with my 7000 salary?"</em>"""