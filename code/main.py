from retriever import load_docs, build_or_load_index, retrieve
from ticket_loader import load_tickets
import pandas as pd

print("Loading docs...")
docs = load_docs()
print(f"Loaded {len(docs)} docs")

print("Building/loading index...")
index, embeddings = build_or_load_index(docs)
print("Index ready")

def process_ticket(ticket, docs, index):
    """Process a single ticket and return the 5 required output columns"""
    issue = ticket.get('Issue', '')
    subject = ticket.get('Subject', '')
    company = ticket.get('Company', '')
    query = f"{ticket.get('Subject', '')} {ticket.get('Issue', '')}"
    retrieved = retrieve(query, docs, index)
    top_result = retrieved[0]["content"][:300]
    print("\n====================")
    print("QUERY:", query)
    print("\nTOP RESULT:")
    print(top_result)
    # TODO: Implement actual agent logic here
    # For now, return placeholder values
    return {
        'status': 'escalated',  # replied or escalated
        'product_area': 'general_support',  # support category
        'response': top_result,  # user-facing answer
        'justification': 'Automated triage determined this requires human assistance.',  # why this decision
        'request_type': 'invalid'  # product_issue, feature_request, bug, invalid
    }

def main():
    # Load input tickets
    tickets_df = load_tickets()

    # Process each ticket
    results = []
    for _, ticket in tickets_df.iterrows():
        result = process_ticket(ticket, docs, index)
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