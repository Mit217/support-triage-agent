import re

from retriever import load_docs, build_or_load_index, retrieve
from ticket_loader import load_tickets
from risk import assess_risk
import pandas as pd

print("Loading docs...")
docs = load_docs()
print(f"Loaded {len(docs)} docs")

print("Building/loading index...")
index, embeddings = build_or_load_index(docs)
print("Index ready")

def classify_request_type(query, risk_level):
    """Classify the request type based on content and risk"""
    query_lower = query.lower()

    # Check for bugs/issues
    if any(word in query_lower for word in ['not working', 'broken', 'error', 'bug', 'issue', 'problem', 'down', 'fail']):
        return 'bug'

    # Check for feature requests
    if any(word in query_lower for word in ['add', 'feature', 'suggest', 'would like', 'can you', 'please add']):
        return 'feature_request'

    # Check for invalid/malicious requests
    if risk_level == "high":
        return 'invalid'

    # Default to product issue for legitimate support requests
    return 'product_issue'


import re

def clean_response(text):

    # Remove image markdown
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)

    # Remove markdown links completely
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Remove raw URLs
    text = re.sub(r'http\S+', '', text)

    # Remove markdown symbols
    text = re.sub(r'[#>*`_~-]', '', text)

    # Remove repeated whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove incomplete markdown/image remnants
    text = re.sub(r'!\[.*?', '', text)
    text = re.sub(r'\[.*?', '', text)
    text = re.sub(r'\S*image\.png\S*', '', text)
    text = re.sub(r'\S*KeyPairId\S*', '', text)

    return text.strip()


def process_ticket(ticket, docs):
    """Process a single ticket and return the 5 required output columns"""
    issue = str(ticket.get('Issue', '') or '')
    subject = str(ticket.get('Subject', '') or '')
    company = str(ticket.get('Company', '') or '').strip()
    company_key = company.lower()
    query = f"{subject} {issue}".strip()

    # Retrieve relevant documentation from the global index
    retrieved = retrieve(query, docs, index, k=3)
    filtered_results = retrieved
    if company_key and company_key != 'none':
        filtered_results = [
            r for r in retrieved
            if company_key in r["path"].lower()
        ]
        if not filtered_results:
            filtered_results = retrieved

    top_result = filtered_results[0]["content"] if filtered_results else "No relevant documentation found."
    top_result = clean_response(top_result[:200])
    # Assess risk level
    risk = assess_risk(query)

    # Classify request type
    request_type = classify_request_type(query, risk)

    # Determine product area based on company and content
    product_area_map = {
        'HackerRank': 'hackerrank_support',
        'Claude': 'claude_support',
        'Visa': 'visa_support'
    }

    # Try to infer more specific product areas from content
    query_lower = query.lower()
    if 'billing' in query_lower or 'payment' in query_lower or 'charge' in query_lower:
        product_area = 'billing'
    elif 'account' in query_lower or 'login' in query_lower or 'access' in query_lower:
        product_area = 'account_management'
    elif 'test' in query_lower or 'assessment' in query_lower or 'interview' in query_lower:
        product_area = 'screen'
    elif 'card' in query_lower or 'transaction' in query_lower:
        product_area = 'general_support'  # Visa-specific
    else:
        product_area = product_area_map.get(company, 'general_support')

    if risk == "high":
        status = "escalated"
        response = "This request requires review by a human support specialist due to security or policy concerns."
        justification =  "Ticket contains sensitive or high-risk content requiring human review."
    else:
        status = "replied"
        top_result = clean_response(top_result)   
        response = f"Based on our support documentation: {top_result}"
        justification = f"Retrieved relevant {product_area} information from support corpus for query: {query[:100]}..."
    
    if len(top_result.strip()) < 30:
        status = "escalated"
        response = "This request requires review by a human support specialist due to security or policy concerns."
        justification =  "Ticket contains sensitive or high-risk content requiring human review."
    
    return {
        'status': status,
        'product_area': product_area,
        'response': response,
        'justification': justification,
        'request_type': request_type
    }

def main():
    # Load input tickets
    tickets_df = load_tickets()

    # Process each ticket
    results = []
    for _, ticket in tickets_df.iterrows():
        result = process_ticket(ticket, docs)
        results.append(result)

    # Create output DataFrame with only the 5 required columns
    output_df = pd.DataFrame(results)

    # Save to output.csv (only the 5 columns, no input columns)
    output_df.to_csv('support_tickets/output.csv', index=False)

    print(f"Processed {len(results)} tickets")
    print("Output saved to support_tickets/output.csv")
    print(f"Columns: {list(output_df.columns)}")
    print(tickets_df.columns)
if __name__ == "__main__":
    main()