import numpy as np
import google.generativeai as genai
from faq_data import college_faq
import re

class RAGChatbot:
    def __init__(self, api_key):
        """Initialize RAG chatbot with simple keyword matching + LLM"""
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # List available models and find the best one
        print("Checking available models...")
        available_models = []
        try:
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
                    print(f"Available: {model.name}")
        except Exception as e:
            print(f"Error listing models: {e}")
        
        # Try to initialize with available models
        model_name = None
        model_priority = [
            'models/gemini-2.5-flash',
            'models/gemini-2.0-flash',
            'models/gemini-flash-latest',
            'gemini-1.5-flash',
            'models/gemini-1.5-flash'
        ]
        
        for model in model_priority:
            try:
                print(f"Trying model: {model}")
                self.llm = genai.GenerativeModel(model)
                model_name = model
                print(f"✅ Successfully loaded model: {model}")
                break
            except Exception as e:
                print(f"❌ Failed to load {model}: {e}")
                continue
        
        if model_name is None:
            # Try the first available model from the list
            if available_models:
                model_name = available_models[0]
                print(f"Using first available model: {model_name}")
                self.llm = genai.GenerativeModel(model_name)
            else:
                raise Exception("No compatible models found. Please check your API key.")
        
        # Prepare FAQ database
        self.faq_data = college_faq
        
        print(f"RAG system ready with model: {model_name}!")
    
    def simple_keyword_match(self, user_query, top_k=3):
        """Simple but effective keyword matching"""
        user_query_lower = user_query.lower()
        
        # Remove punctuation
        user_query_clean = re.sub(r'[^\w\s]', '', user_query_lower)
        user_words = set(user_query_clean.split())
        
        # Score each FAQ based on keyword overlap
        scores = []
        for category, data in self.faq_data.items():
            keywords = data.get('keywords', [])
            response = data.get('response', '')
            
            # Count matching keywords
            keyword_matches = sum(1 for kw in keywords if kw in user_query_lower)
            
            # Count word overlap in response
            response_words = set(response.lower().split())
            word_overlap = len(user_words.intersection(response_words))
            
            total_score = (keyword_matches * 3) + word_overlap
            
            scores.append({
                'category': category,
                'score': total_score,
                'response': response
            })
        
        # Sort by score and get top matches
        scores.sort(key=lambda x: x['score'], reverse=True)
        top_matches = scores[:top_k]
        
        # Build context from top matches
        context = ""
        for match in top_matches:
            if match['score'] > 0:
                context += f"- {match['response']}\n\n"
        
        return context
    
    def generate_response(self, user_query):
        """Generate response using RAG pipeline"""
        
        # Step 1: Retrieve relevant context
        context = self.simple_keyword_match(user_query, top_k=3)
        
        # Step 2: Build prompt for LLM
        if context.strip():
            prompt = f"""You are a helpful and friendly college admissions chatbot assistant. 
Your job is to answer student questions about the college using ONLY the information provided below.

IMPORTANT GUIDELINES:
- Answer in a natural, conversational, and friendly tone
- Use the information from the context to provide accurate answers
- If the question is not covered in the context, politely say "I don't have that specific information. Please contact our admissions office at 1800-XXX-1234 or email admissions@college.edu"
- Keep responses concise (2-4 sentences) unless more detail is needed
- Be helpful and encouraging to prospective students

COLLEGE INFORMATION:
{context}

STUDENT QUESTION: {user_query}

YOUR RESPONSE:"""
        else:
            prompt = f"""You are a college admissions chatbot. A student asked: "{user_query}"

You don't have specific information about this in your database. Politely tell them to contact the admissions office at 1800-XXX-1234 or email admissions@college.edu for this information. Be friendly and apologetic."""
        
        # Step 3: Generate response using Gemini
        try:
            response = self.llm.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"I apologize, but I'm having trouble generating a response right now. Please try again or contact our admissions office directly. Error: {str(e)}"
    
    def chat(self, user_message):
        """Main chat interface"""
        return self.generate_response(user_message)
